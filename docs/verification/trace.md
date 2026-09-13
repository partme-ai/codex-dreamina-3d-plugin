# TRACE Evaluation Evidence — codex-dreamina-3d Skills

Plan gates covered: *"Run TRACE and forward scenarios"* (Task 5) and
*"Run all offline unit/integration tests, plugin and Skill validators, TRACE,
link audit and `git diff --check`"* (Task 7).

The historical scorecard below was produced with
`skill-trace-evaluation/scripts/trace_evaluate.py`. CI now uses the
repository-owned `scripts/trace_gate.py`, which checks the five TRACE
dimensions as observable invariants and has no user-specific absolute path.
The scored report remains design evidence; the repository gate is the release
pass/fail authority.

## Summary

| Skill | T · Trust | R · Reliability | A · Adaptability | C · Convention | E · Effectiveness | Overall |
|---|---|---|---|---|---|---|
| `codex-dreamina-3d-use` | 3.58 | 3.50 | 4.38 | 3.75 | 3.75 | **3.79** |
| `codex-dreamina-3d-from-blender` | 3.58 | 3.55 | 4.25 | 3.75 | 3.90 | **3.81** |
| `codex-dreamina-3d-from-maya` | 3.58 | 3.55 | 4.38 | 3.75 | 3.90 | **3.83** |
| `codex-dreamina-3d-resume` | 3.58 | 3.55 | 4.25 | 3.75 | 3.90 | **3.81** |

The original four Skills retain their recorded scores. The two one-click route
Skills additionally scored `3.92` (`codex-dreamina-3d-jimeng-web`) and `4.00`
(`codex-dreamina-3d-auto-seedance`). All six clear the Good tier:
`skill_trace = 6/6`.

## Dimension readout

**T · Trust (3.58).** No secrets, no bundled scripts in the skill directories,
and the plugin ships a top-level `PRIVACY.md` that states the plugin collects
no telemetry. Two structural deductions are expected for this repository:
T2 (Chinese adaptation) scores 2.0 because the Skill bodies are English-only —
the repository keeps English as the primary language with `README.zh-CN.md` as
the translated companion; and T3 (boundary transparency) scores 3.0 because
the Skills use a "Never do" section rather than a three-way
✅/⚠/❌ applicability table.

**R · Reliability (3.50–3.55).** Each Skill carries explicit prohibitions
(silent installs, auto-resubmits, sending DCC scene data) and the two pipeline
Skills document a validation gate. Deductions reflect the absence of an
interactive-guidance template for incomplete user input.

**A · Adaptability (4.25–4.38, strongest dimension).** Descriptions are
scenario-routed rather than keyword-stuffed, and the router Skill explicitly
handles the zero/one/two-companion cases.

**C · Convention (3.75).** Frontmatter names are valid and match directory
names; bodies are short and task-focused. The deduction is the absence of
`references/` subdirectories — the depth lives in `docs/` and `scripts/`
instead, which suits a plugin whose behaviour is enforced by code rather than
prose.

**E · Effectiveness (3.75–3.90).** Each Skill states the observable
completion contract and separates local preview status, remote submission
status, and final artifact acceptance.

## No-skill baseline comparison

The TRACE framework compares a Skill against a no-skill reference group.
The executable baselines live in
[`tests/scenarios/no_skill_baselines.py`](../../tests/scenarios/no_skill_baselines.py)
and are run by [`tests/test_scenarios.py`](../../tests/test_scenarios.py):

| Scenario | No-skill failure | Guard that prevents it |
|---|---|---|
| `silent_companion_install` | Agent installs a missing companion itself | `capability_probe.select_companion` raises with install guidance |
| `ambiguous_dcc_choice` | Agent picks Blender/Maya arbitrarily | `AmbiguousCompanionError` unless the request names one |
| `unvalidated_preview` | Preview forwarded without validation | `handoff_validator.validate_artifact` rejects bad receipts |
| `quote_reuse` | Stale quote reused after edits | `JobLedger.invalidate_quote` clears quote and approval |
| `paid_retry` | Paid action submitted twice | duplicate submit returns the existing `design_submit_id` |
| `false_end_to_end_completion` | "succeeded" treated as completion | `design_handoff` re-hashes the artifact before accepting |

Per TRACE, effectiveness is measured as improvement over the no-skill group.
Every baseline is an executable assertion, so 6/6 guards firing is concrete
evidence of benefit rather than an assertion of intent.

## Improvement suggestions (prioritised)

1. **P1 — Add `references/` depth.** C2/E3 score lower without subdirectories.
   Moving the state-machine table and gate contracts into
   `skills/*/references/` would raise C2, C3, and E3 together.
2. **P2 — Add a three-way applicability table (✅/⚠/❌) to each Skill.** This
   targets T3, the single largest Trust deduction.
3. **P3 — Add Chinese summaries** to each Skill body to lift T2, consistent
   with the repository's existing bilingual convention.

These are quality improvements, not plan requirements: the plan asks that
TRACE be *run*, which this document records.

## Reproduce

```text
$ python3 /Users/wandl/.agents/skills/skill-trace-evaluation/scripts/trace_evaluate.py \
      --skill-dir skills/codex-dreamina-3d-use --format json
```

`tests/test_trace.py` runs the repository-owned gate for all six Skills and
asserts each passes T/R/A/C/E. `scripts/ci_gate.py --strict` also fails if this
gate is unavailable or any required test is skipped.
