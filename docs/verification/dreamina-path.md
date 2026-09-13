# Task 8 verification — Dreamina path

This document records the cross-plugin runtime acceptance evidence for the
Dreamina (Seedance 2.5) half of the Dreamina 3D pipeline.

## Gate status

| Gate                                            | Status            | Reason                                                            |
|-------------------------------------------------|-------------------|--------------------------------------------------------------------|
| `paid_seedance_canary`                          | `PASS`            | Authorized Seedance 2.5 480p/4s canary reached success and downloaded |
| `codex_dreamina_design_receipt_roundtrip`       | `PASS` (fixture)  | Fake Design adapter exercises capabilities/quote/approve/submit/query/download |

## Paid canary evidence

The user explicitly authorized Blender and Seedance path validation. Exactly
one paid generation was submitted; every later operation queried the same
server-issued submit ID and never resubmitted.

Probe performed on this environment (2026-09-13):

```text
$ command -v dreamina
/Users/wandl/.local/bin/dreamina
$ dreamina --help
Usage: dreamina [flags]
```

Observed result:

```text
submit_id=9f703ef1-3cf2-452a-bfde-4c96433e4434
mode=multimodal2video
model=seedance2.5
video_resolution=480p
duration=4
terminal_status=success
commerce_info.credit_count=54
output=854x480, H.264/AAC MP4, 24 fps, 4.063991 s, 762550 bytes
sha256=950e9a25bd773c04aace0bd0ca5e2b72a255f7abf69286c8677637b6b4f79a75
```

The account balance changed concurrently with another 192-credit task, so the
balance delta is not used as this canary's cost proof. The task-specific
`commerce_info.credit_count=54` is the attributable charge. The downloaded
artifact was independently checked with ffprobe and SHA-256; CLI success alone
was not treated as artifact acceptance.

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
