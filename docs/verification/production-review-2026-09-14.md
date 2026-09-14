# Independent Release Review — 2026-09-14

Plan: [`docs/superpowers/plans/2026-09-14-production-release-handoff.md`](../superpowers/plans/2026-09-14-production-release-handoff.md) Task 1.

Two clean-context reviewers examined the release diff independently. Neither
reviewer had this session's context, and both were instructed to work read-only
and to end with an exact verdict token.

## Reviewed range

| Field | Value |
|---|---|
| Base SHA | `550da6ef69dcc2cbdafdd1c5b4a98896212e5808` |
| HEAD at final verdict | `c2d74c21c9c2439d49eb60cf3b898f0c3a1232a3` |
| Commits under review | 10 |
| Diffstat | 44 files changed, 2820 insertions(+), 182 deletions(-) |
| Specification | [`docs/superpowers/plans/2026-09-14-production-readiness.md`](../superpowers/plans/2026-09-14-production-readiness.md) |

## Reviewers

| Lane | Reviewer type | Verdict |
|---|---|---|
| Code / security | Clean-context code reviewer (subagent) | **APPROVE** |
| Architecture | Clean-context architecture auditor (subagent) | **CLEAR** |

## Round 1 — both lanes negative

Round 1 returned `REQUEST_CHANGES` (code/security) and `BLOCK` (architecture).

### Code / security findings

| # | Severity | Location | Finding |
|---|---|---|---|
| C1 | HIGH | `scripts/design_handoff.py:71` | `verify_result_artifact` called `is_symlink()` on the unresolved path. That inspects only the final component, so a symlinked *intermediate* directory let an artifact escape the approved root. |
| C2 | HIGH | `scripts/auto_orchestrator.py:181`, `scripts/mcp_design_client.py:52-69` | The artifact path returned by the Design MCP was never validated against an approved root. A compromised server could point the client at any readable local file and supply its correct hash. |
| C3 | MEDIUM | `scripts/mcp_design_client.py:92-116` | `submit_video` forwarded `preview.path` without checking it against `approved_roots`. |
| C4 | MEDIUM | `scripts/auto_orchestrator.py:111-117`, schema | Resolution was stored unvalidated while the schema pattern accepted only `WxH`; the MCP actually uses `720p`. |
| C5 | MEDIUM | `scripts/mcp_design_client.py:52-69` | A non-empty `artifacts` list with more than one entry was silently dropped, masking a server-side bug behind a generic "no artifact" error. |
| C6 | LOW | `scripts/job_ledger.py:60` | `QUERYING -> SUBMITTED` was permitted, so the raw state machine allowed re-submission. |
| C7 | LOW | `tests/test_auto_orchestrator.py:59` | Test data used `480p`, a form the schema rejected. |

### Architecture findings

| # | Severity | Location | Finding |
|---|---|---|---|
| A1 | HIGH | `skills/codex-dreamina-3d-from-maya/SKILL.md:8` | Frontmatter declared `status: stable` while the body and the Blender-only release scope require `experimental`. A frontmatter-only consumer would advertise Maya as production-ready. |
| A2 | MEDIUM | `tests/fakes/.blender_adapter.sh:2`, `.maya_adapter.sh:2` | Committed shims embedded an absolute private path and a hardcoded `/usr/local/bin/python3`, violating the Global Constraint against committing absolute private paths. |
| A3 | MEDIUM | `scripts/ci_gate.py:73-78` | The `.CodexCliTests.` discovery filter could select zero tests and still report success. |
| A4 | LOW | `.github/workflows/ci.yml:18` | CI runs on `ubuntu-latest` while production scope is macOS + Blender 5.2.1 LTS. |

## Disposition — round 1

All seven code/security findings and all four architecture findings were fixed.
Dispatched to an implementer, affected tests rerun, and **both** lanes restarted
over the new HEAD as the plan requires.

| Finding | Fix | Commit |
|---|---|---|
| C1 | `verify_result_artifact` resolves before any check and compares containment on resolved paths on both sides (correct where the temp root is itself a link, e.g. `/tmp` -> `/private/tmp`). | `a3bae9d` |
| C2 | Policy persists `download_root`; the orchestrator passes it as `approved_roots`; schema field added. | `a3bae9d`, `c2d74c2` |
| C3 | `_require_within_roots` rejects an out-of-root preview *before* any MCP call. | `a3bae9d` |
| C4 | Schema pattern accepts both `720p` and `1280x720`. | `a3bae9d` |
| C5 | A non-empty artifacts list with `len != 1` raises `McpToolError`. | `a3bae9d` |
| C6 | `SUBMITTED` removed from `ALLOWED_TRANSITIONS[QUERYING]`. | `a3bae9d` |
| C7 | Covered by the C4 schema change. | `a3bae9d` |
| A1 | Frontmatter now `status: experimental`. | `a3bae9d` |
| A2 | Both shims deleted from git (stale leftovers — the current test returns the `.py` adapter directly) and `.gitignore` blocks `tests/fakes/*.sh` from returning. | `a3bae9d` |
| A3 | `MINIMUM_REQUIRED_TESTS = 150` floor raises `StrictGateError` on a shrunken suite. | `a3bae9d` |
| A4 | Accepted with rationale, see below. | — |

