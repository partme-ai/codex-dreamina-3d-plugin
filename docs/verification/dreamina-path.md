# Task 8 verification — Dreamina path

This document records the cross-plugin runtime acceptance evidence for the
Dreamina (Seedance 2.5) half of the Dreamina 3D pipeline.

## Gate status

| Gate                                            | Status            | Reason                                                            |
|-------------------------------------------------|-------------------|--------------------------------------------------------------------|
| `paid_seedance_canary`                          | `NOT_RUN`         | Action-time approval not granted; no credentials available        |
| `codex_dreamina_design_receipt_roundtrip`       | `PASS` (fixture)  | Fake Design adapter exercises capabilities/quote/approve/submit/query/download |

## Why `paid_seedance_canary` was not exercised here

The plan explicitly requires a separate action-time approval for any
paid Seedance generation. That approval was not granted in this
environment, and there are no Dreamina credentials available.

Probe performed on this environment (2026-09-12):

```text
$ command -v dreamina dreamina-cli    # (no output)
```

No Dreamina CLI is installed and no credentials were supplied, so the
gate is recorded as `NOT_RUN` rather than inferred.

To run the canary in a future authorized environment:

1. Install the real `codex-dreamina-design` plugin and complete the
   web login that the design adapter requires (see
   `WebPrerequisiteError`).
2. Explicitly approve the canary run before invoking the orchestrator;
   the design handoff refuses to call `submit` without that approval.
3. Use a low-cost Seedance 2.5 model and minimal duration.

## What was exercised offline

The fake Design adapter (`tests/fakes/fake_design_adapter.py`) walks
the full capability → quote → approve → submit → query → download loop
without ever touching the network. The orchestrator's
`scripts/design_handoff.py` accepts the fake adapter's receipts and
rejects them when:

- the quote echoes back inputs that differ from the request
  (`QuoteMismatchError`),
- the approval is rejected or expired (`ApprovalRejectedError`),
- the submit is a duplicate (returns the prior `design_submit_id`),
- the query reports `unknown` (`UnknownStateError`),
- the artifact's declared sha256 does not match the on-disk file
  (`ArtifactMismatchError`).

These classifications are the same ones a real adapter would surface,
because the orchestrator inspects only the public receipt interface.

## End-to-end completion gate

End-to-end completion (`Completed` state in the job ledger) is gated on
a re-hashed final artifact, not on the design adapter's "succeeded"
report alone. The orchestrator queries, downloads, re-hashes, and only
then transitions the job to `Completed`. A failed re-hash transitions
the job to `Failed` with `error_category='artifact_mismatch'`.