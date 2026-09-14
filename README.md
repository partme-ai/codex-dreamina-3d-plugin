# Codex Dreamina 3D Plugin

![Codex × Dreamina 3D — Turn validated scenes into cinematic 3D](assets/dreamina-3d-hero.png)

<img src="assets/logo.png" alt="Dreamina 3D logo" width="128">

> Production-oriented Blender-to-Dreamina 3D orchestration.

[English](README.md) | [简体中文](README.zh-CN.md)

## Status and version

`codex-dreamina-3d` is a receipt-driven composition plugin rather than a DCC implementation. The production scope is macOS with Blender 5.2.1 LTS and Dreamina Design MCP. Blender preview validation, resumable state, three-entry routing, and a real Seedance canary are verified separately. Maya remains an experimental fixture-compatible path with runtime status `NOT_RUN`.

## Quick start

```bash
codex plugin marketplace add partme-ai/codex-dreamina-3d-plugin --ref main
codex plugin add codex-dreamina-3d@partme-ai-dreamina-3d
```

Restart Codex or the ChatGPT desktop app, open a new task, and ask Codex to convert a validated Blender preview into a Dreamina 3D submission. The plugin hands off the recipe and waits for explicit user approval before submitting to the upstream CLI.

## What you can build

`codex-dreamina-3d` orchestrates a verified Blender preview into a Dreamina 3D artifact through a fixed three-step routing.

```text
Blender scene
  -> codex-blender
  -> validated preview receipt
  -> codex-dreamina-3d handoff
  -> codex-dreamina-design approval/submission/recovery
  -> validated Seedance artifact
```

The plugin never reimplements Blender, the upstream uploader, or the Dreamina CLI. It only owns the routing contract and the receipt validation that gates each step.

## Boundaries and contracts

- No duplicated Blender, media, authentication, billing, or Dreamina CLI logic.
- No silent installation of companion plugins or DCC applications.
- No vendor uploader source, bundled ffmpeg, local browser bridge, or private API replication.
- Local preview completion and remote generation completion are separate gates.

### Experimental compatibility

The repository retains a Maya receipt fixture and experimental Skill for contract evolution. Maya is not advertised or accepted as a production runtime.

## Documentation

- [Architecture](docs/Codex-Dreamina-3D-Plugin-Architecture.md) · [架构文档](docs/Codex-Dreamina-3D-Plugin-Architecture.zh_CN.md)
- [Technical solution](docs/Codex-Dreamina-3D-Plugin-Technical-Solution.md) · [技术方案](docs/Codex-Dreamina-3D-Plugin-Technical-Solution.zh_CN.md)
- [Design spec](docs/superpowers/specs/2026-09-11-codex-dreamina-3d-plugin-design.md)
- [Implementation plan](docs/superpowers/plans/2026-09-11-codex-dreamina-3d-plugin-implementation.md)
- [Clean-room evidence](#clean-room-evidence) below.

### Clean-room evidence

The official Blender 1.0.0 package was downloaded for behavior study only. Observed boundaries include camera render/local video modes, temporary setting restoration, H.264 MP4, protocol-driven limits, and a local web bridge. This orchestrator uses the independent `codex-blender` CLI receipt contract rather than copying that source or bridge.

## License

Apache-2.0 — see [LICENSE](LICENSE).
