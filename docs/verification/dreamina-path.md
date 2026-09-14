# Task 8 verification — Dreamina path

This document records the cross-plugin runtime acceptance evidence for the
Dreamina (Seedance 2.5) half of the Dreamina 3D pipeline.

## Gate status

| Gate                                            | Status            | Reason                                                            |
|-------------------------------------------------|-------------------|--------------------------------------------------------------------|
| `paid_seedance_canary`                          | `PASS`            | Authorized Seedance 2.5 480p/4s canary reached success and downloaded |
| `codex_dreamina_design_receipt_roundtrip`       | `PASS` (fixture)  | Fake Design adapter exercises capabilities/quote/approve/submit/query/download |
| `dreamina_mcp_read_only`                        | `PASS`            | Installed MCP 0.3.0 initialized; trusted CLI and account readiness returned |
| `dreamina_mcp_native_deny`                      | `PASS` (recorded) | Cancel returned `ApprovalDeniedError`; no operation or submit ID was created. **Not re-verified on 2026-09-14** — see below |
| `dreamina_mcp_paid_canary`                      | `PASS`            | One 54-credit submit; restart/query-only/download/hash acceptance passed |

## Re-verification attempt for `dreamina_mcp_native_deny` (2026-09-14)

An attempt was made to reproduce this gate rather than leave it as a record. It
did **not** succeed, so the gate remains a record.

Two obstacles, both environmental:

1. Answering the dialog needs either Screen Recording (to see it) or
   Accessibility (to press Escape). Neither is granted to this agent, so
   `System Events` refused the keystroke outright — it returned
   `"osascript" 不允许发送按键`. The Cancel button could not be pressed.
2. The probe request never reached the dialog anyway: it omitted `model`, and the
   server refused it earlier with `UnsupportedCapabilityError: unknown model:
   None`. The unchanged operation ledger from that attempt therefore proves
   nothing about cancellation; it only shows an invalid request is refused
   before any approval is requested.

The fail-closed behaviour itself is covered by tests: a denied or unavailable
native dialog raises `ApprovalDeniedError`, and `scripts/native_approval.py`
raises it for a dialog that is dismissed or times out — `cancel button` is the
default and `giving up after 300` denies. What remains unverified is the
end-to-end path with a human pressing Cancel.

To close it, an operator with a desktop session should run the submit, press
Cancel, and confirm the operation ledger gained no entry.

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

The legacy fake Design adapter (`tests/fakes/fake_design_adapter.py`) walks
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

That executable route is now fixture-only. Production uses
`McpDesignClient` and the four typed Dreamina Design MCP tools.

## End-to-end completion gate

End-to-end completion (`Completed` state in the job ledger) is gated on
a re-hashed final artifact, not on the design adapter's "succeeded"
report alone. The orchestrator queries, downloads, re-hashes, and only
then transitions the job to `Completed`. A failed re-hash transitions
the job to `Failed` with `error_category='artifact_mismatch'`.

Fresh MCP canary: submit ID `6fd79b95-9b02-4d05-a14d-801001cca136`, one
submission, 54 credits, final SHA-256
`fa7b542c404bda2bfc2facbc2eecd79f028d6e91e08c6ab09fda18fa615335e0`.