## Round 2 — one new finding

Round 2 confirmed all six code fixes as real and sufficient, and raised one new
MEDIUM plus one LOW.

| # | Severity | Location | Finding |
|---|---|---|---|
| C8 | MEDIUM | `scripts/job_ledger.py:106-127` | `ExecutionPolicy.auto_with_budget()` and `auto_exact_request()` did not accept or propagate `download_root`, and the dataclass is frozen. No standard deployment could set it, so `approved_roots` was always `None` and the C2 containment defense was **dead code**. |
| C9 | LOW | `scripts/mcp_design_client.py:67-76` | A single malformed artifact returned `None`, surfacing downstream as a generic "no artifact object" rather than naming the missing field. |
| C10 | — | `scripts/handoff_validator.py:31` | Found while writing the C8 end-to-end test: `codex-blender`'s adapter emits `producer_version: "0.3.0"` (verified at `../codex-blender-plugin/scripts/dreamina_adapter.py:32`) but the accepted range stopped at `0.2.99`. **Every real current receipt would be rejected.** |

C10 is the most consequential finding of the review: it is a live cross-plugin
contract break that the offline suite could not see, because every fixture used
an older version string.

## Disposition — round 2

| Finding | Fix | Commit |
|---|---|---|
| C8 | Both factories take `download_root`; `PolicyDownloadRootTests` drives `run_until_blocked` end to end with a policy root and asserts an out-of-root artifact yields `FINAL_ARTIFACT_INVALID` and a `FAILED` state. | `c2d74c2` |
| C9 | `_artifact` raises a specific `McpToolError` naming the missing field. | `c2d74c2` |
| C10 | Range widened to `0.1.0`–`0.3.99`; `0.4.0` still refused; a drift-guard test reads the sibling manifest and asserts its version stays inside the accepted range. | `c2d74c2` |

## Round 3 — final verdicts over HEAD `c2d74c2`

**Code / security: `APPROVE`.** The reviewer verified C1–C7 as real and
sufficient, verified C8–C10 as correct, and explicitly re-checked path
traversal and symlink defenses, secret/privacy leakage, MCP envelope
normalization, paid submit-at-most-once, restart/query-only recovery, artifact
fail-closed acceptance, CI integrity, schema alignment, and release claims.
No remaining defect. Its single observation was that commit `c2d74c2`'s message
says 186 tests while the suite reports 188 — a cosmetic inaccuracy in the commit
message only, above the 150 floor either way.

**Architecture: `CLEAR`.** The auditor verified A1–A3 as resolved, accepted A4
with rationale, and confirmed no architectural, ownership, state-machine,
approval-boundary, gate-inflation, scope, reproducibility, release, or rollback
defect remains. It specifically checked that the new `download_root`
containment and the widened companion version range introduce no architectural
problem.

## Final verdict

```text
code_security = APPROVE
architecture  = CLEAR
combined      = APPROVE + CLEAR
```

`independent_review = APPROVE + CLEAR` — completion-gate line satisfied.

### Rationale for accepting A4 (ubuntu-latest CI)

CI exercises only deterministic, platform-independent gates: distribution
validation, the state machine, the dispatcher, the strict gate (companion
validators, TRACE, disposable install parity, the full suite) and whitespace
checks. None of these need Blender or macOS. The actual Blender/macOS runtime
acceptance is a separate, documented, human-driven step recorded in
[`production-e2e-2026-09-14.md`](./production-e2e-2026-09-14.md), and CI makes
no runtime claim. Accepted as an observation rather than a blocker.

## Reviewed-tree evidence

```text
strict gate        : 188 tests, 0 required skips, TRACE 6/6, version 0.3.0, parity true
distribution       : validated codex-dreamina-3d compatibility foundation 0.3.0
OpenAI validator   : Plugin validation passed
secret scan        : empty
absolute paths     : none in tracked non-doc files
git diff --check   : clean
```
