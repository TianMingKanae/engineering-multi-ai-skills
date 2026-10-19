import unittest

from labels import normalize_label


class NormalizeLabelTest(unittest.TestCase):
    def test_simple_label(self):
        self.assertEqual("hello-world", normalize_label("Hello World"))

    def test_trim_and_collapse_whitespace(self):
        self.assertEqual("hello-world", normalize_label("  Hello   World  "))

    def test_tabs_and_newlines(self):
        self.assertEqual("hello-world", normalize_label("Hello\t\nWorld"))

    def test_empty_and_blank(self):
        for value in ("", "  \t\n "):
            with self.subTest(value=value):
                self.assertEqual("", normalize_label(value))


if __name__ == "__main__":
    unittest.main()
