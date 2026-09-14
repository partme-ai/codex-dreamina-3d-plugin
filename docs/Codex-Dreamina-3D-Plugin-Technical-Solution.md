# Codex Dreamina 3D Plugin Technical Solution

> **Document control**
>
> | Field | Value |
> |---|---|
> | Status | Implemented; offline and fixture gates validated |
> | Scope | How the orchestration is built, integrated, and verified |
> | Audience | Implementers extending or reviewing this plugin |
> | Runtime evidence | `docs/verification/` |

## 1. Decision

Implement a receipt-driven orchestration plugin. Integrate only through stable local JSON contracts and Skill capability discovery; do not import companion implementation modules.

### Alternatives considered

| Alternative | Why it was rejected |
|---|---|
| Import companion Python modules directly | Couples the plugins at module level, so any companion refactor breaks this one |
| Declare a hard cross-plugin dependency in the manifest | Codex manifests do not currently provide a dependable hard dependency contract |
| Reimplement the upload or generation step | Duplicates authentication, billing, and vendor behavior that already have owners |
| Auto-install a missing companion | Silently mutates the user's environment and can spend money without consent |
| Retry an ambiguous submission | Risks a second paid action with no way to prove which succeeded |

## 2. Implemented layout

```text
.codex-plugin/plugin.json
skills/codex-dreamina-3d-use/
skills/codex-dreamina-3d-from-blender/
skills/codex-dreamina-3d-from-maya/
scripts/capability_probe.py
scripts/handoff_validator.py
schemas/3d_job.schema.json
tests/
```

| Path | Responsibility |
|---|---|
| `scripts/capability_probe.py` | Discover compatible companion installations and versions |
| `scripts/dcc_handoff.py` | argv and JSON boundary with a DCC adapter |
| `scripts/design_handoff.py` | Boundary with the Design plugin; idempotent submission |
| `scripts/handoff_validator.py` | Receipt validation with typed failures |
| `scripts/auto_orchestrator.py` | Advance one job until completion or a real external gate |
| `scripts/job_ledger.py` | Atomic operation receipts keyed by `submit_id` |
| `skills/` (6) | Routing, per-source entry points, and recovery instructions |

## 3. Job state

`Draft -> DccSelected -> PreviewSpecified -> PreviewValidated -> CapabilityResolved -> Quoted -> Approved -> Submitted -> Querying -> Completed|Failed|Unknown`.

Every transition stores receipts atomically. `Unknown` may only query/reconcile. Any change to preview hash, prompt, model, resolution, ratio, duration, or reference inputs invalidates the quote and approval.

| State | Writer | Trigger |
|---|---|---|
| Draft | Ledger | A job exists |
| DccSelected | Ledger | A source plugin is chosen |
| PreviewSpecified | Ledger | Preview parameters are fixed |
| PreviewValidated | Handoff validator | The DCC receipt passes validation |
| CapabilityResolved | Capability probe | A compatible companion set is found |
| Quoted | Design handoff | A quote is obtained |
| Approved | Design plugin | The user approves that quote |
| Submitted | Design handoff | One submission occurs; `submit_id` is persisted |
| Querying | Design handoff | A non-terminal state is observed |
| Completed / Failed / Unknown | Ledger | Terminal or ambiguous outcome |

## 4. Configuration and integration surface

| Setting | Location | Notes |
|---|---|---|
| Companion discovery | Runtime probe | No manifest-level dependency is assumed |
| Operation ledger | Written by `scripts/job_ledger.py` | Atomic writes with a monotonic revision |
| Approval | Owned by `codex-dreamina-design` | This plugin waits rather than decides |
| Schemas | `schemas/3d_job.schema.json` | The receipt shape exchanged with companions |

## 5. Error model

| Type | Field | Meaning |
|---|---|---|
| `ValidatorError` | `.code` | A receipt failed a contract rule |
| `AdapterError` | `.status` | A companion call returned a typed failure |

Contract rules that raise a validator error: a missing required receipt field, a stale preview, a hash mismatch, unsupported media, and unconfirmed restoration. Every failure names the rule it violated so the caller can act without parsing prose.

## 6. Clean-room implementation

Observed vendor behavior informs tests: camera render and local-video paths, state restoration, aspect-preserving resolution, H.264 MP4, and protocol limits. The implementation uses the public DCC and Dreamina CLI contracts, not vendor Python/JavaScript, UI strings, binary ffmpeg, or bridge protocol.

## 7. Test strategy

Contract tests validate producer compatibility and media receipts. State tests cover companion absence, stale preview, changed quote, duplicate submit, timeout, resume, and artifact mismatch. End-to-end tests use fake companion CLIs; real Blender/Maya/Dreamina tests are separate authorized gates.

| Layer | Proves | Command |
|---|---|---|
| Contract | Companion compatibility and receipt shape | `python3 -m unittest discover -s tests -v` |
| State | Companion absence, stale preview, changed quote, duplicate submit, timeout, resume, mismatch | same suite, state classes |
| End-to-end | Multi-step flow with fake companions | same suite, end-to-end classes |
| TRACE | Per-skill behavioural contract | `python3 scripts/trace_gate.py` |
| Strict gate | Everything above, plus distribution and trace | `python3 scripts/ci_gate.py --strict` |
| Local install | Marketplace registration behavior | `python3 scripts/local_install.py --verify` |

## 8. Compatibility and rollout

| Aspect | Position |
|---|---|
| Python | 3.13 |
| Companions | `codex-blender` and `codex-dreamina-design` at pinned, verified revisions |
| Routes | Blender, Jimeng Web, and automatic Seedance |
| Not-run surfaces | Maya runtime, the paid 3D-to-Design end-to-end path, and the official Web route (blocked until the uploader is installed) |

## 9. Evidence map

| Claim | Evidence |
|---|---|
| Companion discovery | `scripts/capability_probe.py` |
| Receipt validation rules | `scripts/handoff_validator.py` |
| Idempotent submission | `scripts/design_handoff.py` and `scripts/job_ledger.py` |
| Offline scope | `docs/verification/offline.md` |
| Runtime records | `docs/verification/end-to-end.md`, `docs/verification/maya-path.md` |
