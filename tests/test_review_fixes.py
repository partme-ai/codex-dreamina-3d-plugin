"""Regression tests for the independent release-review findings.

Each test pins a defect that the two clean-context reviewers reported over the
release diff, so the same class of regression cannot reappear unnoticed.

Reviewer findings covered here:

  - HIGH   symlinked intermediate directory escaping the approved root
  - HIGH   MCP-returned artifact path never checked against the approved root
  - MEDIUM submit preview path never checked against the approved root
  - MEDIUM a multi-artifact MCP response was silently dropped
  - LOW    QUERYING could transition back to SUBMITTED (re-submission)
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

from design_handoff import ArtifactMismatchError, verify_result_artifact  # noqa: E402
from job_ledger import (  # noqa: E402
    ALLOWED_TRANSITIONS,
    InvalidTransitionError,
    JobLedger,
    JobState,
    new_job,
)
from mcp_design_client import McpDesignClient, McpToolError  # noqa: E402


def _write(path: Path, payload: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


class ArtifactContainmentTests(unittest.TestCase):
    """verify_result_artifact must resolve before trusting a path."""

    def test_artifact_inside_approved_root_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "approved"
            digest = _write(root / "out.mp4", b"REAL_MEDIA")
            result = verify_result_artifact(
                {"path": str(root / "out.mp4"), "sha256": digest},
                approved_roots=[str(root)],
            )
            self.assertEqual(result["sha256"], digest)

    def test_artifact_outside_approved_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approved = Path(tmp) / "approved"
            outside = Path(tmp) / "elsewhere"
            digest = _write(outside / "secret.mp4", b"SECRET")
            with self.assertRaises(ArtifactMismatchError) as ctx:
                verify_result_artifact(
                    {"path": str(outside / "secret.mp4"), "sha256": digest},
                    approved_roots=[str(approved)],
                )
            self.assertIn("outside the approved download roots", str(ctx.exception))

    def test_symlinked_leaf_escaping_approved_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approved = Path(tmp) / "approved"
            approved.mkdir()
            target = Path(tmp) / "outside.mp4"
            digest = _write(target, b"ESCAPED")
            link = approved / "link.mp4"
            os.symlink(target, link)
            with self.assertRaises(ArtifactMismatchError):
                verify_result_artifact(
                    {"path": str(link), "sha256": digest},
                    approved_roots=[str(approved)],
                )

    def test_symlinked_intermediate_directory_is_rejected(self) -> None:
        """The original defect: is_symlink() only inspects the final component,
        so an intermediate symlinked directory let the artifact escape."""
        with tempfile.TemporaryDirectory() as tmp:
            approved = Path(tmp) / "approved"
            approved.mkdir()
            outside = Path(tmp) / "outside"
            digest = _write(outside / "planted.mp4", b"PLANTED")
            os.symlink(outside, approved / "sub")
            escaped = approved / "sub" / "planted.mp4"
            self.assertTrue(escaped.is_file(), "precondition: path resolves to a real file")
            with self.assertRaises(ArtifactMismatchError) as ctx:
                verify_result_artifact(
                    {"path": str(escaped), "sha256": digest},
                    approved_roots=[str(approved)],
                )
            self.assertIn("outside the approved download roots", str(ctx.exception))

    def test_symlinked_temp_root_still_accepts_contained_artifact(self) -> None:
        """Containment is compared on resolved paths, so a root reached through
        a link (e.g. /tmp -> /private/tmp on macOS) must still match."""
        with tempfile.TemporaryDirectory() as tmp:
            real = Path(tmp) / "real_root"
            real.mkdir()
            alias = Path(tmp) / "alias_root"
            os.symlink(real, alias)
            digest = _write(real / "out.mp4", b"CONTAINED")
            result = verify_result_artifact(
                {"path": str(alias / "out.mp4"), "sha256": digest},
                approved_roots=[str(alias)],
            )
            self.assertEqual(result["sha256"], digest)


class ProducerVersionContractTests(unittest.TestCase):
    """The validator must accept the version the published companion actually
    emits, and only that published series."""

    def test_blender_published_version_is_accepted(self) -> None:
        """codex-blender's adapter emits producer_version 0.3.0; a range that
        stops at 0.2.99 rejects every current receipt."""
        from handoff_validator import compatible_producer

        for version in ("0.1.0", "0.2.0", "0.3.0"):
            self.assertTrue(
                compatible_producer("codex-blender", version),
                f"codex-blender {version} must be accepted",
            )

    def test_unpublished_newer_version_is_rejected(self) -> None:
        from handoff_validator import compatible_producer

        self.assertFalse(compatible_producer("codex-blender", "0.4.0"))

    def test_maya_stays_within_its_published_series(self) -> None:
        from handoff_validator import compatible_producer

        self.assertTrue(compatible_producer("codex-maya", "0.1.0"))
        self.assertFalse(compatible_producer("codex-maya", "0.3.0"))

    def test_range_covers_the_companion_manifest_version(self) -> None:
        """Guard against future drift: the sibling plugin's declared version
        must fall inside the range this plugin accepts.

        The companion checkout is located the same way CI and the other
        companion tests locate it, so this never skips in the strict gate.
        """
        companion_root = Path(
            os.environ.get("CODEX_BLENDER_REPO", ROOT.parent / "codex-blender-plugin")
        )
        manifest = companion_root / ".codex-plugin" / "plugin.json"
        self.assertTrue(
            manifest.is_file(),
            f"codex-blender companion manifest not found at {manifest}; "
            "set CODEX_BLENDER_REPO to the companion checkout",
        )
        published = json.loads(manifest.read_text())["version"]
        from handoff_validator import compatible_producer

        self.assertTrue(
            compatible_producer("codex-blender", published),
            f"companion publishes {published} but the validator rejects it",
        )


class PolicyDownloadRootTests(unittest.TestCase):
    """The containment defense must be reachable through normal policy
    construction, not only when a caller passes approved_roots by hand."""

    def test_factories_propagate_download_root(self) -> None:
        from job_ledger import ExecutionPolicy

        budget = ExecutionPolicy.auto_with_budget(
            "1.0", permit_one_submission=True, permit_reference_upload=True,
            download_root="/approved/out",
        )
        exact = ExecutionPolicy.auto_exact_request(
            permit_one_submission=True, permit_reference_upload=True,
            download_root="/approved/out",
        )
        self.assertEqual(budget.download_root, "/approved/out")
        self.assertEqual(exact.download_root, "/approved/out")
        self.assertEqual(budget.to_dict()["download_root"], "/approved/out")
        self.assertEqual(exact.to_dict()["download_root"], "/approved/out")

    def test_factories_default_download_root_to_none(self) -> None:
        from job_ledger import ExecutionPolicy

        policy = ExecutionPolicy.auto_exact_request(
            permit_one_submission=True, permit_reference_upload=True
        )
        self.assertIsNone(policy.download_root)

    def test_orchestrator_rejects_artifact_outside_policy_download_root(self) -> None:
        """End-to-end: an artifact the MCP points outside the policy's approved
        download root must fail the job, proving the defense is live."""
        import hashlib as _hl
        from auto_orchestrator import run_until_blocked
        from job_ledger import ExecutionPolicy

        with tempfile.TemporaryDirectory() as tmp:
            approved = Path(tmp) / "approved"
            approved.mkdir()
            outside = Path(tmp) / "outside.mp4"
            payload = b"PLANTED_ELSEWHERE"
            outside.write_bytes(payload)
            digest = _hl.sha256(payload).hexdigest()

            class Client:
                def invoke(self, action, arguments):
                    if action == "status":
                        return {"ready": True}
                    if action == "account":
                        return {"ready": True}
                    if action == "quote":
                        return {"quote_available": False}
                    if action == "submit":
                        return {"submit_id": "ds_1"}
                    if action == "query":
                        return {
                            "status": "succeeded",
                            "artifact": {"path": str(outside), "sha256": digest},
                        }
                    raise AssertionError(action)

            ledger = JobLedger(Path(tmp) / "job.json")
            ledger.write(new_job(
                "job-root",
                ExecutionPolicy.auto_exact_request(
                    permit_one_submission=True,
                    permit_reference_upload=True,
                    download_root=str(approved),
                ),
            ))
            preview = Path(tmp) / "preview.mp4"
            preview.write_bytes(b"\x00\x00\x00\x18ftypisom")
            preview_sha = _hl.sha256(preview.read_bytes()).hexdigest()
            receipt = {
                "schema_version": "1.0.0",
                "producer_plugin": "codex-blender",
                "producer_version": "0.3.0",
                "artifact_id": "blender_e2e",
                "path": str(preview),
                "sha256": preview_sha,
                "codec": "h264",
                "container": "mp4",
                "dimensions": {"width": 1280, "height": 720},
                "fps": 24.0,
                "duration_seconds": 4.0,
                "bytes": preview.stat().st_size,
                "camera": {"name": "Camera"},
                "frame_range": {"start": 1, "end": 96},
                "preview_mode": "camera_render",
                "restoration": {"status": "confirmed"},
            }
            result = run_until_blocked(
                ledger,
                Client(),
                preview_receipt=receipt,
                request={
                    "prompt": "orbit",
                    "model": "seedance2.5",
                    "resolution": "720p",
                    "ratio": "16:9",
                    "duration_seconds": 4,
                },
            )
            self.assertEqual(result.blocked_reason, "FINAL_ARTIFACT_INVALID")
            self.assertEqual(ledger.read()["state"], JobState.FAILED.value)


class McpArtifactTests(unittest.TestCase):
    """The MCP client must surface an unexpected artifact count."""

    class _Invoker:
        def __init__(self, envelope: dict) -> None:
            self._envelope = envelope

        def call(self, name: str, arguments: dict) -> dict:
            return {"structuredContent": self._envelope, "isError": False}

    def _query(self, payload: dict) -> dict:
        return McpDesignClient(self._Invoker(payload)).query_task("ds_1")

    def test_single_artifact_is_returned(self) -> None:
        result = self._query({
            "status": "succeeded",
            "artifacts": [{"path": "/tmp/a.mp4", "sha256": "a" * 64}],
        })
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["artifact"]["sha256"], "a" * 64)

    def test_multiple_artifacts_raise_instead_of_being_dropped(self) -> None:
        with self.assertRaises(McpToolError) as ctx:
            self._query({
                "status": "succeeded",
                "artifacts": [
                    {"path": "/tmp/a.mp4", "sha256": "a" * 64},
                    {"path": "/tmp/b.mp4", "sha256": "b" * 64},
                ],
            })
        self.assertIn("2 artifacts", str(ctx.exception))

    def test_empty_artifact_list_yields_no_artifact(self) -> None:
        result = self._query({"status": "succeeded", "artifacts": []})
        self.assertNotIn("artifact", result)

    def test_non_list_artifacts_raise(self) -> None:
        with self.assertRaises(McpToolError):
            self._query({"status": "succeeded", "artifacts": {"path": "/tmp/a.mp4"}})


class SubmitPreviewRootTests(unittest.TestCase):
    """submit_video must not forward a preview outside the approved roots."""

    class _Invoker:
        def __init__(self) -> None:
            self.calls: list[tuple[str, dict]] = []

        def call(self, name: str, arguments: dict) -> dict:
            self.calls.append((name, arguments))
            return {"structuredContent": {"submit_id": "ds_1"}, "isError": False}

    REQUEST = {
        "prompt": "orbit",
        "model": "seedance2.5",
        "resolution": "720p",
        "ratio": "16:9",
        "duration_seconds": 4,
    }

    def test_preview_outside_approved_roots_is_rejected_before_calling_mcp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approved = Path(tmp) / "approved"
            approved.mkdir()
            outside = Path(tmp) / "outside.mp4"
            outside.write_bytes(b"X")
            invoker = self._Invoker()
            client = McpDesignClient(invoker)
            with self.assertRaises(ValueError) as ctx:
                client.submit_video({
                    **self.REQUEST,
                    "preview": {"path": str(outside), "sha256": "a" * 64},
                    "approved_roots": [str(approved)],
                })
            self.assertIn("outside the approved roots", str(ctx.exception))
            self.assertEqual(invoker.calls, [], "no MCP call may happen after a rejected path")

    def test_preview_inside_approved_roots_is_forwarded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approved = Path(tmp) / "approved"
            preview = approved / "preview.mp4"
            preview.parent.mkdir(parents=True)
            preview.write_bytes(b"X")
            invoker = self._Invoker()
            client = McpDesignClient(invoker)
            result = client.submit_video({
                **self.REQUEST,
                "preview": {"path": str(preview), "sha256": "a" * 64},
                "approved_roots": [str(approved)],
            })
            self.assertEqual(result["submit_id"], "ds_1")
            self.assertEqual(len(invoker.calls), 1)


class QueryOnlyTransitionTests(unittest.TestCase):
    """Once submitted, a job may never return to Submitted."""

    def test_querying_cannot_transition_to_submitted(self) -> None:
        self.assertNotIn(JobState.SUBMITTED, ALLOWED_TRANSITIONS[JobState.QUERYING])

    def test_transition_is_enforced_by_the_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = JobLedger(Path(tmp) / "job.json")
            ledger.write(new_job("job-q"))
            for state, fields in (
                (JobState.DCC_SELECTED, {"selected_companion": {"plugin_id": "codex-blender", "version": "0.3.0", "contract_version": "1.0.0"}}),
                (JobState.PREVIEW_SPECIFIED, {"preview": {"artifact_id": "a", "sha256": "0" * 64, "producer_plugin": "codex-blender", "producer_version": "0.3.0"}}),
                (JobState.PREVIEW_VALIDATED, {"preview_hash_validated": True}),
                (JobState.CAPABILITY_RESOLVED, {"resolved_capability": {"model": "seedance2.5"}}),
                (JobState.QUOTED, {"quote_inputs": {"prompt": "p", "model": "m", "resolution": "720p", "ratio": "16:9", "duration_seconds": 4.0, "reference_artifact_ids": []}, "quote": {"amount": "0"}}),
                (JobState.APPROVED, {"approved_by": "policy", "approved_at": "2026-09-14T00:00:00Z"}),
                (JobState.SUBMITTED, {"submit": {"design_submit_id": "ds_1"}}),
                (JobState.QUERYING, {}),
            ):
                ledger.transition(state, **fields)
            with self.assertRaises(InvalidTransitionError):
                ledger.transition(JobState.SUBMITTED)
            self.assertEqual(ledger.read()["state"], JobState.QUERYING.value)


class ResolutionSchemaTests(unittest.TestCase):
    """The schema must accept the resolution forms the MCP actually uses."""

    def test_schema_accepts_p_suffix_and_wxh(self) -> None:
        import re
        schema = json.loads((ROOT / "schemas" / "3d_job.schema.json").read_text())
        pattern = re.compile(schema["properties"]["quote_inputs"]["properties"]["resolution"]["pattern"])
        for value in ("720p", "480p", "1080p", "1280x720", "1920x1080"):
            self.assertRegex(value, pattern, f"{value} should be accepted")
        for value in ("huge", "72", "", "1280-720"):
            self.assertNotRegex(value, pattern, f"{value} should be rejected")

    def test_schema_carries_download_root(self) -> None:
        schema = json.loads((ROOT / "schemas" / "3d_job.schema.json").read_text())
        props = schema["properties"]["execution_policy"]["properties"]
        self.assertIn("download_root", props)


if __name__ == "__main__":
    unittest.main()
