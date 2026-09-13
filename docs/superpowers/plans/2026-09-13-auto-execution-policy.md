# Auto Execution Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute an approved Blender-preview-to-Dreamina workflow automatically within one budget envelope while preserving quote caps, at-most-once submission, and final artifact verification.

**Architecture:** Extend the existing `JobLedger` with an immutable execution-policy envelope and add an orchestration service that advances only legal states. It must compare the observed quote to the envelope before consuming the single submission authorization; polling, download, re-hash, and media probe proceed automatically after that one submission.

**Tech Stack:** Python 3, dataclasses, JSON Schema, unittest, existing Dreamina Design public interface.

**Spec:** `docs/superpowers/specs/2026-09-11-codex-dreamina-3d-plugin-design.md`

## Global Constraints

- No automatic second paid submission, including after timeout or failed query.
- An observed quote above the cap stops in `Quoted`; no approval is consumed.
- A platform-required web acknowledgement remains visible exactly once when applicable.
- All final artifacts require independent local hash and media validation before `Completed`.

---

### Task 1: Persist an immutable automatic-run envelope

**Files:**
- Modify: `scripts/job_ledger.py`
- Modify: `schemas/3d_job.schema.json`
- Test: `tests/test_job_ledger.py`

**Interfaces:**

```python
@dataclass(frozen=True)
class ExecutionPolicy:
    mode: Literal["interactive", "auto_with_budget", "review_only"]
    max_charge: Decimal | None
    permit_one_submission: bool
    permit_reference_upload: bool

def new_job(job_id: str, execution_policy: ExecutionPolicy | None = None) -> dict: ...
```

- [ ] **Step 1: Write failing ledger tests**

```python
def test_auto_policy_rejects_quote_above_budget():
    ledger = new_policy_ledger(max_charge="3.20")
    with self.assertRaises(BudgetExceededError):
        ledger.record_quote(Decimal("3.21"))
```

- [ ] **Step 2: Run the focused test and verify failure**

Run: `python3 -m unittest tests.test_job_ledger -v`

- [ ] **Step 3: Implement envelope parsing and schema validation**

Store only non-secret policy fields. Reject malformed money, negative caps, automatic mode without one-submission permission, and attempts to change the envelope after quote creation.

- [ ] **Step 4: Run focused tests**

Run: `python3 -m unittest tests.test_job_ledger -v`

### Task 2: Add automatic orchestration gates

**Files:**
- Create: `scripts/auto_orchestrator.py`
- Modify: `scripts/design_handoff.py`
- Test: `tests/test_auto_orchestrator.py`

**Interfaces:**

```python
def run_until_blocked(
    ledger: JobLedger,
    design_client: DesignClient,
    policy: ExecutionPolicy,
) -> dict: ...
```

- [ ] **Step 1: Write failing workflow tests**

Cover: below-cap quote submits once then completes; above-cap quote stops at `Quoted`; missing upload permission stops before submission; `Unknown` performs query only; final hash mismatch becomes `Failed`.

- [ ] **Step 2: Run the focused test and verify failure**

Run: `python3 -m unittest tests.test_auto_orchestrator -v`

- [ ] **Step 3: Implement legal ledger progression**

Use existing `design_handoff` and `handoff_validator` boundaries. Persist the first `design_submit_id` before polling. Do not call `submit` from `Submitted`, `Querying`, or `Unknown`.

- [ ] **Step 4: Run focused workflow tests**

Run: `python3 -m unittest tests.test_auto_orchestrator tests.test_design_handoff -v`

### Task 3: Update Skills and verification evidence

**Files:**
- Modify: `skills/codex-dreamina-3d-from-blender/SKILL.md`
- Modify: `skills/codex-dreamina-3d-resume/SKILL.md`
- Modify: `docs/verification/end-to-end.md`
- Test: `tests/test_skills.py`

- [ ] **Step 1: Write failing Skill assertions**

Assert `auto_with_budget` describes one envelope, automatic query/download, cap stop, and no resubmit.

- [ ] **Step 2: Run focused tests and verify failure**

Run: `python3 -m unittest tests.test_skills -v`

- [ ] **Step 3: Update routing language**

Document that interactive review remains available while automatic policy presents one final report and only exceptions interrupt the run.

- [ ] **Step 4: Run full validation**

Run: `python3 -m unittest discover -s tests -v && python3 scripts/validate_distribution.py && git diff --check`
