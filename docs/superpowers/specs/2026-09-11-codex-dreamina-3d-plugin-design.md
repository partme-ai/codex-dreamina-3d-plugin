# Codex Dreamina 3D Plugin Design

## Goal

Orchestrate a verified Blender or Maya preview artifact into a safe, explicitly approved Seedance 2.5 generation workflow.

## Requirements

- Detect exactly one supported DCC companion or require the user to choose.
- Validate the shared artifact receipt and current file hash before Dreamina work.
- Delegate capability, quotation, approval, submission, query and download to `codex-dreamina-design`.
- Persist an end-to-end non-secret job ledger with resumable states.
- Keep local export, remote submission, and artifact acceptance as separate gates.

## Execution policy

The plugin accepts the Blender request's `ExecutionPolicy`. In
`auto_with_budget`, the user makes one bounded authorization at task start:
model preference, resolution, duration, reference-upload permission, a
maximum charge, and permission for one remote submission. The orchestrator
then automatically resolves capability, validates the preview, obtains a
quote, compares it with the cap, submits once, polls only the recorded submit
identifier, downloads, re-hashes, probes media, and returns the final
artifact inventory.

The workflow asks again only if a required reference was not authorized for
upload, the actual quote exceeds the cap, a platform-mandated confirmation is
shown, the web prerequisite is missing, an output must overwrite an
unapproved file, validation fails, or recovery would create another paid
submission. A transient query failure never permits a resubmit. `interactive`
retains per-stage review; `review_only` performs no upload or remote action.

The job ledger records the policy envelope, observed quote, consumed approval,
single `design_submit_id`, and final verification evidence. This makes the
automatic path auditable without turning the user experience into a sequence
of manual confirmation dialogs.

## Non-goals

No DCC internals, Dreamina private API, vendor uploader copy, bundled media binaries, silent companion install, or automatic paid retry.
