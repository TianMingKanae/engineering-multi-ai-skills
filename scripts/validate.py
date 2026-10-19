"""Validate skill metadata, repository links and Python syntax without dependencies."""
import ast
from pathlib import Path
import re
import sys


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = []
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if not skills:
        errors.append("No skills found")
    for path in skills:
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            errors.append(f"Bad frontmatter: {path.relative_to(root)}")
            continue
        name = re.search(r"^name: (.+)$", parts[1], re.MULTILINE)
        description = re.search(r"^description: (.+)$", parts[1], re.MULTILINE)
        if not name or name[1] != path.parent.name or not re.fullmatch(r"[a-z0-9-]{1,63}", name[1]):
            errors.append(f"Bad skill name: {path.parent.name}")
        if not description or len(description[1].strip()) < 20:
            errors.append(f"Missing useful description: {path.parent.name}")
    files = [p for p in root.rglob("*") if p.is_file() and
             not any(part in {".git", ".multi-ai", "__pycache__"} for part in p.relative_to(root).parts)]
    for path in files:
        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                errors.append(str(exc))
        if path.suffix == ".md":
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" in link or link.startswith("#"):
                    continue
                dest = (path.parent / link.split("#")[0]).resolve()
                if not dest.is_relative_to(root) or not dest.exists():
                    errors.append(f"Broken local link in {path.relative_to(root)}: {link}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"PASS: {len(skills)} skills; local Markdown links and Python syntax checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
