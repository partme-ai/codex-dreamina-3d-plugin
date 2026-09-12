"""TRACE evaluation gate (plan Task 5 / Task 7: "Run TRACE").

Runs the deterministic TRACE scorer from the ``skill-trace-evaluation`` skill
against all four Dreamina 3D Skills and asserts each produces a complete
five-dimension score set (T/R/A/C/E) with no missing sub-items.

The evaluator lives outside this repository, so the tests skip with an explicit
reason when it is not installed rather than reporting a false pass.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE_SCRIPT = Path(
    "/Users/wandl/.agents/skills/skill-trace-evaluation/scripts/trace_evaluate.py"
)
SKILLS = (
    "codex-dreamina-3d-use",
    "codex-dreamina-3d-from-blender",
    "codex-dreamina-3d-from-maya",
    "codex-dreamina-3d-resume",
)
DIMENSIONS = ("T", "R", "A", "C", "E")
SUB_ITEMS_PER_DIMENSION = 4


def _evaluate(skill: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(TRACE_SCRIPT), "--skill-dir", str(ROOT / "skills" / skill), "--format", "json"],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0:
        raise AssertionError(f"TRACE scorer failed for {skill}:\n{proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout)


@unittest.skipUnless(TRACE_SCRIPT.is_file(), f"TRACE evaluator not installed at {TRACE_SCRIPT}")
class TraceEvaluationTests(unittest.TestCase):
    def test_all_four_skills_evaluate(self) -> None:
        for skill in SKILLS:
            with self.subTest(skill=skill):
                report = _evaluate(skill)
                self.assertEqual(report["skill_name"], skill)

    def test_each_skill_has_all_five_dimensions(self) -> None:
        for skill in SKILLS:
            with self.subTest(skill=skill):
                base = _evaluate(skill)["base_scores"]
                for dim in DIMENSIONS:
                    self.assertIn(dim, base, f"{skill} missing dimension {dim}")
                    self.assertIn("avg", base[dim])
                    self.assertIsInstance(base[dim]["avg"], float)

    def test_each_dimension_has_four_sub_items(self) -> None:
        for skill in SKILLS:
            with self.subTest(skill=skill):
                base = _evaluate(skill)["base_scores"]
                for dim in DIMENSIONS:
                    sub = base[dim]["sub_items"]
                    self.assertEqual(
                        len(sub), SUB_ITEMS_PER_DIMENSION,
                        f"{skill}/{dim} has {len(sub)} sub-items, expected {SUB_ITEMS_PER_DIMENSION}",
                    )

    def test_overall_score_is_within_bounds(self) -> None:
        for skill in SKILLS:
            with self.subTest(skill=skill):
                base = _evaluate(skill)["base_scores"]
                self.assertGreaterEqual(base["overall"], 1.0)
                self.assertLessEqual(base["overall"], 5.0)

    def test_skills_clear_the_good_tier_floor(self) -> None:
        """The plugin's Skills must at least reach the 'Good' band (>= 3.5)."""
        for skill in SKILLS:
            with self.subTest(skill=skill):
                overall = _evaluate(skill)["base_scores"]["overall"]
                self.assertGreaterEqual(overall, 3.5, f"{skill} overall {overall} below Good tier")

    def test_trace_evidence_document_records_scores(self) -> None:
        doc = (ROOT / "docs" / "verification" / "trace.md").read_text(encoding="utf-8")
        for skill in SKILLS:
            self.assertIn(skill, doc, f"trace.md does not record {skill}")
        self.assertIn("skill_trace = 4/4", doc)


if __name__ == "__main__":
    unittest.main()