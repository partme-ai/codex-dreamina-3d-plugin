# Dreamina 3D Production Release Handoff Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Complete the remaining independent review, GitHub release verification, Marketplace refresh, and fresh-task smoke gates for `codex-dreamina-3d` 0.3.0 without making another paid Dreamina submission.

**Architecture:** The implementation is already complete across three repositories. This handoff treats the current committed SHAs as review inputs, uses `codex-dreamina-3d` as the release repository, and validates Blender and Dreamina Design only through their published plugin contracts. Review, remote CI, installed cache, and fresh-task discovery remain separate evidence gates.

**Tech Stack:** Python 3.13, unittest, GitHub Actions, Codex plugin Marketplace, Dreamina Design MCP, Blender 5.2.1 LTS.

**Spec:** `docs/superpowers/plans/2026-09-14-production-readiness.md`

## Global Constraints

- Do not call `dreamina_submit_video`, `dreamina_submit_image`, or any other paid generation tool. The authorized canary is complete.
- Do not repeat submit ID `6fd79b95-9b02-4d05-a14d-801001cca136`; it may be queried read-only only if evidence must be reconfirmed.
- Release scope is macOS + Blender 5.2.1 LTS. Maya and Windows are excluded from Dreamina 3D release claims.
- `jimeng_web` is `OPTIONAL_UNAVAILABLE` while the user-installed official uploader is absent.
- Do not rewrite Git history, force-push, delete user data, or modify unrelated repositories.
- Do not claim release success until source HEAD, remote SHA, CI SHA, installed cache SHA/content, and version 0.3.0 all agree.

## Authoritative Starting State

| Repository | Required committed SHA | Status |
|---|---|---|
| `codex-blender-plugin` | `e2f6f0252f55dd99c384dd1710ebbede1c1bcd7e` | pushed; installed public cache refreshed and adapter entry passed |
| `codex-dreamina-design-plugin` | `06d1fc5dc97744bb0482fbb8088af564e0eec27c` | pushed; query polling compatibility fix included |
| `codex-dreamina-3d-plugin` | start review at `550da6ef69dcc2cbdafdd1c5b4a98896212e5808`, candidate currently `bbb3862f23db024b26774ebd8e6d8772b0393736` plus this plan document | local main; release not yet pushed |

Runtime evidence already accepted:

- Blender preview SHA-256: `b8b5b7607d29b4ac02da83117078b491badd22e0a81e995aa09c0402e18847bb`.
- Seedance submit ID: `6fd79b95-9b02-4d05-a14d-801001cca136`.
- Task-attributed cost: 54 credits.
- Final artifact SHA-256: `fa7b542c404bda2bfc2facbc2eecd79f028d6e91e08c6ab09fda18fa615335e0`.
- Strict local gate: 164 tests, zero required skips, TRACE 6/6.

---

### Task 1: Independent two-lane release review

**Files:**
- Read: `docs/superpowers/plans/2026-09-14-production-readiness.md`
- Read: `docs/verification/production-e2e-2026-09-14.md`
- Review: Git diff `550da6ef69dcc2cbdafdd1c5b4a98896212e5808..HEAD`
- Create: `docs/verification/production-review-2026-09-14.md`

**Interfaces:**
- Consumes: exact release diff and production acceptance plan.
- Produces: code/security verdict `APPROVE|REQUEST_CHANGES` and architecture verdict `CLEAR|BLOCK`.

- [x] **Step 1: Dispatch a clean-context code/security reviewer**

Prompt exactly:

```text
Review repository /Users/wandl/workspaces/workspace-partme-ai/codex-dreamina-3d-plugin read-only.
Review diff 550da6ef69dcc2cbdafdd1c5b4a98896212e5808..HEAD against docs/superpowers/plans/2026-09-14-production-readiness.md.
Check correctness, path traversal and symlink defenses, secret/privacy leakage, MCP envelope normalization, paid submit-at-most-once, restart/query-only recovery, artifact fail-closed acceptance, CI integrity, and release claims.
Do not modify files or call paid/external mutation tools.
Return findings by severity with exact file:line. End with exactly APPROVE or REQUEST_CHANGES.
```

- [x] **Step 2: Dispatch a separate clean-context architecture reviewer**

Prompt exactly:

