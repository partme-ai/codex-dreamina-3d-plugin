# Codex Dreamina 3D Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build receipt-driven Blender/Maya to Seedance 2.5 orchestration for Codex.

**Architecture:** Runtime capability discovery selects a DCC companion. A handoff validator and end-to-end ledger coordinate the companion artifact with `codex-dreamina-design` without sharing implementation internals.

**Tech Stack:** Codex plugin, Agent Skills, Python, JSON Schema, unittest/pytest.

**Spec:** `docs/superpowers/specs/2026-09-11-codex-dreamina-3d-plugin-design.md`

## Constraints

- ID `codex-dreamina-3d`.
- Companion plugins are runtime-discovered, never silently installed.
- Receipt/hash validation precedes capability discovery or quotation.
- Paid submission is delegated and at-most-once.
- Vendor code and bridge protocols are excluded.

### Task 1: Shared contract conformance
- [ ] Write failing tests using planned Blender/Maya ArtifactReceipt fixtures.
- [ ] Define `3d_job` and compatibility schemas plus handoff validator.
- [ ] Reject stale/hash-mismatched/unrestored artifacts; commit `feat: define Dreamina 3D handoff`.

### Task 2: Companion capability discovery
- [ ] Write failing tests for none/one/both/incompatible companions.
- [ ] Implement deterministic selection and explicit user choice for ambiguity.
- [ ] Prove no installation side effect; commit `feat: discover 3D companion plugins`.

### Task 3: End-to-end job ledger
- [ ] Write failing transition, atomicity, restart and corrupted-ledger tests.
- [ ] Implement the specified state machine and receipt references without secrets.
- [ ] Prove invalid transitions fail closed; commit `feat: persist Dreamina 3D jobs`.

### Task 4: Design-plugin handoff
- [ ] Write failing tests for capability resolution, quote binding, changed inputs, submit-once and unknown results.
- [ ] Implement only the public receipt interface to `codex-dreamina-design`.
- [ ] Prove timeout queries instead of resubmits; commit `feat: orchestrate Seedance generation`.

### Task 5: Agent Skills
- [ ] Baseline no-skill scenarios for silent installs, stale previews, and paid retries.
- [ ] Create and individually validate use/from-blender/from-maya/resume Skills.
- [ ] Run TRACE and forward scenarios; commit `feat: add Dreamina 3D workflows`.

### Task 6: Distribution and cross-plugin acceptance
- [ ] Add failing identity/marketplace/link/secret/contract-version tests.
- [ ] Implement validator and public marketplace entry.
- [ ] Run fake-companion E2E tests and validate all three plugin packages.
- [ ] Record real Blender, Maya, and paid Dreamina gates separately; commit `test: verify Dreamina 3D distribution`.
