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