```text
Audit repository /Users/wandl/workspaces/workspace-partme-ai/codex-dreamina-3d-plugin read-only.
Evaluate diff 550da6ef69dcc2cbdafdd1c5b4a98896212e5808..HEAD and docs/superpowers/plans/2026-09-14-production-readiness.md.
Verify cross-plugin ownership, durable state transitions, approval boundaries, no gate inflation, Blender-only macOS scope, optional Jimeng Web behavior, CI reproducibility, release and rollback readiness.
Do not modify files or call paid/external mutation tools.
Return exact evidence and blockers. End with exactly CLEAR or BLOCK.
```

- [x] **Step 3: Stop on a negative or missing verdict**

Do not proceed if either review is absent, the code verdict is `REQUEST_CHANGES`, or the architecture verdict is `BLOCK`. Send findings to an implementer, rerun affected tests, and repeat both reviews over the new HEAD.

- [x] **Step 4: Record both raw verdicts and exact reviewed HEAD**

Create `docs/verification/production-review-2026-09-14.md` containing reviewer identity/type, reviewed base SHA, reviewed HEAD SHA, findings, dispositions, and final `APPROVE + CLEAR`. Do not summarize a conditional verdict as approval.

---

### Task 2: Final local release gates and release commit

**Files:**
- Modify: `docs/superpowers/plans/2026-09-14-production-readiness.md`
- Create: `docs/verification/production-release-2026-09-14.md`

**Interfaces:**
- Consumes: `APPROVE + CLEAR` review evidence.
- Produces: one clean 0.3.0 release commit.

- [x] **Step 1: Verify the public version and pinned companions**

Run:

```bash
python3 -c 'import json; print(json.load(open(".codex-plugin/plugin.json"))["version"])'
rg -n 'ref: (e2f6f0252f55dd99c384dd1710ebbede1c1bcd7e|06d1fc5dc97744bb0482fbb8088af564e0eec27c)' .github/workflows/ci.yml
```

Expected: version `0.3.0` and both exact companion SHAs.

- [x] **Step 2: Run the strict gate**

Run:

```bash
/usr/local/bin/python3 scripts/ci_gate.py --strict
```

Expected: `tests_run=164`, `required_skips=0`, `trace=6/6`, `version=0.3.0`, `parity=true`.

- [x] **Step 3: Run distribution, secret, link, and whitespace gates**

Run:

```bash
/usr/local/bin/python3 scripts/validate_distribution.py .
git diff --check
git grep -n -E 'BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY|AIza[0-9A-Za-z_-]{30,}|sk-[A-Za-z0-9]{20,}' -- . ':!docs/verification/*'
```

Expected: validator passes, whitespace check is empty, secret scan is empty. Validate every relative Markdown link in `README*.md`, `docs/**/*.md`, and `skills/**/*.md`; missing-link count must be zero.

- [x] **Step 4: Update the canonical plan truthfully**

Mark Task 8 Steps 1–3 complete only after the above evidence exists. Leave Steps 4–8 unchecked until their respective remote/install/smoke evidence exists.

- [x] **Step 5: Commit the review and release evidence**

```bash
git add docs/superpowers/plans/2026-09-14-production-readiness.md docs/superpowers/plans/2026-09-14-production-release-handoff.md docs/verification/production-review-2026-09-14.md docs/verification/production-release-2026-09-14.md
git commit -m "release: certify Dreamina 3D 0.3.0"
```

---

### Task 3: Push and verify exact-SHA GitHub CI

**Files:**
- Modify after verification: `docs/verification/production-release-2026-09-14.md`

**Interfaces:**
- Consumes: clean local release commit.
- Produces: identical local/tracking/remote SHA and successful terminal CI for that SHA.

- [x] **Step 1: Push without history rewriting**

```bash
git push origin main
```

- [x] **Step 2: Prove SHA equality**

```bash
git rev-parse HEAD
git rev-parse origin/main
git ls-remote origin refs/heads/main
```

All three values must be identical. Record the full 40-character SHA.

- [x] **Step 3: Wait for CI on the exact SHA**

Use GitHub CLI or GitHub UI to identify the workflow run whose `headSha` equals the full release SHA. Wait until terminal status. Required result: `conclusion=success`. Do not cite an earlier run.

- [x] **Step 4: Confirm strict-gate evidence in CI logs**

The exact-SHA log must show 164 tests, zero required skips, TRACE 6/6, candidate version 0.3.0, and installed-candidate parity true. Any checkout failure for pinned companions is a release failure.

---

### Task 4: Refresh and compare the public Marketplace installation

**Files:**
- Modify after verification: `docs/verification/production-release-2026-09-14.md`

