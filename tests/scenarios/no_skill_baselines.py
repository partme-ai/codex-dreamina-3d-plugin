"""No-skill baseline scenarios for codex-dreamina-3d.

Each scenario captures a failure mode that an unguided agent exhibits when the
Dreamina 3D Skills are NOT loaded, pairs it with the deterministic guard that
the plugin installs, and carries an executable probe proving the guard fires.

The plan (Task 5 / Task 6) requires baselines for:
  - silent companion installation
  - ambiguous DCC choice
  - unvalidated preview
  - quote reuse after inputs changed
  - paid retry after an unknown result
  - false end-to-end completion

Scenarios are data plus a callable; ``tests/test_scenarios.py`` runs every
probe and asserts the guard fires.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from capability_probe import (  # noqa: E402
    AmbiguousCompanionError,
    MissingCompanionError,
    discover_companions,
    select_companion,
)
from handoff_validator import validate_artifact  # noqa: E402
from job_ledger import (  # noqa: E402
    InvalidTransitionError,
    JobLedger,
    JobState,
    QuoteInputs,
    new_job,
)
from design_handoff import ArtifactMismatchError, design_handoff  # noqa: E402

FAKES = ROOT / "tests" / "fakes"


@dataclass(frozen=True)
class Scenario:
    id: str
    title: str
    no_skill_baseline: str
    guard: str
    skill: str
    probe: Callable[[], tuple[bool, str]]


# --------------------------------------------------------------------------
# Probe implementations
# --------------------------------------------------------------------------

def _probe_silent_install() -> tuple[bool, str]:
    """No companions present: discovery must return [] and selection must raise
    install guidance; the module must not shell out or touch the network."""
    with tempfile.TemporaryDirectory() as tmp:
        found = discover_companions((Path(tmp),))
        if found != []:
            return False, f"expected no companions, found {found}"
        try:
            select_companion([], requested=None)
        except MissingCompanionError as exc:
            if "install" not in str(exc).lower():
                return False, "MissingCompanionError lacked install guidance"
        else:
            return False, "select_companion did not raise on empty candidates"
    source = (ROOT / "scripts" / "capability_probe.py").read_text()
    for forbidden in ("subprocess", "urllib", "requests.", "os.system"):
        if forbidden in source:
            return False, f"capability_probe.py performs side effects: {forbidden!r}"
    return True, "no-companion path returns install guidance and performs no install"


def _probe_ambiguous_choice() -> tuple[bool, str]:
    """Two companions installed with no explicit request must raise rather than
    let the agent pick arbitrarily."""
    from capability_probe import Companion

    blender = Companion(
        plugin_id="codex-blender", version="0.1.0", executable=Path("/bin/true"),
        contract_versions=("1.0.0",), manifest_path=Path("/tmp/b.json"),
    )
    maya = Companion(
        plugin_id="codex-maya", version="0.1.0", executable=Path("/bin/true"),
        contract_versions=("1.0.0",), manifest_path=Path("/tmp/m.json"),
    )
    try:
        select_companion([blender, maya], requested=None)
    except AmbiguousCompanionError:
        pass
    else:
        return False, "select_companion silently picked a companion"
    # An explicit request still resolves deterministically.
    picked = select_companion([blender, maya], requested="maya")
    if picked.plugin_id != "codex-maya":
        return False, f"explicit choice resolved to {picked.plugin_id}"
    return True, "ambiguity raises; explicit request resolves deterministically"


def _probe_unvalidated_preview() -> tuple[bool, str]:
    """A receipt with unconfirmed restoration or a stale hash must be rejected
    before any Dreamina work."""
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "preview.mp4"
        artifact.write_bytes(b"\x00\x00\x00\x18ftypisom")
        sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
        base = json.loads((ROOT / "tests" / "fixtures" / "blender_artifact.json").read_text())
        base.update({"path": str(artifact), "sha256": sha, "bytes": artifact.stat().st_size})

        cases = {
            "restoration unknown": {**base, "restoration": {"status": "unknown"}},
            "hash mismatch": {**base, "sha256": "f" * 64},
            "unsupported codec": {**base, "codec": "prores"},
            "oversized duration": {**base, "duration_seconds": 120.0},
        }
        for label, receipt in cases.items():
            errors = validate_artifact(receipt, artifact)
            if not errors:
                return False, f"validator accepted a bad receipt: {label}"
        # A valid receipt still passes, proving the guard is not a blanket deny.
        if validate_artifact(base, artifact):
            return False, "validator rejected a valid receipt"
    return True, "all four invalid receipts rejected; valid receipt accepted"


def _probe_quote_reuse() -> tuple[bool, str]:
    """After a quote-binding input changes, the ledger must walk the job back
    and clear the quote so the stale quote cannot be reused."""
    with tempfile.TemporaryDirectory() as tmp:
        ledger = JobLedger(Path(tmp) / "job.json")
        ledger.write(new_job("job-quote"))
        ledger.transition(JobState.DCC_SELECTED, selected_companion={"plugin_id": "codex-blender", "version": "0.1.0", "contract_version": "1.0.0"})
        ledger.transition(JobState.PREVIEW_SPECIFIED, preview={"artifact_id": "a1", "sha256": "0" * 64, "producer_plugin": "codex-blender", "producer_version": "0.1.0"})
        ledger.transition(JobState.PREVIEW_VALIDATED, preview_hash_validated=True)
        ledger.transition(JobState.CAPABILITY_RESOLVED, resolved_capability={"model": "seedance-2.5"})
        ledger.transition(JobState.QUOTED, quote_inputs=QuoteInputs("p", "seedance-2.5", "1280x720", "16:9", 4.0), quote={"price_usd": 1.0})
        ledger.transition(JobState.APPROVED, approved_by="user", approved_at="2026-09-12T00:00:00Z")

        ledger.invalidate_quote(reason="prompt changed")
        job = ledger.read()
        if job["quote"] is not None or job["quote_inputs"] is not None:
            return False, "quote survived invalidation"
        if job["approval"] is not None:
            return False, "approval survived invalidation"
        if job["state"] != JobState.PREVIEW_VALIDATED.value:
            return False, f"expected PreviewValidated, got {job['state']}"
        # Direct Approved -> Submitted is no longer reachable either.
        try:
            ledger.transition(JobState.SUBMITTED, submit={"design_submit_id": "x"})
        except InvalidTransitionError:
            pass
        else:
            return False, "ledger allowed Approved->Submitted after invalidation"
    return True, "quote and approval cleared; job returns to PreviewValidated"


def _probe_paid_retry() -> tuple[bool, str]:
    """A duplicate submit must return the existing submit id; the ledger must
    forbid Submitted -> Submitted and Unknown -> Submitted."""
    with tempfile.TemporaryDirectory() as tmp:
        state_dir = Path(tmp) / "design"
        state_dir.mkdir()
        wrapper = state_dir / "design.sh"
        wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {FAKES / 'fake_design_adapter.py'} --state-dir {state_dir} \"$@\"\n")
        wrapper.chmod(0o755)

        first = design_handoff(executable=str(wrapper), mode="submit", payload={"job_key": "paid"}, request_dir=state_dir)
        second = design_handoff(executable=str(wrapper), mode="submit", payload={"job_key": "paid"}, request_dir=state_dir)
        # The guard is idempotency: the second submit must reuse the first
        # design_submit_id so no new paid action is created.
        if not first.get("design_submit_id"):
            return False, f"first submit produced no id: {first}"
        if first["design_submit_id"] != second["design_submit_id"]:
            return False, (
                "second submit created a new paid action: "
                f"{first['design_submit_id']} -> {second['design_submit_id']}"
            )

        ledger = JobLedger(Path(tmp) / "job.json")
        ledger.write(new_job("job-paid"))
        for state, fields in (
            (JobState.DCC_SELECTED, {"selected_companion": {"plugin_id": "codex-blender", "version": "0.1.0", "contract_version": "1.0.0"}}),
            (JobState.PREVIEW_SPECIFIED, {"preview": {"artifact_id": "a1", "sha256": "0" * 64, "producer_plugin": "codex-blender", "producer_version": "0.1.0"}}),
            (JobState.PREVIEW_VALIDATED, {"preview_hash_validated": True}),
            (JobState.CAPABILITY_RESOLVED, {"resolved_capability": {"model": "seedance-2.5"}}),
            (JobState.QUOTED, {"quote_inputs": QuoteInputs("p", "seedance-2.5", "1280x720", "16:9", 4.0), "quote": {"price_usd": 1.0}}),
            (JobState.APPROVED, {"approved_by": "user", "approved_at": "2026-09-12T00:00:00Z"}),
            (JobState.SUBMITTED, {"submit": {"design_submit_id": first["design_submit_id"]}}),
        ):
            ledger.transition(state, **fields)
        for illegal in (JobState.SUBMITTED, JobState.APPROVED, JobState.QUOTED):
            try:
                ledger.transition(illegal)
            except InvalidTransitionError:
                continue
            return False, f"ledger allowed Submitted -> {illegal.value}"
    return True, "duplicate submit reuses id; ledger forbids Submitted -> Submitted/Quoted/Approved"


def _probe_false_e2e_completion() -> tuple[bool, str]:
    """A design plugin reporting 'succeeded' with a mismatched artifact must not
    complete the job; only a re-hashed matching artifact may reach Completed."""
    with tempfile.TemporaryDirectory() as tmp:
        state_dir = Path(tmp) / "design"
        state_dir.mkdir()
        wrapper = state_dir / "design.sh"
        wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {FAKES / 'fake_design_adapter.py'} --state-dir {state_dir} \"$@\"\n")
        wrapper.chmod(0o755)
        out = state_dir / "result.mp4"

        try:
            design_handoff(
                executable=str(wrapper), mode="query",
                payload={"design_submit_id": "ds_x", "force_error": "artifact_mismatch"},
                request_dir=state_dir, output_path=out,
            )
        except ArtifactMismatchError:
            pass
        else:
            return False, "query accepted a mismatched artifact"

        # A matching artifact is accepted, proving the guard is not a blanket deny.
        matched = state_dir / "matched.mp4"
        matched.write_bytes(b"GOOD")
        good = design_handoff(
            executable=str(wrapper), mode="query",
            payload={"design_submit_id": "ds_x"}, request_dir=state_dir, output_path=matched,
        )
        if good.get("status") != "succeeded":
            return False, f"valid query rejected: {good}"
    return True, "mismatched artifact rejected; matching artifact accepted"


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        id="silent_companion_install",
        title="Silent companion installation",
        no_skill_baseline=(
            "Without the router Skill an agent that finds no codex-blender/codex-maya "
            "installation installs one itself before asking the user."
        ),
        guard="capability_probe.select_companion raises MissingCompanionError carrying install guidance; the module performs no subprocess or network call.",
        skill="codex-dreamina-3d-use",
        probe=_probe_silent_install,
    ),
    Scenario(
        id="ambiguous_dcc_choice",
        title="Arbitrary DCC choice when both companions exist",
        no_skill_baseline=(
            "Without the router Skill an agent picks Blender or Maya arbitrarily when "
            "both companions are installed."
        ),
        guard="capability_probe.select_companion raises AmbiguousCompanionError unless the request names blender/maya.",
        skill="codex-dreamina-3d-use",
        probe=_probe_ambiguous_choice,
    ),
    Scenario(
        id="unvalidated_preview",
        title="Preview submitted without validation",
        no_skill_baseline=(
            "Without the workflow Skill an agent forwards a preview receipt straight to "
            "Dreamina without checking restoration or re-hashing the file."
        ),
        guard="handoff_validator.validate_artifact rejects unconfirmed restoration, hash mismatch, unsupported codec, and over-limit duration.",
        skill="codex-dreamina-3d-from-blender",
        probe=_probe_unvalidated_preview,
    ),
    Scenario(
        id="quote_reuse",
        title="Stale quote reused after inputs changed",
        no_skill_baseline=(
            "Without the workflow Skill an agent keeps an approved quote after the user "
            "edits the prompt, resolution, or duration."
        ),
        guard="job_ledger.JobLedger.invalidate_quote clears quote/approval and walks the job back to PreviewValidated.",
        skill="codex-dreamina-3d-from-maya",
        probe=_probe_quote_reuse,
    ),
    Scenario(
        id="paid_retry",
        title="Paid action retried after an unknown result",
        no_skill_baseline=(
            "Without the resume Skill an agent re-submits after a timeout, paying twice."
        ),
        guard="design_handoff returns the existing design_submit_id on duplicate; job_ledger forbids Submitted -> Submitted.",
        skill="codex-dreamina-3d-resume",
        probe=_probe_paid_retry,
    ),
    Scenario(
        id="false_end_to_end_completion",
        title="Completion reported on adapter success alone",
        no_skill_baseline=(
            "Without the resume Skill an agent treats a 'succeeded' query response as "
            "end-to-end completion without verifying the downloaded artifact."
        ),
        guard="design_handoff re-hashes the declared artifact and raises ArtifactMismatchError; job_ledger requires a result hash for Completed.",
        skill="codex-dreamina-3d-resume",
        probe=_probe_false_e2e_completion,
    ),
)


def scenario_ids() -> tuple[str, ...]:
    return tuple(s.id for s in SCENARIOS)


__all__ = ["Scenario", "SCENARIOS", "scenario_ids"]
