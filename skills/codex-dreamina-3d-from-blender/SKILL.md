---
name: codex-dreamina-3d-from-blender
description: Drive a Blender preview through the validated Dreamina 3D pipeline. Use when the user has a Blender scene and wants a Seedance 2.5 render from it.
metadata:
  type: workflow
  plugin: codex-dreamina-3d
  source_dcc: codex-blender
  status: stable
---

# codex-dreamina-3d-from-blender

## When to use

The user wants a Dreamina 3D render from a Blender scene. Companion
`codex-blender` is already installed.

## Workflow

### Automatic run policy

When the user provides one `auto_with_budget` envelope — approved reference
upload, model/resolution/duration preferences, a maximum charge, and
permission for one remote submission — perform the following workflow without
asking at every state transition. Resolve capability, validate the preview,
obtain and compare the quote, submit once only when it is within the cap,
query the recorded identifier, download, and independently verify the final
artifact. Return one final artifact inventory.

Stop and ask only when the quote exceeds the cap, a required reference was
not authorized for upload, a platform-mandated confirmation or web
prerequisite is pending, validation fails, or recovery would require another
paid submission. `interactive` retains the review at each gate; `review_only`
does not upload or submit.

1. **Inspect.** Call `inspect_scene(executable=codex-blender_adapter,
   scene=<user_scene>)`. Reject if the scene cannot be inspected.
2. **Specify preview.** Collect user-approved camera, frame range, output
   path, and dimensions. Build a `PreviewSpec`.
3. **Export.** Call `request_preview_export(...)` with the user's prompt
   metadata embedded in the request payload. Independent re-hash is
   performed by the orchestrator — never trust the producer's declared
   sha256 alone.
4. **Validate.** Run `validate_artifact(receipt, current_file)` from
   `scripts/handoff_validator.py`. On any error, transition the job to
   `Failed` with the classified `error_category`.
5. **Resolve capability.** Call `design_handoff(mode='capabilities', ...)`.
   On web prereq → stop and ask the user to log in.
6. **Quote.** Build `QuoteInputs(prompt, model, resolution, ratio, duration)`.
   Submit via `design_handoff(mode='quote', ...)`; cross-check echoed fields.
7. **Approve.** Require explicit user authorization before
   `design_handoff(mode='approve', ...)`. Persist the approval id.
8. **Submit.** `design_handoff(mode='submit', ...)`. Persist
   `submit.design_submit_id` BEFORE reporting success.
9. **Query.** Loop `design_handoff(mode='query', ...)` with backoff. On
   `UnknownStateError` only query — never resubmit.
10. **Download + verify.** Re-hash the downloaded artifact and compare to
    the declared hash; reject on mismatch.

## Ledger transitions

Drive the job through `Draft → DccSelected → PreviewSpecified →
PreviewValidated → CapabilityResolved → Quoted → Approved → Submitted →
Querying → Completed | Failed | Unknown` exactly once each.

## Never do

- Never resubmit a job whose `design_submit_id` is already set.
- Never skip the preview validation gate.
- Never send DCC scene data to the design plugin — only the validated
  artifact reference (artifact_id + sha256), the user prompt, and the
  quote inputs.
