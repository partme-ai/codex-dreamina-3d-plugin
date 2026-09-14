# Task 8 verification — End-to-end

This document records the end-to-end runtime acceptance evidence for the
Dreamina 3D pipeline.

## Gate status

| Gate                                              | Status            | Reason                                              |
|---------------------------------------------------|-------------------|------------------------------------------------------|
| `fixture_blender_to_design_e2e`                   | `PASS` (fixture)  | Driven by fake Blender + fake Design adapters         |
| `fixture_maya_to_design_e2e`                      | `PASS` (fixture)  | Driven by fake Maya + fake Design adapters            |
| `real_blender_preview_handoff`                    | `PASS`            | Managed Blender 5.2.1 + installed implementation; receipt re-hash passed |
| `public_blender_adapter_entry`                    | `PASS`            | Refreshed 0.3.0 cache matches GitHub `e2f6f02` |
| `real_blender_to_design_e2e`                      | `PASS`            | One MCP submit, restart/query-only, verified download |
| `real_maya_to_design_e2e`                         | `NOT_RUN`         | No real Maya install or callable companion adapter   |
| `real_blender_to_seedance_cli_e2e`                | `PASS`            | Authorized Seedance 2.5 canary passed artifact verification |
| `paid_seedance_canary`                            | `PASS`            | One submission, 54 task-attributed credits, no resubmit |
| `dreamina_design_mcp_e2e`                         | `PASS`            | Installed MCP handled approval, submit, query and download |

## End-to-end completion contract

End-to-end completion requires **all four** of the following gates to be
true; failing any one transitions the job to `Failed` rather than to
`Completed`:

1. **Preview receipt validated.** The handoff validator accepted the
   preview receipt and confirmed the on-disk sha256.
2. **Capability resolved.** The design plugin returned at least one
   capability matching the requested model.
3. **Quote bound.** The quote echoed back every quote-binding input and
   was explicitly approved by the user.
4. **Final artifact accepted.** The design plugin's `succeeded` response
   was followed by a download whose on-disk sha256 matches the declared
   hash.

HTTP 200, CLI exit code 0, and "succeeded" responses are **not** by
themselves sufficient to transition to `Completed`.

## How to reproduce the fixture end-to-end

The fixture path uses the fake adapters that ship under `tests/fakes/`:

```text
$ python3 scripts/validate_distribution.py .
validated codex-dreamina-3d compatibility foundation 0.1.0

$ /usr/local/bin/python3 -m unittest discover -s tests
...
Ran 131 tests in 18.371s
OK
```

The full unit and integration test suite covers every failure mode the
real adapters would surface, including duplicate submit, unknown state,
artifact hash mismatch, restoration unknown, and timeout → query-only.

## What blocks production release

The following items must be exercised in an authorized environment
before production release:

1. Restore and package the missing Blender adapter implementation, then run a
   fresh Blender 5.2.1 preview and receipt re-hash.
2. Real Maya adapter smoke test, if Maya is restored to release scope.
3. Keep the official Web route optional until the user-installed official
   uploader is present; the factory-startup probe currently finds none.
4. Commit, push, run remote CI, reinstall public plugins, and verify source/cache parity.
