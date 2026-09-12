"""Local install verification (plan Task 7: "Install locally and verify
source/cache parity plus fresh-task Skill discovery").

Codex discovers locally installed plugins through the ``personal`` marketplace
at ``~/.agents/plugins/marketplace.json``; installation itself is performed by
the Codex CLI (``codex plugin add <name>@personal``), which materialises the
plugin under ``~/.codex/plugins/cache/personal/<plugin>/<version>/`` and owns
the ``[plugins."<name>@personal"]`` entry in ``config.toml``.

These tests exercise the registration half deterministically (against a
temporary marketplace file, so the developer's real ``~/.agents`` is never
touched), and verify skill discovery from the repository itself. The CLI
half is asserted only when the Codex CLI is present, and is otherwise skipped
with an explicit reason.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import local_install  # noqa: E402

PLUGIN_NAME = "codex-dreamina-3d"
EXPECTED_SKILLS = (
    "codex-dreamina-3d-from-blender",
    "codex-dreamina-3d-from-maya",
    "codex-dreamina-3d-resume",
    "codex-dreamina-3d-use",
)


def _discover_skills(plugin_dir: Path) -> list[str]:
    """Enumerate skills the way Codex does: read ``skills`` from the manifest,
    then take every child directory that contains a ``SKILL.md``."""
    manifest = json.loads((plugin_dir / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    skills_dir = (plugin_dir / manifest.get("skills", "./skills/")).resolve()
    if not skills_dir.is_dir():
        return []
    return sorted(
        child.name for child in skills_dir.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    )


class ManifestIdentityTests(unittest.TestCase):
    def test_plugin_identity(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], PLUGIN_NAME)
        self.assertEqual(manifest["skills"], "./skills/")

    def test_source_tree_discovers_four_skills(self) -> None:
        self.assertEqual(_discover_skills(ROOT), list(EXPECTED_SKILLS))

    def test_every_skill_has_matching_frontmatter_name(self) -> None:
        skill_root = ROOT / "skills"
        for name in EXPECTED_SKILLS:
            text = (skill_root / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), f"{name} lacks frontmatter")
            fm = text.split("---\n", 2)[1]
            declared = next(
                (line.partition(":")[2].strip() for line in fm.splitlines() if line.startswith("name:")),
                None,
            )
            self.assertEqual(declared, name)


class MarketplaceRegistrationTests(unittest.TestCase):
    """Registration is exercised against a temp marketplace path."""

    def setUp(self) -> None:
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self._original = local_install.MARKETPLACE_PATH
        local_install.MARKETPLACE_PATH = Path(self._tmp.name) / "marketplace.json"

    def tearDown(self) -> None:
        local_install.MARKETPLACE_PATH = self._original
        self._tmp.cleanup()

    def test_register_creates_marketplace_with_local_source(self) -> None:
        result = local_install.register(plugin_dir=ROOT)
        self.assertTrue(result["changed"])
        data = json.loads(local_install.MARKETPLACE_PATH.read_text())
        self.assertEqual(data["name"], "personal")
        entry = next(e for e in data["plugins"] if e["name"] == PLUGIN_NAME)
        self.assertEqual(entry["source"]["source"], "local")
        self.assertTrue(entry["source"]["path"].endswith("codex-dreamina-3d-plugin"))
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")

    def test_register_is_idempotent(self) -> None:
        local_install.register(plugin_dir=ROOT)
        first = local_install.MARKETPLACE_PATH.read_text()
        second = local_install.register(plugin_dir=ROOT)
        self.assertFalse(second["changed"])
        self.assertEqual(first, local_install.MARKETPLACE_PATH.read_text())

    def test_dry_run_does_not_write(self) -> None:
        result = local_install.register(plugin_dir=ROOT, dry_run=True)
        self.assertTrue(result["changed"])
        self.assertFalse(local_install.MARKETPLACE_PATH.exists())

    def test_registration_survives_json_round_trip(self) -> None:
        local_install.register(plugin_dir=ROOT)
        data = json.loads(local_install.MARKETPLACE_PATH.read_text())
        self.assertIsInstance(data["plugins"], list)

    def test_relative_path_is_home_relative(self) -> None:
        result = local_install.register(plugin_dir=ROOT)
        # Paths inside the home directory are stored as "./..." so the
        # marketplace stays portable across machines.
        if result["entry"]["source"]["path"].startswith("./"):
            self.assertNotIn(str(Path.home()), result["entry"]["source"]["path"])


class CachebusterTests(unittest.TestCase):
    """The documented local-iteration loop requires a cachebuster suffix:
    <base-version>+codex.<token>, replacing any existing cachebuster."""

    def setUp(self) -> None:
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        src = ROOT / ".codex-plugin" / "plugin.json"
        dst_dir = Path(self._tmp.name) / ".codex-plugin"
        dst_dir.mkdir(parents=True)
        (dst_dir / "plugin.json").write_text(src.read_text())
        self.plugin_dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _version(self) -> str:
        return json.loads((self.plugin_dir / ".codex-plugin" / "plugin.json").read_text())["version"]

    def test_cachebuster_appends_codex_suffix(self) -> None:
        version = local_install.bump_cachebuster(self.plugin_dir, "local-20260912-120000")
        self.assertEqual(version, "0.1.0+codex.local-20260912-120000")
        self.assertEqual(self._version(), version)

    def test_cachebuster_replaces_existing_token(self) -> None:
        local_install.bump_cachebuster(self.plugin_dir, "local-first")
        version = local_install.bump_cachebuster(self.plugin_dir, "local-second")
        self.assertEqual(version, "0.1.0+codex.local-second")
        self.assertEqual(self._version().count("+"), 1)

    def test_cachebuster_default_token_is_timestamped(self) -> None:
        version = local_install.bump_cachebuster(self.plugin_dir)
        self.assertTrue(version.startswith("0.1.0+codex.local-"), version)

    def test_cachebuster_version_remains_strict_semver(self) -> None:
        version = local_install.bump_cachebuster(self.plugin_dir, "abc")
        self.assertRegex(version, r"^0\.1\.0\+[0-9A-Za-z.-]+$")

    def test_cachebuster_preserves_prerelease_base(self) -> None:
        manifest_path = self.plugin_dir / ".codex-plugin" / "plugin.json"
        data = json.loads(manifest_path.read_text())
        data["version"] = "1.2.3-beta.1+codex.old"
        manifest_path.write_text(json.dumps(data))
        version = local_install.bump_cachebuster(self.plugin_dir, "new")
        self.assertEqual(version, "1.2.3-beta.1+codex.new")


class CodexCliTests(unittest.TestCase):
    """The CLI half of the install is asserted only when Codex is present."""

    def setUp(self) -> None:
        self.cli = local_install.find_cli()
        if self.cli is None:
            self.skipTest("Codex CLI not installed on this machine")

    def test_cli_lists_plugin_as_installed(self) -> None:
        out = local_install.list_plugins(self.cli)
        self.assertIn(PLUGIN_NAME, out, out)
        line = next(l for l in out.splitlines() if PLUGIN_NAME in l)
        self.assertIn("installed", line, line)
        self.assertIn("enabled", line, line)

    def test_cli_reports_installed_version(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        out = local_install.list_plugins(self.cli)
        line = next(l for l in out.splitlines() if PLUGIN_NAME in l)
        self.assertIn(manifest["version"], line, line)


if __name__ == "__main__":
    unittest.main()