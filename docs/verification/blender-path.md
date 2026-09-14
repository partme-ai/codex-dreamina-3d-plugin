# Task 8 verification — Blender path

Cross-plugin runtime acceptance evidence for the Blender half of the Dreamina 3D
pipeline.

## Gate status

| Gate | Status | Reason |
|---|---|---|
| `local_blender_runtime` | `PASS` | **Independently reproduced** — a fresh managed Blender 5.2.1 Harness produced a byte-identical MP4 (see below) |
| `public_blender_adapter_entry` | `PASS` | Installed 0.3.0 cache at GitHub `e2f6f02`; `bin/blender_adapter --help` exits 0 |
| `codex_blender_receipt_recorded` | `PASS` (fixture) | Validated via `tests/fakes/fake_blender_adapter.py` |
| `blender_to_design_receipt_chain` | `PASS` (fixture) | Fake Design adapter accepted the preview receipt without a network call |

## Independent reproduction (2026-09-14)

`local_blender_runtime` was previously a *record*. It has now been reproduced
from scratch, and the artifact came out byte-identical:

| Value | Previously recorded | Reproduced | |
|---|---|---|---|
| SHA-256 | `b8b5b7607d29b4ac02da83117078b491badd22e0a81e995aa09c0402e18847bb` | same | identical |
| bytes | `104428` | `104428` | identical |
| media | 1920×1080, H.264, 24 fps, 2.000 s | same | identical |

### Exact reproduction procedure

```bash
BL=/Applications/Blender.app/Contents/MacOS/Blender
PLUGIN=<codex-blender checkout>          # or the installed 0.3.0 cache
WS=$(mktemp -d); mkdir -p "$WS/runtime" "$WS/out"; chmod 700 "$WS/runtime"

# 1. Start a managed Harness in a factory scene (default Cube + Camera).
"$BL" --disable-autoexec --factory-startup \
  --python "$PLUGIN/scripts/managed_bootstrap.py" -- \
  --session-id d3verify --runtime-dir "$WS/runtime" --output-root "$WS/out" &
# wait for "$WS/runtime/d3verify.json" (mode 0600)

# 2. Export the preview through the public adapter.
cat > "$WS/request.json" <<'JSON'
{"artifact_id": "blender_verify_e2e", "camera_name": "Camera",
 "frame_range": {"start": 1, "end": 48}}
JSON
CODEX_BLENDER_DESCRIPTOR="$WS/runtime/d3verify.json" \
CODEX_BLENDER_FFPROBE=/opt/homebrew/bin/ffprobe \
python3 "$PLUGIN/scripts/dreamina_adapter.py" \
  --descriptor "$WS/runtime/d3verify.json" \
  --request "$WS/request.json" \
  --receipt "$WS/receipt.json" \
  --output "$WS/out/preview.mp4"
```

The run above produced the receipt reproduced in the table, with
`restoration.status = confirmed`.

### What was independently checked, not taken on trust

1. **The artifact hash.** `shasum -a 256` on the produced MP4 equals the hash
   the receipt claims, and equals the previously recorded hash.
2. **The media properties.** `ffprobe` independently reports `h264`,
   `1920x1080`, `24/1`, `2.000000` s, `104428` bytes.
3. **The receipt contract.** `scripts/handoff_validator.py::validate_artifact`
   returns no errors for the receipt against the on-disk file.
4. **The scene was restored.** `scene.inspect` reported the same object set
   (3) before and after the export, with the compared settings unchanged.
5. **The whole local chain.** Driving `run_until_blocked` with the real receipt
   and a fake design client advanced `Draft → … → Submitted → Querying` with
   exactly **one** submit and a persisted `design_submit_id`.

### The artifact is deliberately not committed

The distribution boundary forbids generated media in the plugin package, so the
MP4 is not stored here. What is stored is the procedure above plus the hash: the
run is deterministic, so the digest is the checkable claim. To re-verify, run
the procedure and compare the digest.

## Fixture path

`tests/fakes/fake_blender_adapter.py` honours the same argv + JSON contract as
the real adapter:

```text
$ python3 tests/fakes/fake_blender_adapter.py \
    --request tests/fixtures/blender_artifact.json \
    --receipt /tmp/blender.receipt.json \
    --output  /tmp/blender.mp4
```

The fake path is what the offline suite exercises. The real path above is the
runtime gate.

## Determinism guarantees preserved

The contract check is independent of whether the adapter is fake or real:
schema version, producer id, restoration status, codec/container, dimensions,
fps, duration, size, and sha256 are all validated against the receipt and the
file. A real adapter that emits a non-conforming receipt is rejected
identically.
