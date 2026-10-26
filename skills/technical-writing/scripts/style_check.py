"""Flag style fingerprints from Markel (1994) in a .tex / .md / .txt file.

Usage: python style_check.py <file> [--only wordy,passive,...]
Prints "line: [category] match -- hint". Flags only; never edits. Each flag is a
prompt to reread the sentence, not an error (passives in methods are often fine).
"""
import argparse
from bisect import bisect_right
from pathlib import Path
import re
import sys

WORDY = {
    r"\butili[sz](e|es|ed|ing|ation)\b": "use",
    r"\bin order to\b": "to",
    r"\bso as to\b": "to",
    r"\bdue to the fact that\b": "because",
    r"\bbased on the fact that\b": "because",
    r"\bin light of the fact that\b": "because",
    r"\bdespite the fact that\b": "although",
    r"\bat (the present time|this point in time)\b": "now",
    r"\bduring the course of\b": "during",
    r"\bha(ve|s) the (capability|ability) to\b": "can",
    r"\bin the event that\b": "if",
    r"\bprior to\b": "before",
    r"\bsubsequent to\b": "after",
    r"\btake into consideration\b": "consider",
    r"\buntil such time as\b": "until",
    r"\bin regard(s)? to\b|\bwith regard to\b": "about / for",
    r"\ba (large )?(number|majority) of\b": "many / most (or give the number)",
    r"\bit is (often|usually) the case that\b": "often / usually",
    r"\bit is worth (noting|mentioning|pointing out) that\b": "cut",
    r"\bit (can|could) be (seen|observed|noted) (from .{0,30} )?that\b": "Fig. X shows ... / cut",
    r"\bin this paper, we\b": "use once only",
    r"\bplays? an? (important|key|vital|crucial) role\b": "say what it does",
    r"\bmore and more\b": "increasingly",
    r"\bwith the (rapid )?development of\b": "state the trend directly",
}
FANCY = {
    r"\bdemonstrat(e|es|ed|ing)\b": "show",
    r"\bascertain\w*\b": "find out",
    r"\bcommenc\w*\b": "begin",
    r"\binitiat(e|es|ed|ing)\b": "begin / start",
    r"\bterminat(e|es|ed|ing)\b": "end / stop",
    r"\bendeavou?r\w*\b": "try",
    r"\bfinaliz\w*\b": "finish",
    r"\bprocur\w*\b": "get",
    r"\bfacilitat\w*\b": "help / allow",
    r"\bnumerous\b": "many",
    r"\bsubsequently\b": "then / later",
    r"\bnovel\b": "show the novelty instead",
    r"\bsignificant(ly)?\b": "specify practical meaning; statistical significance needs a declared test",
}
REDUNDANT = [
    r"\bend result\b", r"\bany and all\b", r"\beach and every\b", r"\bcompletely (eliminat|remov)\w*",
    r"\bvery unique\b", r"\bfuture plans?\b", r"\bstill remains?\b", r"\bpast history\b",
    r"\bbasic(ally)? fundamental\b", r"\bclose proximity\b", r"\bfinal outcome\b", r"\brepeat(ed)? again\b",
    r"\bcurrently (now|at present)\b", r"\bjointly (together|combined)\b",
]
CONFUSED = {
    r"\bcomprised of\b": "consists of / comprises",
    r"\bless (items|records|samples|trials|files|requests)\b": "fewer",
    r"\bamount of (items|records|samples|trials|files|requests)\b": "number of",
    r"\bdifferent with\b": "different from",
    r"\bresearches\b|\binformations\b|\bequipments\b|\bfeedbacks\b": "uncountable noun",
    r"\bbesides,": "in addition,",
}
CHECKS = {
    "expletive": (re.compile(r"(^|[.!?]\s+)(There (is|are|was|were|exist)|It is)\b"), "start with the real subject"),
    "passive": (re.compile(r"\b(is|are|was|were|be|been|being)\s+(\w+ly\s+)?(\w+ed|\w+en|made|done|set|chosen|found|shown|given|run|built|kept|held|seen)\b", re.I), "who acts? active if the actor matters"),
    "nominal": (re.compile(r"\b(?!(?:function|direction|position|fraction|portion|section|equation|distance|variance|instance|presence|sequence|element|segment|basis|analysis|combination|realization|distribution|definition|location|orientation|configuration)\s)(\w+(tion|ment|sis|ance|ence))\s+of\b", re.I), "a hidden verb? 'optimization of x' -> 'optimize x'"),
    "bare-this": (re.compile(r"(^|[.!?]\s+)(This|These|That|Those|It)\s+(is|are|was|were|shows?|means?|implies|indicates?|leads?|results?|can|will|has|have)\b"), "add the noun: 'This gain ...'"),
    "dash": (re.compile(r"---|\u2014"), "em dash: prefer comma, parentheses or a new sentence"),
    "contraction": (re.compile(r"\b\w+'(t|re|ve|ll|d)\b", re.I), "check whether the destination permits contractions"),
    "colon-after-verb": (re.compile(r"\b(are|is|include|includes|consist of|such as):"), "colon only after a complete clause"),
    "number-unit": (re.compile(r"\b\d+(\.\d+)?(dB|dBm|GHz|MHz|mW|W|m|ms|Hz)\b"), "space between number and unit"),
    "leading-zero": (re.compile(r"(?<![\d.])\.\d"), "write 0.5, not .5"),
}

