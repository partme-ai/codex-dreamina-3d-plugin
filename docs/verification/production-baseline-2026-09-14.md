# Production Baseline — 2026-09-14

## Dreamina 3D

- source/tracking/remote: `550da6ef69dcc2cbdafdd1c5b4a98896212e5808`
- version: `0.2.0`
- worktree before hardening: clean except this production plan
- installed selector: `codex-dreamina-3d@personal`
- installed version: `0.2.0`
- current Python 3.13 suite: 137 tests pass
- latest published CI: run `34749012596`, success with 11 skips

## Blender Dependency

- published source/tracking/remote at audit start: `caf835c`
- installed version: `codex-blender@personal 0.2.0`
- Blender: `5.2.1 LTS`
- official uploader enabled: no
- official Web runtime: `BLOCKED_MISSING_OFFICIAL_ADDON`
- checkout contains extensive unrelated in-progress changes; they are excluded
  from this baseline and must be reconciled before Task 5.

## Dreamina Design Dependency

- local HEAD at audit start: `00654f9`
- remote main at audit start: `897f6cb`
- installed version: `0.3.0`
- system-Python MCP initialize/tools-list: pass, 11 tools
- current local suite: 256 tests pass
- latest published CI at audit start: run `34773828367`, success

## Runtime Evidence Boundary

- real Blender preview and receipt re-hash: pass
- historical direct-CLI Seedance 2.5 canary: pass
- Dreamina 3D automatic orchestrator: missing
- real Dreamina 3D → Design MCP paid E2E: not run
- Maya runtime: not run
