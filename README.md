# Codex Dreamina 3D Plugin

<img src="assets/logo.png" alt="Dreamina 3D logo" width="128">

> Compatibility foundation for Blender/Maya-to-Dreamina 3D orchestration.

[English](README.md) | [简体中文](README.zh-CN.md)

## Status and purpose

`codex-dreamina-3d` is a receipt-driven composition plugin rather than a DCC implementation. Its Blender/Maya companion discovery, preview validation, resumable job ledger, Dreamina Design handoff, fixture end-to-end workflows, distribution checks, and Agent Skills are implemented and validated offline. The real Blender 5.2.1 preview and receipt handoff pass; Maya and paid Seedance runtime acceptance remain separate, explicitly authorized gates.

## License

Apache-2.0 — see [LICENSE](LICENSE).

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

The official Blender 1.0.0 package was downloaded for behavior study only. Observed boundaries include camera render/local video modes, temporary setting restoration, H.264 MP4, protocol-driven limits, and a local web bridge. This orchestrator uses the independent `codex-blender` CLI receipt contract rather than copying that source or bridge.
