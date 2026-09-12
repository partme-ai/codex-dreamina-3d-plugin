"""Tests for the runtime verification documents under docs/verification/.

These tests pin the existence and required content of the four
Task 8 evidence documents:

  - docs/verification/blender-path.md
  - docs/verification/maya-path.md
  - docs/verification/dreamina-path.md
  - docs/verification/end-to-end.md

In an offline verification environment, the runtime gates are recorded
as ``NOT_RUN``; these tests assert that the documents reflect that and
explain the reason rather than claiming success.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = ROOT / "docs" / "verification"

DOCS = {
    "blender-path": (VERIFICATION / "blender-path.md", "local_blender_runtime"),
    "maya-path": (VERIFICATION / "maya-path.md", "local_maya_runtime"),
    "dreamina-path": (VERIFICATION / "dreamina-path.md", "paid_seedance_canary"),
    "end-to-end": (VERIFICATION / "end-to-end.md", "paid_seedance_canary"),
}


class VerificationDocsTests(unittest.TestCase):
    def test_all_four_verification_docs_exist(self) -> None:
        for name, (path, _) in DOCS.items():
            self.assertTrue(path.is_file(), f"missing verification doc: {name}")

    def test_each_doc_records_its_gate(self) -> None:
        for name, (path, gate) in DOCS.items():
            text = path.read_text(encoding="utf-8")
            self.assertIn(gate, text, f"{name} does not name the gate {gate}")

    def test_runtime_gates_are_marked_not_run(self) -> None:
        # In this offline environment, no real DCC software / paid credentials
        # are available, so the runtime gates must be recorded as NOT_RUN.
        for name, (path, gate) in DOCS.items():
            text = path.read_text(encoding="utf-8")
            # Find the row in the gate-status table for this gate.
            for line in text.splitlines():
                if line.strip().startswith(f"| `{gate}`"):
                    self.assertIn("NOT_RUN", line, f"{name} gate {gate} should be NOT_RUN: {line}")
                    break
            else:
                self.fail(f"{name} has no status row for {gate}")


if __name__ == "__main__":
    unittest.main()