TEX_DROP = [
    (re.compile(r"(?<!\\)%.*$"), ""),                       # comments
    (re.compile(r"\$[^$]*\$"), " MATH "),                   # inline math
    (re.compile(r"\\(cite|ref|eqref|label|url|includegraphics)\{[^}]*\}"), " REF "),
    (re.compile(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?"), " "),      # commands
]


def clean(line, tex):
    if tex:
        for pat, rep in TEX_DROP:
            line = pat.sub(rep, line)
    return line


def acronym_flags(lines):
    """Acronyms (2+ capitals) used before any '(ACR)' definition, or never defined."""
    defined, out = {}, []
    for i, l in enumerate(lines, 1):
        for m in re.finditer(r"\(([A-Z][A-Za-z]*[A-Z]s?)\)", l):
            defined.setdefault(m.group(1).rstrip("s"), i)
    seen = set()
    skip = {"MATH", "REF", "IEEE", "OK", "GHz", "MHz", "THz", "kHz", "dBm", "dBi", "SI", "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII"}
    for i, l in enumerate(lines, 1):
        for m in re.finditer(r"\b([A-Z]{2,}[A-Za-z]*)\b", l):
            a = m.group(1).rstrip("s")
            if a in skip or a in seen:
                continue
            seen.add(a)
            d = defined.get(a)
            if d is None:
                out.append((i, "acronym", a, "never defined as 'Full Name (" + a + ")'"))
            elif d > i:
                out.append((i, "acronym", a, f"used before its definition on line {d}"))
    return out


def main(argv=None):
    categories = {"wordy", "fancy", "confused", "redundant", "long-line", "long-sentence", "acronym", *CHECKS}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--only", help="Comma-separated categories: " + ", ".join(sorted(categories)))
    args = parser.parse_args(argv)
    only = set(args.only.split(",")) if args.only is not None else None
    if only is not None and (not only or only - categories):
        parser.error("unknown or empty category; see --help")
    tex = args.file.suffix.lower() == ".tex"
    try:
        raw = args.file.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as exc:
        parser.error(str(exc))
    if tex:
        # Strip comments before looking for math/bibliography delimiters.
        raw = [re.sub(r"(?<!\\)%.*$", "", line) for line in raw]
    if tex:  # stop at the bibliography: its keys are not prose
        for k, l in enumerate(raw):
            if re.search(r"\\begin\{thebibliography\}|\\bibliography\{|\\printbibliography\b", l):
                raw = raw[:k]
                break
    # Blank skipped blocks before all checks, including acronyms and long sentences.
    visible = []
    in_math = False
    for line in raw:
        if tex and re.search(r"\\begin\{(?:equation|align|eqnarray|gather|multline|displaymath)\*?\}|\\\[", line):
            in_math = True
        if in_math:
            if re.search(r"\\end\{(?:equation|align|eqnarray|gather|multline|displaymath)\*?\}|\\\]", line):
                in_math = False
            visible.append("")
            continue
        visible.append(clean(line, tex))
    lines = visible
    flags = []
    for i, l in enumerate(lines, 1):
        for group, table in (("wordy", WORDY), ("fancy", FANCY), ("confused", CONFUSED)):
            for pat, hint in table.items():
                for m in re.finditer(pat, l, re.I):
                    flags.append((i, group, m.group(0), hint))
        for pat in REDUNDANT:
            for m in re.finditer(pat, l, re.I):
                flags.append((i, "redundant", m.group(0), "say it once"))
        for name, (rx, hint) in CHECKS.items():
            for m in rx.finditer(l):
                flags.append((i, name, m.group(0).strip(), hint))
        words = len(l.split())
        if words > 40 and not tex:
            flags.append((i, "long-line", f"{words} words", "a sentence this long may need splitting"))
    # long sentences across lines
    text = " ".join(lines)
    starts, offset = [], 0
    for line in lines:
        starts.append(offset)
        offset += len(line) + 1
    cursor = 0
    for s in re.split(r"(?<=[.!?])\s+", text):
        start = text.find(s, cursor)
        cursor = start + len(s)
        n = len(s.split())
        if n > 35:
            first = s[:50]
            ln = bisect_right(starts, start + len(s) - len(s.lstrip()))
            flags.append((ln, "long-sentence", f"{n} words: {first}...", "split, or check it reads aloud"))
    flags += acronym_flags(lines)
    if only:
        flags = [f for f in flags if f[1] in only]
    flags.sort(key=lambda f: (f[0], f[1]))
    counts = {}
    for ln, cat, match, hint in flags:
        counts[cat] = counts.get(cat, 0) + 1
        print(f"{ln}: [{cat}] {match} -- {hint}")
    print("\nsummary: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) if counts else "no flags")
    return 0


if __name__ == "__main__":
    sys.exit(main())
