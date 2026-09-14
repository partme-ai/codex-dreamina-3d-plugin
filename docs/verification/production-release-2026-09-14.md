# Dreamina 3D 0.3.0 Production Release Evidence

Plan: [`docs/superpowers/plans/2026-09-14-production-release-handoff.md`](../superpowers/plans/2026-09-14-production-release-handoff.md) Tasks 2–6.
Canonical plan: [`docs/superpowers/plans/2026-09-14-production-readiness.md`](../superpowers/plans/2026-09-14-production-readiness.md).

This record contains no account identifiers, credentials, prompt text, signed
URLs, loopback tokens, or local private paths.

## Release identity

| Field | Value |
|---|---|
| Plugin | `codex-dreamina-3d` |
| Version | `0.3.0` |
| Skill inventory | 6 (`use`, `from-blender`, `from-maya`, `jimeng-web`, `auto-seedance`, `resume`) |
| Release scope | macOS + Blender 5.2.1 LTS |

## Task 2 — Local release gates

| Gate | Result | Evidence |
|---|---|---|
| Public version | `0.3.0` | `.codex-plugin/plugin.json` |
| Pinned companion SHAs present in CI | PASS | `e2f6f0252f55dd99c384dd1710ebbede1c1bcd7e`, `06d1fc5dc97744bb0482fbb8088af564e0eec27c` |
| Strict gate | PASS | 188 tests, 0 required skips, TRACE 6/6, version 0.3.0, parity true |
| Distribution validator | PASS | `validated codex-dreamina-3d compatibility foundation 0.3.0` |
| OpenAI plugin validator | PASS | `Plugin validation passed` |
| Secret scan | PASS | empty |
| Absolute private paths in tracked non-doc files | PASS | empty |
| Link audit | PASS | 30 checked / 0 broken |
| Whitespace | PASS | `git diff --check` clean |

### Gate history across the review rounds

| Revision | Tests | TRACE | Version | Parity |
|---|---|---|---|---|
| Before review | 164 | 6/6 | 0.3.0 | true |
| After round 1 fixes (`a3bae9d`) | 179 | 6/6 | 0.3.0 | true |
| After round 2 fixes (`c2d74c2`) | 188 | 6/6 | 0.3.0 | true |

## Task 3 — Push and exact-SHA CI

| Gate | Result |
|---|---|
| Release SHA pushed | _recorded below after push_ |
| Local HEAD == tracking == `git ls-remote origin refs/heads/main` | _recorded below_ |
| GitHub Actions run for the exact SHA | _recorded below_ |
| CI log shows 188 tests, 0 required skips, TRACE 6/6, version 0.3.0, parity true | _recorded below_ |

## Task 4 — Public Marketplace installation

| Gate | Result |
|---|---|
| Marketplace upgraded | _recorded below_ |
| Plugin reports `installed, enabled` at `0.3.0` | _recorded below_ |
| Source/installed parity (manifest, marketplace, `skills/`, `schemas/`, `scripts/`) | _recorded below_ |
| Installed read-only entry points import/compile | _recorded below_ |

## Task 5 — Fresh Codex task discovery and read-only smoke

| Gate | Result |
|---|---|
| Fresh Codex task (not this conversation) | _recorded below_ |
| Skill discovery: `use`, `from-blender`, `jimeng-web`, `auto-seedance`, `resume` | _recorded below_ |
| Dreamina Design MCP initializes at 0.3.0 | _recorded below_ |
| Blender 0.3.0 public `bin/blender_adapter --help` | _recorded below_ |
| Official uploader probed without installing or enabling | _recorded below_ |
| Router reports `jimeng_web=OPTIONAL_UNAVAILABLE` when the add-on is absent | _recorded below_ |

## Task 6 — Completion gate

| Gate line | Status |
|---|---|
| `release_scope = blender_macos_only` | PASS |
| `artifact_acceptance = FAIL_CLOSED` | PASS |
| `auto_orchestrator = PASS` | PASS |
| `mcp_design_binding = PASS` | PASS |
| `submit_at_most_once = PASS` | PASS |
| `restart_query_only = PASS` | PASS |
| `official_web_security = PASS` | PASS |
| `official_web_runtime = PASS or OPTIONAL_UNAVAILABLE` | OPTIONAL_UNAVAILABLE |
| `ci_required_skips = 0` | PASS |
| `local_blender_runtime = PASS` | PASS (recorded 2026-09-14) |
| `dreamina_mcp_read_only = PASS` | PASS (recorded 2026-09-14) |
| `dreamina_mcp_native_deny = PASS` | PASS (recorded 2026-09-14) |
| `dreamina_mcp_paid_canary = separately approved PASS` | PASS (separately approved) |
| `final_artifact_hash = PASS` | PASS |
| `independent_review = APPROVE + CLEAR` | PASS |
| `remote_ci_exact_sha = PASS` | _pending CI_ |
| `public_marketplace_version = 0.3.0` | _pending marketplace refresh_ |
| `source_cache_parity = PASS` | _pending marketplace refresh_ |
| `maya_claim = EXCLUDED` | EXCLUDED |
| `windows_claim = EXCLUDED` | EXCLUDED |

## Accepted limitations

- **Maya** remains implemented as an experimental fixture path with runtime
  status `NOT_RUN`. Its Skill frontmatter declares `status: experimental`, and
  the manifest carries no Maya claim. Outside the release scope.
- **Windows** is outside the release scope.
- **`jimeng_web`** is `OPTIONAL_UNAVAILABLE` while the user-installed official
  uploader is absent. The router reports this honestly and a Jimeng Web link
  terminates at `JimengLinkReady`, never at Seedance `Completed`.
- **CI runs on `ubuntu-latest`.** Accepted: CI exercises only deterministic,
  platform-independent gates, and the Blender/macOS runtime acceptance is the
  separate documented step above. CI makes no runtime claim.
