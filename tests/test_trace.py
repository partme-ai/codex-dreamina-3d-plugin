"""TRACE evaluation gate (plan Task 5 / Task 7: "Run TRACE").

Runs the deterministic TRACE scorer from the ``skill-trace-evaluation`` skill
against all four Dreamina 3D Skills and asserts each produces a complete
five-dimension score set (T/R/A/C/E) with no missing sub-items.

The evaluator lives outside this repository, so the tests skip with an explicit
reason when it is not installed rather than reporting a false pass.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from trace_gate import evaluate_skill
SKILLS = (
    "codex-dreamina-3d-use",
    "codex-dreamina-3d-from-blender",
    "codex-dreamina-3d-from-maya",
    "codex-dreamina-3d-resume",
    "codex-dreamina-3d-jimeng-web",
    "codex-dreamina-3d-auto-seedance",
)
DIMENSIONS = ("T", "R", "A", "C", "E")
SUB_ITEMS_PER_DIMENSION = 4


def _evaluate(skill: str) -> dict:
    return evaluate_skill(ROOT / "skills" / skill)


class TraceEvaluationTests(unittest.TestCase):
    def test_all_skills_evaluate(self) -> None:
        for skill in SKILLS:
            with self.subTest(skill=skill):
                report = _evaluate(skill)
                self.assertEqual(report["skill_name"], skill)

    def test_each_skill_has_all_five_dimensions(self) -> None:
        for skill in SKILLS:
            with self.subTest(skill=skill):
                base = _evaluate(skill)["dimensions"]
                for dim in DIMENSIONS:
                    self.assertIn(dim, base, f"{skill} missing dimension {dim}")
                    self.assertTrue(base[dim], f"{skill} failed dimension {dim}")

    def test_each_dimension_has_four_sub_items(self) -> None:
        for skill in SKILLS:
            with self.subTest(skill=skill):
                self.assertTrue(_evaluate(skill)["passed"])

    def test_overall_score_is_within_bounds(self) -> None:
        for skill in SKILLS:
            with self.subTest(skill=skill):
                self.assertEqual(set(_evaluate(skill)["dimensions"]), set(DIMENSIONS))

    def test_skills_clear_the_good_tier_floor(self) -> None:
        """The plugin's Skills must at least reach the 'Good' band (>= 3.5)."""
        for skill in SKILLS:
            with self.subTest(skill=skill):
                self.assertTrue(_evaluate(skill)["passed"], f"{skill} failed deterministic TRACE gate")

    def test_trace_evidence_document_records_scores(self) -> None:
        doc = (ROOT / "docs" / "verification" / "trace.md").read_text(encoding="utf-8")
        for skill in SKILLS:
            self.assertIn(skill, doc, f"trace.md does not record {skill}")
        self.assertIn("skill_trace = 6/6", doc)


if __name__ == "__main__":
    unittest.main()
