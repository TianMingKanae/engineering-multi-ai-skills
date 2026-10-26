from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "skills/technical-writing/scripts/style_check.py"


class WritingStyleTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def scan(self, text, suffix=".md", *options):
        path = self.root / ("draft" + suffix)
        original = text.encode("utf-8") if isinstance(text, str) else text
        path.write_bytes(original)
        result = subprocess.run([sys.executable, str(CHECKER), str(path), *options],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(original, path.read_bytes(), "The style scan must never edit the draft")
        return result

    def test_wordy_phrase_is_advisory_with_original_line_number(self):
        result = self.scan("Records arrived.\nWe act in order to finish.\n", ".txt", "--only", "wordy")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("2: [wordy] in order to", result.stdout)

    def test_categories_filter_without_silently_ignoring_typo(self):
        result = self.scan("The record was processed in order to finish.\n", ".md", "--only", "wordy")
        self.assertIn("[wordy]", result.stdout)
        self.assertNotIn("[passive]", result.stdout)
        bad = self.scan("Records arrived.\n", ".md", "--only", "words")
        self.assertEqual(2, bad.returncode)
        self.assertNotIn("Traceback", bad.stderr)

    def test_plain_text_can_have_no_suggestions(self):
        result = self.scan("Records arrived.\n")
        self.assertEqual(0, result.returncode)
        self.assertEqual("no flags", result.stdout.strip())

    def test_wrapped_long_sentence_reports_its_actual_starting_line(self):
        text = "Introduction.\nMany\nrecords " + "remain " * 36 + "available.\n"
        result = self.scan(text, ".txt", "--only", "long-sentence")
        self.assertEqual(0, result.returncode)
        self.assertIn("2: [long-sentence]", result.stdout)

    def test_math_and_bibliography_do_not_leak_into_acronym_scan(self):
        result = self.scan("\\begin{equation}\nABC = XYZ\n\\end{equation}\n"
                           "Records arrived.\n\\bibliography{refs}\nWe act in order to finish.\n",
                           ".tex", "--only", "acronym,wordy")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("no flags", result.stdout.strip())

    def test_bracket_math_and_commented_delimiters_preserve_prose(self):
        result = self.scan("% \\begin{equation}\nWe act in order to finish.\n"
                           "\\[\nABC = XYZ\n\\]\n",
                           ".tex", "--only", "wordy,acronym")
        self.assertEqual(0, result.returncode)
        self.assertIn("2: [wordy]", result.stdout)
        self.assertNotIn("[acronym]", result.stdout)

    def test_figure_captions_are_prose_and_keep_line_numbers(self):
        result = self.scan("\\begin{figure}\n\\caption{We act in order to finish.}\n\\end{figure}\n",
                           ".tex", "--only", "wordy")
        self.assertEqual(0, result.returncode)
        self.assertIn("2: [wordy] in order to", result.stdout)

    def test_utf8_bom_is_supported_and_invalid_bytes_fail_explicitly(self):
        result = self.scan(b"\xef\xbb\xbfWe act in order to finish.\n", ".txt", "--only", "wordy")
        self.assertEqual(0, result.returncode)
        self.assertIn("1: [wordy]", result.stdout)
        invalid = self.scan(b"\xff\xfe\x00\x00", ".txt")
        self.assertEqual(2, invalid.returncode)
        self.assertNotIn("Traceback", invalid.stderr)

    def test_missing_filter_value_and_missing_file_are_bounded_cli_errors(self):
        result = self.scan("Records arrived.\n", ".txt", "--only")
        self.assertEqual(2, result.returncode)
        missing = subprocess.run([sys.executable, str(CHECKER), str(self.root / "missing.md")],
                                 capture_output=True, text=True)
        self.assertEqual(2, missing.returncode)
        self.assertNotIn("Traceback", missing.stderr)


if __name__ == "__main__":
    unittest.main()
