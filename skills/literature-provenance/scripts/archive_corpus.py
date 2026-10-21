"""Index an already-authorized offline PDF/text corpus with explicit per-file rights."""
import argparse
import hashlib
import json
from pathlib import Path


def index(corpus, policy):
    corpus = Path(corpus).resolve()
    entries = []
    for path in sorted(corpus.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".pdf", ".txt"}:
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(corpus):
            raise ValueError("Corpus entries must be regular files inside the corpus")
        name = path.relative_to(corpus).as_posix()
        rights = policy.get("files", {}).get(name)
        if (not isinstance(rights, dict) or not all(isinstance(rights.get(k), str) and rights[k].strip()
                for k in ("source_id", "version", "access_basis", "redistribution"))
                or not isinstance(rights.get("permitted_nodes"), list) or not rights["permitted_nodes"]
                or not all(isinstance(n, str) and n for n in rights["permitted_nodes"])):
            raise ValueError(f"Explicit source/version/rights/recipients required: {name}")
        raw = path.read_bytes()
        entries.append(dict(file=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), rights=rights))
    if not entries:
        raise ValueError("No PDF/text corpus entries found")
    return dict(schema="offline-corpus-v1", files=entries)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--corpus", type=Path, required=True)
    p.add_argument("--policy", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    try:
        manifest = index(args.corpus, json.loads(args.policy.read_text(encoding="utf-8")))
        with args.out.open("x", encoding="utf-8") as f:
            f.write(json.dumps(manifest, indent=2) + "\n")
        print(f"INDEXED {len(manifest['files'])} authorized local sources")
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        p.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
