"""Locate an exact short quote without inventing page numbers or section headings."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def units(text):
    return len(re.findall(r"[\u3400-\u9fff]|[^\W_\u3400-\u9fff]+(?:['’-][^\W_\u3400-\u9fff]+)*", text))


def read_pages(path):
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(path)
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs require an authorized decrypted local copy")
        return [(page.extract_text() or "", reader.page_labels[i]) for i, page in enumerate(reader.pages)], "pdf-physical-page"
    if path.suffix.lower() == ".txt":
        return [(text, None) for text in path.read_text(encoding="utf-8").split("\f")], "text-page-index"
    raise ValueError("Use PDF or UTF-8 text with explicit form-feed page boundaries")


def locate(path, query):
    if not query.strip() or not 1 <= units(query) <= 40:
        raise ValueError("Quote must contain 1..40 words/CJK characters")
    pages, basis = read_pages(path)
    if not any(text.strip() for text, _ in pages):
        raise ValueError("No extractable text; use reviewed OCR with a preserved page map")
    source_hash = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    results, heading = [], None
    for index, (text, label) in enumerate(pages, 1):
        headings = []
        for match in re.finditer(r"^(?:#{1,6}\s+.+|\d+(?:\.\d+)*[.)]?\s+[A-Z].+|[IVX]+\.\s+[A-Z].+)$", text, re.MULTILINE):
            headings.append((match.start(), match[0].strip()))
        start = 0
        while True:
            position = text.find(query, start)
            if position < 0:
                break
            before = [title for offset, title in headings if offset <= position]
            results.append(dict(page_index=index, page_label=label, page_basis=basis,
                                section=before[-1] if before else heading, quote=query,
                                offset_start=position, offset_end=position + len(query),
                                source_sha256=source_hash, page_text_sha256=hashlib.sha256(text.encode()).hexdigest()))
            start = position + 1
        if headings:
            heading = headings[-1][1]
    if not results:
        raise ValueError("Exact quote not found; do not reconstruct or silently normalize text")
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("--quote", required=True)
    args = p.parse_args()
    try:
        print(json.dumps(locate(args.source, args.quote), indent=2, ensure_ascii=False))
    except (OSError, ValueError, ImportError) as exc:
        p.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
