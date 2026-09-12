"""Runner for the no-skill baseline scenarios in tests/scenarios/.

Every scenario pairs an unguided-agent failure mode with the deterministic
guard the plugin installs. This module runs each probe and asserts the guard
actually fires, so the baseline is executable evidence rather than prose.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.scenarios.no_skill_baselines import SCENARIOS, scenario_ids  # noqa: E402

REQUIRED_SCENARIO_IDS = (
    "silent_companion_install",
    "ambiguous_dcc_choice",
    "unvalidated_preview",
    "quote_reuse",
    "paid_retry",
    "false_end_to_end_completion",
)


class ScenarioInventoryTests(unittest.TestCase):
    def test_all_required_scenarios_present(self) -> None:
        for required in REQUIRED_SCENARIO_IDS:
            self.assertIn(required, scenario_ids(), f"missing scenario: {required}")

    def test_every_scenario_has_baseline_guard_and_skill(self) -> None:
        for scenario in SCENARIOS:
            self.assertTrue(scenario.no_skill_baseline, f"{scenario.id} lacks a baseline description")
            self.assertTrue(scenario.guard, f"{scenario.id} lacks a guard description")
            self.assertTrue((ROOT / "skills" / scenario.skill / "SKILL.md").is_file(),
                            f"{scenario.id} references missing skill {scenario.skill}")

    def test_every_scenario_references_a_real_guard_artifact(self) -> None:
        # Each guard string must name at least one module that exists under
        # scripts/ (e.g. "capability_probe.select_companion raises ...").
        known = {p.stem for p in (ROOT / "scripts").glob("*.py")}
        for scenario in SCENARIOS:
            self.assertTrue(
                any(module in scenario.guard for module in known),
                f"{scenario.id} guard names no known module: {scenario.guard!r}",
            )


class ScenarioGuardTests(unittest.TestCase):
    """Each probe must prove the guard fires (and, where applicable, that a
    valid input still passes so the guard is not a blanket deny)."""

    def test_silent_companion_install_guard_fires(self) -> None:
        self._run("silent_companion_install")

    def test_ambiguous_dcc_choice_guard_fires(self) -> None:
        self._run("ambiguous_dcc_choice")

    def test_unvalidated_preview_guard_fires(self) -> None:
        self._run("unvalidated_preview")

    def test_quote_reuse_guard_fires(self) -> None:
        self._run("quote_reuse")

    def test_paid_retry_guard_fires(self) -> None:
        self._run("paid_retry")

    def test_false_end_to_end_completion_guard_fires(self) -> None:
        self._run("false_end_to_end_completion")

    def _run(self, scenario_id: str) -> None:
        scenario = next(s for s in SCENARIOS if s.id == scenario_id)
        fired, detail = scenario.probe()
        self.assertTrue(fired, f"{scenario_id}: {detail}")


if __name__ == "__main__":
    unittest.main()