**Interfaces:**
- Consumes: successful exact-SHA CI.
- Produces: public installed cache for 0.3.0 with byte-identical release content.

- [x] **Step 1: Upgrade the public marketplace and plugin**

```bash
codex plugin marketplace upgrade partme-ai-dreamina-3d
codex plugin add codex-dreamina-3d@partme-ai-dreamina-3d
codex plugin list
```

If the marketplace name differs, resolve the existing configured public marketplace with `codex plugin marketplace list`; do not silently substitute `personal`.

- [x] **Step 2: Verify installed identity**

The listed plugin must be `installed, enabled`, version `0.3.0`, and source the public GitHub marketplace rather than the local checkout.

- [x] **Step 3: Compare source and installed content**

Compare `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `skills/`, `schemas/`, and `scripts/` recursively by relative path and SHA-256. Exclude only `.git`, `__pycache__`, and `*.pyc`. Required result: no missing, extra, or mismatched production file.

- [x] **Step 4: Verify installed read-only entry points**

Run the installed distribution validator and import/compile smoke for `auto_orchestrator.py`, `mcp_design_client.py`, `job_ledger.py`, and `handoff_validator.py`. Do not invoke a paid Dreamina tool.

---

### Task 5: Fresh Codex task discovery and read-only smoke

**Files:**
- Modify after verification: `docs/verification/production-release-2026-09-14.md`

**Interfaces:**
- Consumes: refreshed public installed plugin.
- Produces: clean-session proof that end users see the intended entry points.

- [x] **Step 1: Start a genuinely fresh Codex task**

Do not reuse this conversation or an already loaded plugin snapshot.

- [x] **Step 2: Verify Skill discovery**

Confirm discovery of:

```text
codex-dreamina-3d-use
codex-dreamina-3d-from-blender
codex-dreamina-3d-jimeng-web
codex-dreamina-3d-auto-seedance
codex-dreamina-3d-resume
```

Maya may remain installed as an experimental Skill but must not be advertised as production-ready.

- [x] **Step 3: Run read-only capability smoke**

Verify Dreamina Design MCP initializes at 0.3.0; call only `dreamina_cli_status` and `dreamina_account`. Confirm Blender 0.3.0 public `bin/blender_adapter --help` succeeds. Probe the official uploader without installing or enabling it.

- [x] **Step 4: Verify honest routing output**

The router must expose `preview_only`, `auto_seedance`, and `jimeng_web`; it must report `jimeng_web=OPTIONAL_UNAVAILABLE` when the official add-on is absent. It must not treat `JimengLinkReady` as `Completed` and must not initiate generation during smoke testing.

---

### Task 6: Final production verdict

**Files:**
- Modify: `docs/superpowers/plans/2026-09-14-production-readiness.md`
- Modify: `docs/verification/production-release-2026-09-14.md`

**Interfaces:**
- Consumes: review, local, remote CI, installed-cache, and fresh-task evidence.
- Produces: auditable production-ready verdict.

- [x] **Step 1: Complete the release evidence table**

Record exact SHAs, CI run URL/ID and conclusion, marketplace name/version/cache SHA, file parity counts, fresh-task ID, read-only MCP results, Blender adapter result, and optional Web status. Do not record account IDs, credentials, prompt text, signed video URLs, loopback tokens, or local private paths.

- [x] **Step 2: Check the completion gate line by line**

Every line in the canonical plan's `Completion Gate` must be `PASS`, `EXCLUDED`, or the explicitly permitted `OPTIONAL_UNAVAILABLE`. `independent_review` must be `APPROVE + CLEAR`, `remote_ci_exact_sha` must be `PASS`, and `public_marketplace_version` must be `0.3.0`.

- [x] **Step 3: Mark Task 8 complete and commit evidence**

```bash
git add docs/superpowers/plans/2026-09-14-production-readiness.md docs/verification/production-release-2026-09-14.md
git commit -m "docs: record Dreamina 3D 0.3.0 production release"
git push origin main
```

Because this evidence commit changes HEAD, wait for CI on the new exact SHA and refresh/compare the public Marketplace cache again before issuing the final verdict.

- [x] **Step 4: Final response contract**

Report production-ready only for `preview_only` and `auto_seedance` on macOS/Blender. Report `jimeng_web` as optional unavailable until the official add-on is installed. Explicitly exclude Maya and Windows. Include the final GitHub SHA, CI run, Marketplace version, parity result, and final artifact SHA-256.
