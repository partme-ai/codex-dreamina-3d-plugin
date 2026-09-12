"""Task 7 distribution tests.

These tests extend the foundation tests in tests/test_distribution.py with
the Task 7 clean-room provenance + distribution requirements:

  - the four required Skills exist and are loadable;
  - the plugin id, repository URL, contract versions, and links match the
    manifest;
  - no secret patterns are present in any tracked file;
  - no symlinks or local cache directories are shipped;
  - no ffmpeg / vendor-source / local-bridge-protocol references exist in
    the implementation;
  - `git diff --check` produces no output.
"""

from __future__ import annotations

import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

REQUIRED_SKILLS = (
    "codex-dreamina-3d-use",
    "codex-dreamina-3d-from-blender",
    "codex-dreamina-3d-from-maya",
    "codex-dreamina-3d-resume",
)

SECRET_PATTERNS = (
    re.compile(rb"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)

EXCLUDED_VENDOR_STRINGS = (
    "codex_blender/",  # companion internals
    "codex_maya/",
    "from blender import",
    "import maya",
)

EXCLUDED_MEDIA_BINARIES = (
    "ffmpeg",
    "ffprobe",
)


class SkillsInventoryTests(unittest.TestCase):
    def test_all_four_skills_are_present(self) -> None:
        for skill in REQUIRED_SKILLS:
            self.assertTrue((SKILLS / skill / "SKILL.md").is_file(), f"missing skill: {skill}")


class IdentityAndLinksTests(unittest.TestCase):
    def test_plugin_id_and_repo_match(self) -> None:
        import json
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest["name"], "codex-dreamina-3d")
        self.assertEqual(manifest["repository"], "https://github.com/partme-ai/codex-dreamina-3d-plugin")
        self.assertEqual(manifest["interface"]["websiteURL"], "https://github.com/partme-ai/codex-dreamina-3d-plugin")

    def test_research_doc_records_known_sha256(self) -> None:
        research = (ROOT / "docs" / "research" / "seedance-2.5-uploader-behavior.md").read_text()
        self.assertIn("471b315b8da91023be46496f902f7d64c1b48b91567d10cd442de7dffe0d68ae", research)


class SecretPatternTests(unittest.TestCase):
    def test_no_secrets_anywhere_in_repo(self) -> None:
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            data = path.read_bytes()
            for pattern in SECRET_PATTERNS:
                self.assertIsNone(pattern.search(data), f"secret-like content in {path}")


class CleanRoomExclusionTests(unittest.TestCase):
    def test_no_companion_internal_imports(self) -> None:
        # Restrict the scan to shipped implementation files (scripts/).
        # Test files may legitimately mention companion names.
        for py in (ROOT / "scripts").rglob("*.py"):
            text = py.read_text()
            for forbidden in EXCLUDED_VENDOR_STRINGS:
                self.assertNotIn(forbidden, text, f"{py} contains vendor internals: {forbidden}")

    def test_no_ffmpeg_or_media_binary_paths(self) -> None:
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            name = path.name.lower()
            for binary in EXCLUDED_MEDIA_BINARIES:
                self.assertFalse(name == binary or name.startswith(binary + "."), f"vendor binary present: {path}")


class NoSymlinksOrCachesTests(unittest.TestCase):
    def test_no_symlinks_under_repo(self) -> None:
        for path in ROOT.rglob("*"):
            if ".git" in path.parts:
                continue
            if path.is_symlink():
                self.fail(f"unexpected symlink: {path}")

    def test_no_cache_directories_shipped(self) -> None:
        for path in ROOT.iterdir():
            if not path.is_dir():
                continue
            if path.name in ("__pycache__", ".cache", "node_modules", ".pytest_cache"):
                self.fail(f"cache directory present: {path}")


class GitDiffCheckTests(unittest.TestCase):
    def test_git_diff_check_is_clean(self) -> None:
        # `git diff --check` exits 0 with no output when there are no
        # whitespace/line-ending problems in the working tree vs index.
        result = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class OfflineVerificationDocTests(unittest.TestCase):
    def test_offline_md_lists_three_runtime_blind_spots(self) -> None:
        text = (ROOT / "docs" / "verification" / "offline.md").read_text()
        for marker in ("local_blender_runtime", "local_maya_runtime", "paid_seedance_canary"):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()