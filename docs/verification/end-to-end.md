# Task 8 verification — End-to-end

This document records the end-to-end runtime acceptance evidence for the
Dreamina 3D pipeline.

## Gate status

| Gate                                              | Status            | Reason                                              |
|---------------------------------------------------|-------------------|------------------------------------------------------|
| `fixture_blender_to_design_e2e`                   | `PASS` (fixture)  | Driven by fake Blender + fake Design adapters         |
| `fixture_maya_to_design_e2e`                      | `PASS` (fixture)  | Driven by fake Maya + fake Design adapters            |
| `real_blender_to_design_e2e`                      | `NOT_RUN`         | No real Blender install, no Dreamina credentials     |
| `real_maya_to_design_e2e`                         | `NOT_RUN`         | No real Maya install, no Dreamina credentials        |
| `paid_seedance_canary`                            | `NOT_RUN`         | No action-time approval, no Dreamina credentials     |

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

$ python3 -m unittest discover -s tests
............................................................
Ran 88 tests in ~12s
OK
```

The full unit and integration test suite covers every failure mode the
real adapters would surface, including duplicate submit, unknown state,
artifact hash mismatch, restoration unknown, and timeout → query-only.

## What blocks production release

The following items must be exercised in an authorized environment
before production release:

1. Real Blender adapter smoke test (see [./blender-path.md](./blender-path.md)).
2. Real Maya adapter smoke test (see [./maya-path.md](./maya-path.md)).
3. Paid Seedance canary (see [./dreamina-path.md](./dreamina-path.md)).
4. Explicit operator sign-off recorded in this document.