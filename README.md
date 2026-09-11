# Codex Dreamina 3D Plugin

> Design-stage orchestration from Blender or Maya preview artifacts to Seedance 2.5.

[English](README.md) | [简体中文](README.zh-CN.md)

## Status and purpose

`codex-dreamina-3d` is a composition plugin, not a DCC implementation. It will detect `codex-blender` or `codex-maya`, request a validated preview MP4, enrich a Seedance prompt, obtain current Dreamina capabilities and quotation through `codex-dreamina-design`, require explicit approval, submit once, and recover by `submit_id`.

```text
Blender/Maya scene
  -> codex-blender or codex-maya
  -> validated preview receipt
  -> codex-dreamina-3d handoff
  -> codex-dreamina-design approval/submission/recovery
  -> validated Seedance artifact
```

## Boundaries

- No duplicated Blender, Maya, media, authentication, billing, or Dreamina CLI logic.
- No silent installation of companion plugins or DCC applications.
- No vendor uploader source, bundled ffmpeg, local browser bridge, or private API replication.
- Local preview completion and remote generation completion are separate gates.

## Documentation

- [Architecture](docs/Codex-Dreamina-3D-Plugin-Architecture.md) / [中文](docs/Codex-Dreamina-3D-Plugin-Architecture.zh_CN.md)
- [Technical solution](docs/Codex-Dreamina-3D-Plugin-Technical-Solution.md) / [中文](docs/Codex-Dreamina-3D-Plugin-Technical-Solution.zh_CN.md)
- [Design spec](docs/superpowers/specs/2026-09-11-codex-dreamina-3d-plugin-design.md)
- [Implementation plan](docs/superpowers/plans/2026-09-11-codex-dreamina-3d-plugin-implementation.md)

## Clean-room evidence

The official Blender 1.0.0 package was downloaded for behavior study only. Observed boundaries include camera render/local video modes, temporary setting restoration, H.264 MP4, protocol-driven limits, and a local web bridge. This project will implement an independent CLI-based handoff rather than copy that source or bridge.
