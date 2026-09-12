"""Local install + fresh-task Skill discovery verification (plan Task 7).

The plan requires: "Install locally and verify source/cache parity plus
fresh-task Skill discovery".

These tests exercise the installer against a temporary plugins root (so the
developer's real ``~/.codex`` is never touched by the suite), and separately
prove that a *fresh* process with no prior state can discover the installed
Skills purely from the manifest.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from local_install import (  # noqa: E402
    PLUGIN_DIR,
    discover_skills,
    install,
    read_manifest,
    source_cache_parity,
    validate_skill_frontmatter,
)

EXPECTED_SKILLS = (
    "codex-dreamina-3d-from-blender",
    "codex-dreamina-3d-from-maya",
    "codex-dreamina-3d-resume",
    "codex-dreamina-3d-use",
)


class InstallerTests(unittest.TestCase):
    def test_dry_run_plans_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = install(plugins_root=root, dry_run=True)
            self.assertFalse(result["installed"])
            self.assertEqual(list(root.rglob("*")), [])

    def test_install_creates_expected_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = install(plugins_root=root)
            manifest = read_manifest(PLUGIN_DIR)
            expected = root / "personal" / manifest["name"] / manifest["version"]
            self.assertEqual(Path(result["target"]), expected)
            self.assertTrue((expected / ".codex-plugin" / "plugin.json").is_file())
            self.assertTrue((expected / "skills").is_dir())

    def test_install_does_not_copy_vcs_or_caches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = install(plugins_root=root)
            installed = Path(result["target"])
            self.assertFalse((installed / ".git").exists())
            self.assertEqual(list(installed.rglob("__pycache__")), [])
            self.assertEqual(list(installed.rglob(".DS_Store")), [])

    def test_source_cache_parity_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = install(plugins_root=root)
            self.assertEqual(result["parity_errors"], [])
            # Re-check explicitly against the source tree.
            self.assertEqual(source_cache_parity(PLUGIN_DIR, Path(result["target"])), [])

    def test_install_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = install(plugins_root=root)
            second = install(plugins_root=root)
            self.assertEqual(first["target"], second["target"])
            self.assertEqual(second["parity_errors"], [])


class SkillDiscoveryTests(unittest.TestCase):
    def test_discover_skills_from_source(self) -> None:
        self.assertEqual(list(discover_skills(PLUGIN_DIR)), list(EXPECTED_SKILLS))

    def test_discover_skills_from_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = install(plugins_root=Path(tmp))
            self.assertEqual(list(result["skills"]), list(EXPECTED_SKILLS))

    def test_installed_skill_frontmatter_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = install(plugins_root=Path(tmp))
            self.assertEqual(result["skill_errors"], [])
            self.assertEqual(validate_skill_frontmatter(Path(result["target"])), [])

    def test_fresh_task_discovers_skills_with_no_prior_state(self) -> None:
        """Spawn a pristine interpreter with an empty environment that only
        knows the installed plugins root, and confirm it enumerates the four
        Skills from the manifest alone."""
        with tempfile.TemporaryDirectory() as tmp:
            result = install(plugins_root=Path(tmp))
            installed = Path(result["target"])
            script = (
                "import json, sys\n"
                "from pathlib import Path\n"
                f"sys.path.insert(0, {str(PLUGIN_DIR / 'scripts')!r})\n"
                "from local_install import discover_skills\n"
                f"print(json.dumps(discover_skills(Path({str(installed)!r}))))\n"
            )
            proc = subprocess.run(
                [sys.executable, "-I", "-c", script],
                capture_output=True, text=True, timeout=60,
                env={"PATH": "/usr/bin:/bin"},
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(json.loads(proc.stdout), list(EXPECTED_SKILLS))

    def test_fresh_task_sees_manifest_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = install(plugins_root=Path(tmp))
            installed = Path(result["target"])
            script = (
                "import json\n"
                "from pathlib import Path\n"
                f"m = json.loads((Path({str(installed)!r}) / '.codex-plugin' / 'plugin.json').read_text())\n"
                "print(json.dumps({'name': m['name'], 'version': m['version'], 'skills': m['skills']}))\n"
            )
            proc = subprocess.run(
                [sys.executable, "-I", "-c", script],
                capture_output=True, text=True, timeout=60,
                env={"PATH": "/usr/bin:/bin"},
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["name"], "codex-dreamina-3d")
            self.assertEqual(payload["skills"], "./skills/")


if __name__ == "__main__":
    unittest.main()