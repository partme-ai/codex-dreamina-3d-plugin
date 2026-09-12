# Task 8 verification — Maya path

This document records the cross-plugin runtime acceptance evidence for the
Maya half of the Dreamina 3D pipeline.

## Gate status

| Gate                                            | Status            | Reason                                                          |
|-------------------------------------------------|-------------------|------------------------------------------------------------------|
| `local_maya_runtime`                            | `NOT_RUN`         | No local Maya install (and no license) detected in this environment |
| `codex_maya_receipt_recorded`                   | `PASS` (fixture)  | Validated via the fake Maya adapter (`tests/fakes/fake_maya_adapter.py`) |
| `maya_to_design_receipt_chain`                  | `PASS` (fixture)  | Fake Design adapter accepted the preview receipt without a network call |

## How the receipt was recorded (fixture path)

The fake Maya adapter (`tests/fakes/fake_maya_adapter.py`) honours the
same argv + JSON contract documented for the real codex-maya adapter:

```text
$ python3 tests/fakes/fake_maya_adapter.py \
    --request tests/fixtures/maya_artifact.json \
    --receipt /tmp/maya.receipt.json \
    --output  /tmp/maya.mp4
```

A successful run produces a receipt whose `producer_plugin` is
`codex-maya`, `preview_mode == 'local_video'`, `restoration.status == 'confirmed'`,
and `sha256` matches the independently re-hashed on-disk file. The
orchestrator's `scripts/handoff_validator.py` accepts that receipt.

## Why `local_maya_runtime` was not exercised here

Exercising a real Maya path requires a local Maya install with a valid
license and an installed codex-maya adapter.

Probe performed on this environment (2026-09-12):

```text
$ command -v maya mayapy Maya          # (no output)
$ ls -d /Applications/Autodesk/maya*   # no matches found
```

No Maya installation is present, so the gate is recorded as `NOT_RUN`
rather than inferred. Explicit runtime authorization was likewise not
granted. The contract check (`scripts/handoff_validator.py`) does not
depend on whether the adapter is fake or real.

## Determinism guarantees preserved

The same validator enforces producer id, schema version, restoration
status, codec/container, dimensions, fps, duration, size, and sha256.
A real Maya adapter that emits a non-conforming receipt will be rejected
identically.