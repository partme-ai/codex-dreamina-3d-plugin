"""Tests for the four Agent Skills under skills/.

Each Skill MUST:
  - have YAML frontmatter with name and description;
  - explicitly mention local preview status, Dreamina submission status,
    and final artifact acceptance as distinct states;
  - not instruct silent companion installation or paid retry.

The Skills MUST cover the four flows required by the plan:
  - codex-dreamina-3d-use (router)
  - codex-dreamina-3d-from-blender
  - codex-dreamina-3d-from-maya
  - codex-dreamina-3d-resume
"""

from __future__ import annotations

import re
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

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _load_skill(name: str) -> tuple[dict, str]:
    path = SKILLS / name / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise AssertionError(f"missing YAML frontmatter in {path}")
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    body = text[m.end():]
    return fm, body


class SkillStructureTests(unittest.TestCase):
    def test_all_four_skills_present(self) -> None:
        for name in REQUIRED_SKILLS:
            self.assertTrue((SKILLS / name / "SKILL.md").is_file(), f"missing skill: {name}")

    def test_each_skill_has_name_and_description(self) -> None:
        for name in REQUIRED_SKILLS:
            fm, _ = _load_skill(name)
            self.assertEqual(fm.get("name"), name)
            self.assertTrue(fm.get("description"), f"{name} missing description")

    def test_no_skill_silently_installs_companion(self) -> None:
        for name in REQUIRED_SKILLS:
            _, body = _load_skill(name)
            self.assertNotIn("pip install", body)
            self.assertNotIn("brew install", body)
            self.assertNotIn("apt-get install", body)
            self.assertNotIn("silently install", body)

    def test_no_skill_auto_retries_paid_actions(self) -> None:
        for name in REQUIRED_SKILLS:
            _, body = _load_skill(name)
            # Skills may explicitly PROHIBIT paid retries (e.g. "never
            # auto-resubmit"), but must not contain instructions to perform
            # one.
            self.assertNotIn("please retry the submit", body.lower())
            self.assertNotIn("automatically resubmit", body.lower())
            self.assertNotIn("auto-retry submit", body.lower())

    def test_no_skill_does_not_run_dcc_without_preview_validation(self) -> None:
        for name in REQUIRED_SKILLS[1:]:
            _, body = _load_skill(name)
            # All non-router skills must explicitly mention validating the preview.
            self.assertIn("validate", body.lower())

    def test_skills_distinguish_three_status_categories(self) -> None:
        for name in REQUIRED_SKILLS:
            _, body = _load_skill(name)
            body_lower = body.lower()
            self.assertTrue(
                any(token in body_lower for token in ("local preview", "preview validated", "previewvalidated")),
                f"{name} does not mention local preview status",
            )
            self.assertTrue(
                any(token in body_lower for token in ("submitted", "querying", "design submit")),
                f"{name} does not mention Dreamina submission status",
            )
            self.assertTrue(
                "completed" in body_lower or "artifact" in body_lower,
                f"{name} does not mention final artifact acceptance",
            )


class RouterSkillTests(unittest.TestCase):
    def test_router_mentions_companion_detection(self) -> None:
        _, body = _load_skill("codex-dreamina-3d-use")
        self.assertIn("discover_companions", body)
        self.assertIn("select_companion", body)


class ResumeSkillTests(unittest.TestCase):
    def test_resume_skill_blocks_re_submission_of_completed_jobs(self) -> None:
        _, body = _load_skill("codex-dreamina-3d-resume")
        self.assertIn("Never", body)  # explicit "Never do" section
        self.assertIn("design_submit_id", body)
        # Must forbid re-export of completed work.
        body_lower = body.lower()
        self.assertTrue("re-submit" in body_lower or "resubmit" in body_lower or "re-export" in body_lower)

    def test_resume_skill_maps_every_state(self) -> None:
        _, body = _load_skill("codex-dreamina-3d-resume")
        for state in ("Draft", "DccSelected", "PreviewSpecified", "PreviewValidated",
                      "CapabilityResolved", "Quoted", "Approved",
                      "Submitted", "Querying", "Completed", "Failed", "Unknown"):
            self.assertIn(state, body, f"resume Skill does not map state {state}")


class AutomaticPolicySkillTests(unittest.TestCase):
    def test_blender_skill_describes_one_time_automatic_envelope(self) -> None:
        _, body = _load_skill("codex-dreamina-3d-from-blender")
        self.assertIn("auto_with_budget", body)
        self.assertIn("maximum charge", body)
        self.assertIn("submit once", body)
        self.assertIn("quote exceeds the cap", body)


if __name__ == "__main__":
    unittest.main()
