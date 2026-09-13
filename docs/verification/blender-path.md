# Task 8 verification — Blender path

This document records the cross-plugin runtime acceptance evidence for the
Blender half of the Dreamina 3D pipeline.

## Gate status

| Gate                                            | Status            | Reason                                                            |
|-------------------------------------------------|-------------------|--------------------------------------------------------------------|
| `local_blender_runtime`                         | `NOT_RUN`         | Blender is present, but no callable companion adapter or runtime authorization is available |
| `codex_blender_receipt_recorded`                | `PASS` (fixture)  | Validated via the fake Blender adapter (`tests/fakes/fake_blender_adapter.py`) |
| `blender_to_design_receipt_chain`               | `PASS` (fixture)  | Fake Design adapter accepted the preview receipt without a network call |

## How the receipt was recorded (fixture path)

The fake Blender adapter (`tests/fakes/fake_blender_adapter.py`) honours the
same argv + JSON contract documented for the real codex-blender adapter:

```text
$ python3 tests/fakes/fake_blender_adapter.py \
    --request tests/fixtures/blender_artifact.json \
    --receipt /tmp/blender.receipt.json \
    --output  /tmp/blender.mp4
```

A successful run produces a receipt whose `producer_plugin` is
`codex-blender`, `restoration.status == 'confirmed'`, and `sha256` matches
the independently re-hashed on-disk file. The orchestrator's
`scripts/handoff_validator.py` accepts that receipt.

## Why `local_blender_runtime` was not exercised here

The plan separates offline evidence (Tasks 1–7) from runtime evidence
(Task 8). Exercising a real Blender path requires:

- a local Blender install discoverable through `codex-blender`'s adapter;
- explicit runtime authorization from the operator (the design plugin's
  approval gate is not bypassed for verification).

Probe performed on this environment (2026-09-13):

```text
$ /Applications/Blender.app/Contents/MacOS/Blender --version
Blender 5.2.1 LTS

$ python3 -c '... discover_companions((Path(".."),)) ...'
# no candidates: codex-blender-plugin does not ship bin/blender_adapter
```

Blender and the `codex-blender` plugin are present, but the orchestrator's
documented capability probe cannot resolve a callable adapter executable.
Explicit runtime authorization was likewise not granted, so the gate remains
`NOT_RUN` rather than inferred. To run it, publish the `bin/blender_adapter`
contract from the companion plugin, obtain runtime authorization, and invoke
it with the same argv/JSON contract shown above.

## Determinism guarantees preserved

The contract check (`scripts/handoff_validator.py`) is independent of
whether the adapter is fake or real: schema version, producer id,
restoration status, codec/container, dimensions, fps, duration, size,
and sha256 are all validated against the receipt and the file. A real
adapter that emits a non-conforming receipt will be rejected identically.
