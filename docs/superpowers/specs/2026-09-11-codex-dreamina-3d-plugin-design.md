# Codex Dreamina 3D Plugin Design

## Goal

Orchestrate a verified Blender or Maya preview artifact into a safe, explicitly approved Seedance 2.5 generation workflow.

## Requirements

- Detect exactly one supported DCC companion or require the user to choose.
- Validate the shared artifact receipt and current file hash before Dreamina work.
- Delegate capability, quotation, approval, submission, query and download to `codex-dreamina-design`.
- Persist an end-to-end non-secret job ledger with resumable states.
- Keep local export, remote submission, and artifact acceptance as separate gates.

## Non-goals

No DCC internals, Dreamina private API, vendor uploader copy, bundled media binaries, silent companion install, or automatic paid retry.
