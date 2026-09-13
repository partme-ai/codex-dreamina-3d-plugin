# Task 8 verification — Blender path

This document records the cross-plugin runtime acceptance evidence for the
Blender half of the Dreamina 3D pipeline.

## Gate status

| Gate                                            | Status            | Reason                                                            |
|-------------------------------------------------|-------------------|--------------------------------------------------------------------|
| `local_blender_runtime`                         | `PASS`            | Blender 5.2.1 preview-only MP4 and shared receipt validated |
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

## Real runtime evidence

The plan separates offline evidence (Tasks 1–7) from runtime evidence
(Task 8). Exercising a real Blender path requires:

- a local Blender install discoverable through `codex-blender`'s adapter;
- explicit runtime authorization from the operator (the design plugin's
  approval gate is not bypassed for verification).

Probe performed on this environment (2026-09-13):

```text
$ /Applications/Blender.app/Contents/MacOS/Blender --version
Blender 5.2.1 LTS

$ python3 -c '... discover_companions((installed_plugins_root,)) ...'
codex-blender 0.1.0 bin/blender_adapter ('1.0.0',)
```

The `codex-blender` source now publishes `bin/blender_adapter` with receipt
contract `1.0.0`. An authorized Blender 5.2.1 run produced a 320×180, 24 fps,
2-second H.264 MP4 with SHA-256
`2a38c024311534e8ddcced9927a9c4fe64a5c05cba91cd5e7879712ebced8e6e` and
`restoration.status=confirmed`. This orchestrator copied and independently
re-hashed the artifact to the same digest.

## Determinism guarantees preserved

The contract check (`scripts/handoff_validator.py`) is independent of
whether the adapter is fake or real: schema version, producer id,
restoration status, codec/container, dimensions, fps, duration, size,
and sha256 are all validated against the receipt and the file. A real
adapter that emits a non-conforming receipt will be rejected identically.
