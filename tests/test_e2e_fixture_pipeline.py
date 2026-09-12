"""End-to-end fixture test: Blender preview -> Dreamina 3D -> fake design
plugin -> final artifact.

This is the offline equivalent of the Task 8 runtime gates. It exercises
every transition in the job ledger without touching the network, real
DCC software, or paid credentials.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from job_ledger import (  # noqa: E402
    JobLedger,
    JobState,
    QuoteInputs,
    new_job,
)
from handoff_validator import validate_artifact  # noqa: E402
from dcc_handoff import (  # noqa: E402
    PreviewSpec,
    request_preview_export,
)
from design_handoff import (  # noqa: E402
    design_handoff,
    build_multimodal_request,
)

FAKES = ROOT / "tests" / "fakes"
BLENDER = FAKES / "fake_blender_adapter.py"
DESIGN = FAKES / "fake_design_adapter.py"


def _shim(script: Path, state_dir: Path | None = None) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        wrapper = Path(tmp) / "wrapper.sh"
    wrapper = Path(tempfile.mkdtemp()) / "wrapper.sh"
    if state_dir is None:
        wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {script} \"$@\"\n")
    else:
        wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {script} --state-dir {state_dir} \"$@\"\n")
    wrapper.chmod(0o755)
    return str(wrapper)


class FixturePipelineTests(unittest.TestCase):
    def test_blender_to_design_to_completed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger_path = tmp_path / "job.json"
            preview_dir = tmp_path / "previews"
            state_dir = tmp_path / "design_state"
            state_dir.mkdir()
            final_out = state_dir / "result.mp4"
            final_out.write_bytes(b"FINAL_MEDIA_BYTES")
            final_sha = hashlib.sha256(final_out.read_bytes()).hexdigest()
            # Override the fake design adapter's "succeeded" hash so the
            # artifact-mismatch path passes.
            (state_dir / "fake_success_sha.txt").write_text(final_sha)

            blender_exe = _shim(BLENDER)
            design_exe = _shim(DESIGN, state_dir)

            # 1. Preview export via the fake Blender adapter.
            spec = PreviewSpec(
                scene="/tmp/scene.blend",
                camera_name="Camera.001",
                frame_start=1,
                frame_end=96,
                output_label="preview",
            )
            receipt, _rehashed = request_preview_export(
                executable=blender_exe,
                spec=spec,
                output_dir=preview_dir,
                artifact_id="blender_e2e",
                request_payload={"output_bytes": 4096},
            )
            self.assertEqual(receipt["producer_plugin"], "codex-blender")

            # 2. Drive the job ledger through every transition.
            ledger = JobLedger(ledger_path)
            ledger.write(new_job("job-blender-e2e"))
            ledger.transition(JobState.DCC_SELECTED, selected_companion={"plugin_id": "codex-blender", "version": "0.1.0", "contract_version": "1.0.0"})
            ledger.transition(
                JobState.PREVIEW_SPECIFIED,
                preview={
                    "artifact_id": receipt["artifact_id"],
                    "sha256": receipt["sha256"],
                    "producer_plugin": receipt["producer_plugin"],
                    "producer_version": receipt["producer_version"],
                },
            )
            # 3. Validate the preview independently.
            preview_errors = validate_artifact(receipt, Path(receipt["path"]))
            self.assertEqual(preview_errors, [])
            ledger.transition(JobState.PREVIEW_VALIDATED, preview_hash_validated=True)
            ledger.transition(JobState.CAPABILITY_RESOLVED, resolved_capability={"model": "seedance-2.5"})
            quote = QuoteInputs(
                prompt="render a white model",
                model="seedance-2.5",
                resolution="1280x720",
                ratio="16:9",
                duration_seconds=4.0,
            )
            ledger.transition(JobState.QUOTED, quote_inputs=quote, quote={"price_usd": 1.0})
            ledger.transition(JobState.APPROVED, approved_by="user", approved_at="2026-09-12T00:00:00Z")
            submit = design_handoff(executable=design_exe, mode="submit", payload={"job_key": "j-e2e"}, request_dir=state_dir)
            ledger.transition(
                JobState.SUBMITTED,
                submit={"design_submit_id": submit["design_submit_id"], "submitted_at": "2026-09-12T00:00:01Z", "design_status": "submitted"},
            )
            ledger.transition(JobState.QUERYING)
            ledger.transition(
                JobState.COMPLETED,
                result={"artifact_id": "result_e2e", "sha256": final_sha, "path": str(final_out)},
            )
            self.assertEqual(ledger.read()["state"], JobState.COMPLETED)

            # 4. The multimodal request must never carry DCC scene data.
            req = build_multimodal_request(
                preview_artifact_id=receipt["artifact_id"],
                preview_sha256=receipt["sha256"],
                prompt="render a white model",
                quote_inputs=quote.to_dict(),
            )
            for forbidden in ("scene", ".blend", "codex_blender", "codex_maya"):
                self.assertNotIn(forbidden, json.dumps(req))

    def test_maya_to_design_to_completed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger_path = tmp_path / "job.json"
            preview_dir = tmp_path / "previews"
            state_dir = tmp_path / "design_state"
            state_dir.mkdir()
            final_out = state_dir / "maya_result.mp4"
            final_out.write_bytes(b"MAYA_FINAL_MEDIA_BYTES")
            final_sha = hashlib.sha256(final_out.read_bytes()).hexdigest()
            (state_dir / "fake_success_sha.txt").write_text(final_sha)

            maya_exe = _shim(FAKES / "fake_maya_adapter.py")
            design_exe = _shim(DESIGN, state_dir)

            spec = PreviewSpec(
                scene="/tmp/scene.ma",
                camera_name="perspShape",
                frame_start=1,
                frame_end=90,
                output_label="playblast",
            )
            receipt, _rehashed = request_preview_export(
                executable=maya_exe,
                spec=spec,
                output_dir=preview_dir,
                artifact_id="maya_e2e",
                request_payload={"output_bytes": 8192},
            )
            self.assertEqual(receipt["producer_plugin"], "codex-maya")

            ledger = JobLedger(ledger_path)
            ledger.write(new_job("job-maya-e2e"))
            ledger.transition(JobState.DCC_SELECTED, selected_companion={"plugin_id": "codex-maya", "version": "0.1.0", "contract_version": "1.0.0"})
            ledger.transition(
                JobState.PREVIEW_SPECIFIED,
                preview={
                    "artifact_id": receipt["artifact_id"],
                    "sha256": receipt["sha256"],
                    "producer_plugin": receipt["producer_plugin"],
                    "producer_version": receipt["producer_version"],
                },
            )
            self.assertEqual(validate_artifact(receipt, Path(receipt["path"])), [])
            ledger.transition(JobState.PREVIEW_VALIDATED, preview_hash_validated=True)
            ledger.transition(JobState.CAPABILITY_RESOLVED, resolved_capability={"model": "seedance-2.5"})
            quote = QuoteInputs(
                prompt="render a playblast",
                model="seedance-2.5",
                resolution="1920x1080",
                ratio="16:9",
                duration_seconds=3.0,
            )
            ledger.transition(JobState.QUOTED, quote_inputs=quote, quote={"price_usd": 1.0})
            ledger.transition(JobState.APPROVED, approved_by="user", approved_at="2026-09-12T00:00:00Z")
            submit = design_handoff(executable=design_exe, mode="submit", payload={"job_key": "j-maya-e2e"}, request_dir=state_dir)
            ledger.transition(
                JobState.SUBMITTED,
                submit={"design_submit_id": submit["design_submit_id"], "submitted_at": "2026-09-12T00:00:01Z", "design_status": "submitted"},
            )
            ledger.transition(JobState.QUERYING)
            ledger.transition(
                JobState.COMPLETED,
                result={"artifact_id": "result_maya_e2e", "sha256": final_sha, "path": str(final_out)},
            )
            self.assertEqual(ledger.read()["state"], JobState.COMPLETED)


if __name__ == "__main__":
    unittest.main()