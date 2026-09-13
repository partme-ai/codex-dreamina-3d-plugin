# Codex Dreamina 3D Plugin Technical Solution

## Decision

Implement a receipt-driven orchestration plugin. Integrate only through stable local JSON contracts and Skill capability discovery; do not import companion implementation modules.

## Implemented layout

```text
.codex-plugin/plugin.json
skills/codex-dreamina-3d-use/
skills/codex-dreamina-3d-from-blender/
skills/codex-dreamina-3d-from-maya/
scripts/capability_probe.py
scripts/handoff_validator.py
schemas/3d_job.schema.json
tests/
```

## Job state

`Draft -> DccSelected -> PreviewSpecified -> PreviewValidated -> CapabilityResolved -> Quoted -> Approved -> Submitted -> Querying -> Completed|Failed|Unknown`.

Every transition stores receipts atomically. `Unknown` may only query/reconcile. Any change to preview hash, prompt, model, resolution, ratio, duration, or reference inputs invalidates the quote and approval.

## Clean-room implementation

Observed vendor behavior informs tests: camera render and local-video paths, state restoration, aspect-preserving resolution, H.264 MP4, and protocol limits. The implementation uses the public DCC and Dreamina CLI contracts, not vendor Python/JavaScript, UI strings, binary ffmpeg, or bridge protocol.

## Tests

Contract tests validate producer compatibility and media receipts. State tests cover companion absence, stale preview, changed quote, duplicate submit, timeout, resume, and artifact mismatch. End-to-end tests use fake companion CLIs; real Blender/Maya/Dreamina tests are separate authorized gates.
