"""Three-package validation (plan Task 6 / Task 8: "validate all three plugin
packages").

The Dreamina 3D pipeline spans three Codex plugin packages:

  - codex-blender      (DCC preview producer)
  - codex-maya         (DCC preview producer)
  - codex-dreamina-3d  (this orchestrator)

Each ships its own ``scripts/validate_distribution.py``. This test runs all
three against their own repository roots and asserts each reports success.

The sibling packages are separate checkouts. When they are absent (for example
on a CI runner that cloned only this repository) the tests skip with an
explicit reason rather than failing, so the gate is honest about what it
actually exercised.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SIBLINGS = {
    "codex-blender": WORKSPACE / "codex-blender-plugin",
    "codex-maya": WORKSPACE / "codex-maya-plugin",
    "codex-dreamina-3d": ROOT,
}
EXPECTED_IDENTITY = {
    "codex-blender": "codex-blender",
    "codex-maya": "codex-maya",
    "codex-dreamina-3d": "codex-dreamina-3d",
}


def _validator_for(repo: Path) -> Path:
    return repo / "scripts" / "validate_distribution.py"


class ThreePackageValidationTests(unittest.TestCase):
    def _run_validator(self, label: str) -> tuple[int, str]:
        repo = SIBLINGS[label]
        validator = _validator_for(repo)
        proc = subprocess.run(
            [sys.executable, str(validator), str(repo)],
            capture_output=True, text=True, timeout=120, cwd=str(repo),
        )
        return proc.returncode, (proc.stdout + proc.stderr).strip()

    def test_codex_blender_package_validates(self) -> None:
        self._assert_validates("codex-blender")

    def test_codex_maya_package_validates(self) -> None:
        self._assert_validates("codex-maya")

    def test_codex_dreamina_3d_package_validates(self) -> None:
        self._assert_validates("codex-dreamina-3d")

    def _assert_validates(self, label: str) -> None:
        repo = SIBLINGS[label]
        if not _validator_for(repo).is_file():
            self.skipTest(
                f"sibling package {label!r} not present at {repo} "
                "(separate checkout required to exercise this gate)"
            )
        code, output = self._run_validator(label)
        self.assertEqual(code, 0, f"{label} validator failed:\n{output}")
        self.assertIn(EXPECTED_IDENTITY[label], output, f"{label} validator output unexpected:\n{output}")

    def test_all_three_present(self) -> None:
        missing = [label for label, repo in SIBLINGS.items() if not _validator_for(repo).is_file()]
        if missing:
            self.skipTest(f"packages not present in this workspace: {missing}")
        self.assertEqual(sorted(SIBLINGS), ["codex-blender", "codex-dreamina-3d", "codex-maya"])


if __name__ == "__main__":
    unittest.main()