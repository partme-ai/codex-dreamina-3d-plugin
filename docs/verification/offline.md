# Offline Verification Evidence — codex-dreamina-3d

This document records the offline (no-network, no-DCC, no-credits) evidence
that the Dreamina 3D plugin's Tasks 1–7 satisfy the implementation plan's
completion gate (excluding the runtime-acceptance items recorded separately
in [Task 8 verification](./blender-path.md), [Task 8 verification — Maya](./maya-path.md),
and [Task 8 verification — Dreamina](./dreamina-path.md)).

## Test suite

The plugin's offline test suite covers every non-runtime gate:

```text
$ /usr/local/bin/python3 -m unittest discover -s tests -v
...
Ran 131 tests in ~18s
OK
```

Individual breakdown:

| Test file                              | Coverage                                         |
|----------------------------------------|---------------------------------------------------|
| `tests/test_distribution.py`           | identity, marketplace parity, brand assets, secrets |
| `tests/test_handoff_validator.py`      | Task 1 — receipt validation, hash-mismatch, mutation detection |
| `tests/test_capability_probe.py`       | Task 2 — companion discovery + selection        |
| `tests/test_job_ledger.py`             | Task 3 — state machine, atomicity, secret scrubbing |
| `tests/test_dcc_handoff.py`            | Task 4 — fake Blender/Maya adapters, no internal imports |
| `tests/test_design_handoff.py`         | Task 5 — fake Design adapter, normalized request |
| `tests/test_skills.py`                 | Task 6 — four Skills, frontmatter, prohibitions  |
| `tests/test_distribution_extended.py`  | Task 7 — Skill parity, link audit, ffmpeg absence |
| `tests/test_e2e_fixture_pipeline.py`    | Task 8 — Blender/Maya fixture pipelines reach validated completion |
| `tests/test_local_install.py`           | Local marketplace registration, cachebuster, installed Skill discovery |
| `tests/test_scenarios.py`               | No-skill baselines and executable guard scenarios |
| `tests/test_three_package_validation.py`| Blender, Maya, and Dreamina 3D distribution validators |
| `tests/test_trace.py`                   | Four-Skill TRACE structure and score floor |
| `tests/test_verification_docs.py`       | Runtime gate evidence remains explicit and non-inferred |

## Distribution validator

```text
$ python3 scripts/validate_distribution.py .
validated codex-dreamina-3d compatibility foundation 0.1.0
```

The validator enforces:
- plugin id `codex-dreamina-3d`
- version `0.1.0`
- skills path `./skills/`
- no `mcpServers` / portable `plugin.json` / `mcp.json`
- 1–3 default prompts of length ≤ 128
- marketplace parity with the GitHub repository URL
- PNG dimensions for logo (1024²), logo-dark (1024²), composer icon (256²)
- absence of secret patterns across every tracked file
- presence of `assets/`, `skills/`, `schemas/`, `scripts/`, `tests/` and the
  required docs/legal files

## Source / cache parity and `git diff --check`

The branch `feat/3d-handoff-tasks-1-7` carries every change as commits; a
fresh `git clone` of the repository URL `https://github.com/partme-ai/codex-dreamina-3d-plugin.git`
yields the same content because no remote binaries, cache directories, or
symlinks were introduced.

```text
$ git diff --check
(no output — clean)
```

## Runtime-acceptance items

The completion gate's runtime items are recorded separately and explicitly
marked as not run in this offline environment:

- `local_blender_runtime` — see [./blender-path.md](./blender-path.md) (`PASS`)
- `local_maya_runtime` — see [./maya-path.md](./maya-path.md) (`NOT_RUN`)
- `paid_seedance_canary` — see [./dreamina-path.md](./dreamina-path.md) (`PASS`)

These gates require explicit runtime authorization and external software /
credentials and must be exercised in a controlled environment before a
production release.
