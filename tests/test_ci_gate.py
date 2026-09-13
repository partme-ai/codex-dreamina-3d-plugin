"""Tests for the repository-owned strict CI production gate."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ci_gate


class StrictGateTests(unittest.TestCase):
    def test_required_skip_is_a_failure(self):
        result = unittest.TestResult()
        result.skipped.append((self, "missing companion"))
        with self.assertRaises(ci_gate.StrictGateError):
            ci_gate.assert_test_result(result)

    def test_disposable_install_has_source_parity(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = ci_gate.verify_disposable_install(ROOT, Path(tmp))
        self.assertEqual(receipt["version"], "0.2.0")
        self.assertGreater(receipt["files_verified"], 10)
        self.assertTrue(receipt["parity"])

    def test_missing_companion_validator_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ci_gate.StrictGateError):
                ci_gate.validate_companion("codex-blender", Path(tmp))


if __name__ == "__main__":
    unittest.main()
