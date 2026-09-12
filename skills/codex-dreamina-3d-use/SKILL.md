---
name: codex-dreamina-3d-use
description: Route a Dreamina 3D orchestration request to the right workflow. Use when the user wants to turn a DCC preview into a Dreamina render without naming the source DCC.
metadata:
  type: router
  plugin: codex-dreamina-3d
  status: stable
---

# codex-dreamina-3d-use

## When to use

The user wants a Dreamina 3D render but has not specified whether the source
preview comes from Blender or Maya. This Skill routes to the right workflow.

## Workflow

1. **Discover companions.** Call `discover_companions(search_roots)` from
   `scripts/capability_probe.py`. Do not crawl user directories and do not
   install anything.
2. **Choose the companion.** Call `select_companion(candidates, requested=None)`.
   - zero companions: surface `install_guidance()` and stop.
   - one companion: route to `codex-dreamina-3d-from-{blender|maya}`.
   - two companions: ask the user to pick.
3. **Delegate** to the chosen companion Skill and stop.

## Never do

- Never install or modify a companion plugin.
- Never skip the companion detection step.
- Never proceed to Dreamina submission before the preview is validated.

## Gate signals

- Local preview status: `PreviewValidated` in the job ledger.
- Dreamina submission status: `Submitted | Querying | Unknown` in the ledger.
- Final artifact acceptance: `Completed` (only after `result.sha256` is on
  disk and matches the declared hash).