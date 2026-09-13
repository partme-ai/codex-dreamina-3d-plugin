"""Tests for the runtime verification documents under docs/verification/.

These tests pin the existence and required content of the four
Task 8 evidence documents:

  - docs/verification/blender-path.md
  - docs/verification/maya-path.md
  - docs/verification/dreamina-path.md
  - docs/verification/end-to-end.md

The authorized Blender preview and paid Dreamina canary gates are recorded as
``PASS``. Maya remains ``NOT_RUN``; these tests keep proof levels distinct.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = ROOT / "docs" / "verification"

DOCS = {
    "blender-path": (VERIFICATION / "blender-path.md", "local_blender_runtime", "PASS"),
    "maya-path": (VERIFICATION / "maya-path.md", "local_maya_runtime", "NOT_RUN"),
    "dreamina-path": (VERIFICATION / "dreamina-path.md", "paid_seedance_canary", "PASS"),
    "end-to-end": (VERIFICATION / "end-to-end.md", "paid_seedance_canary", "PASS"),
}


class VerificationDocsTests(unittest.TestCase):
    def test_all_four_verification_docs_exist(self) -> None:
        for name, (path, _, _) in DOCS.items():
            self.assertTrue(path.is_file(), f"missing verification doc: {name}")

    def test_each_doc_records_its_gate(self) -> None:
        for name, (path, gate, _) in DOCS.items():
            text = path.read_text(encoding="utf-8")
            self.assertIn(gate, text, f"{name} does not name the gate {gate}")

    def test_runtime_gates_record_the_verified_proof_level(self) -> None:
        for name, (path, gate, expected_status) in DOCS.items():
            text = path.read_text(encoding="utf-8")
            # Find the row in the gate-status table for this gate.
            for line in text.splitlines():
                if line.strip().startswith(f"| `{gate}`"):
                    self.assertIn(
                        expected_status, line,
                        f"{name} gate {gate} should be {expected_status}: {line}",
                    )
                    break
            else:
                self.fail(f"{name} has no status row for {gate}")


if __name__ == "__main__":
    unittest.main()
