"""Validate skill metadata, repository links and Python syntax without dependencies."""
import ast
from pathlib import Path
import re
import sys


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = []
    version_file = root / "VERSION"
    version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else ""
    if not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", version):
        errors.append("VERSION must contain a stable MAJOR.MINOR.PATCH version")
    else:
        changelog_file = root / "CHANGELOG.md"
        changelog = changelog_file.read_text(encoding="utf-8") if changelog_file.exists() else ""
        if not re.search(r"^## \[" + re.escape(version) + r"\](?: - \d{4}-\d{2}-\d{2})?$", changelog, re.MULTILINE):
            errors.append("CHANGELOG.md must have a heading for VERSION")
        readme = (root / "README.md").read_text(encoding="utf-8")
        badge = f"https://img.shields.io/badge/version-{version}-blue.svg"
        release = f"https://github.com/TianMingKanae/engineering-multi-ai-skills/releases/tag/v{version}"
        if badge not in readme or release not in readme:
            errors.append("README version badge/release link must match VERSION")
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
    print(f"PASS: version {version}; {len(skills)} skills; local Markdown links and Python syntax checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
