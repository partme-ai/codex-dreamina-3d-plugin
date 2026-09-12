#!/usr/bin/env python3
"""Install codex-dreamina-3d into a local Codex plugins root.

Mirrors the layout Codex uses for locally installed plugins:

    <plugins-root>/personal/<plugin-name>/<version>/...

The installer copies the plugin tree (excluding VCS, caches, and OS noise),
then verifies:

  1. the installed manifest parses and still declares ``name``/``version``;
  2. every skill directory under ``skills/`` carries a ``SKILL.md`` whose
     frontmatter ``name`` matches the directory name;
  3. source/cache parity — every installed file hashes identically to its
     source counterpart.

Use ``--dry-run`` to report the plan without touching disk.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".cache", "node_modules", "build", "dist"}
EXCLUDED_FILES = {".DS_Store"}
DEFAULT_ROOT = Path("~/.codex/plugins/cache").expanduser()
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _ignore(directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in EXCLUDED_DIRS or name in EXCLUDED_FILES:
            ignored.add(name)
    return ignored


def read_manifest(root: Path) -> dict:
    return json.loads((root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))


def discover_skills(root: Path) -> list[str]:
    """Enumerate skills the way Codex does: read ``skills`` from the manifest,
    then take every child directory that contains a ``SKILL.md``."""
    manifest = read_manifest(root)
    skills_rel = manifest.get("skills", "./skills/")
    skills_dir = (root / skills_rel).resolve()
    if not skills_dir.is_dir():
        return []
    found: list[str] = []
    for child in sorted(skills_dir.iterdir()):
        if child.is_dir() and (child / "SKILL.md").is_file():
            found.append(child.name)
    return found


def validate_skill_frontmatter(root: Path) -> list[str]:
    """Return a list of error strings for any skill whose frontmatter is
    missing or whose ``name`` does not match its directory."""
    errors: list[str] = []
    manifest = read_manifest(root)
    skills_dir = (root / manifest.get("skills", "./skills/")).resolve()
    if not skills_dir.is_dir():
        return [f"skills directory missing: {skills_dir}"]
    for child in sorted(skills_dir.iterdir()):
        if not child.is_dir():
            continue
        skill_md = child / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{child.name}: no SKILL.md")
            continue
        text = skill_md.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(text)
        if not match:
            errors.append(f"{child.name}: missing YAML frontmatter")
            continue
        name_field = None
        for line in match.group(1).splitlines():
            if line.startswith("name:"):
                name_field = line.partition(":")[2].strip()
                break
        if name_field != child.name:
            errors.append(f"{child.name}: frontmatter name {name_field!r} != directory name")
    return errors


def source_cache_parity(source: Path, installed: Path) -> list[str]:
    """Return a list of mismatches between the source tree and the installed tree."""
    mismatches: list[str] = []
    for src in sorted(source.rglob("*")):
        rel = src.relative_to(source)
        if any(part in EXCLUDED_DIRS for part in rel.parts) or src.name in EXCLUDED_FILES:
            continue
        if not src.is_file():
            continue
        dst = installed / rel
        if not dst.is_file():
            mismatches.append(f"missing in install: {rel}")
            continue
        if sha256_of(src) != sha256_of(dst):
            mismatches.append(f"hash mismatch: {rel}")
    return mismatches


def install(
    *,
    source: Path = PLUGIN_DIR,
    plugins_root: Path = DEFAULT_ROOT,
    source_name: str = "personal",
    dry_run: bool = False,
) -> dict:
    manifest = read_manifest(source)
    name = manifest["name"]
    version = manifest["version"]
    target = plugins_root / source_name / name / version

    if dry_run:
        return {"target": str(target), "installed": False, "manifest": manifest}

    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=_ignore)

    skill_errors = validate_skill_frontmatter(target)
    parity_errors = source_cache_parity(source, target)
    return {
        "target": str(target),
        "installed": True,
        "manifest": manifest,
        "skills": discover_skills(target),
        "skill_errors": skill_errors,
        "parity_errors": parity_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="plugins cache root")
    parser.add_argument("--source-name", default="personal", help="cache namespace (personal / local)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = install(plugins_root=Path(args.root).expanduser(), source_name=args.source_name, dry_run=args.dry_run)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result.get("skill_errors") or result.get("parity_errors"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())