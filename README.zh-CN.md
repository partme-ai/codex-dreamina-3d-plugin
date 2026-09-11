# Codex Dreamina 3D 插件

<img src="assets/logo.png" alt="Dreamina 3D Logo" width="128">

> 从 Blender/Maya 预览产物到 Dreamina 3D 的 Codex 编排兼容基础。

[English](README.md) | [简体中文](README.zh-CN.md)

## 状态与定位

`codex-dreamina-3d` 现已具备经过验证的兼容 manifest、Marketplace 元数据、品牌资产、Legal 文档、测试和实施目录。它仍是组合插件而不是 DCC 实现；跨插件交接工作流尚未实现。

## 许可证

Apache-2.0，见 [LICENSE](LICENSE)。

```text
Blender/Maya 场景
  -> codex-blender 或 codex-maya
  -> 已验证预览回执
  -> codex-dreamina-3d 交接
  -> codex-dreamina-design 批准/提交/恢复
  -> 已验证 Seedance 产物
```

## 边界

- 不重复实现 Blender、Maya、媒体、认证、计费或 Dreamina CLI 逻辑。
- 不静默安装伴随插件或 DCC 软件。
- 不复制供应商上传器、不捆绑 ffmpeg、不仿制本地浏览器 Bridge 或私有 API。
- 本地预览完成和远程生成完成是两个独立门禁。

## 文档

- [Architecture](docs/Codex-Dreamina-3D-Plugin-Architecture.md) / [中文](docs/Codex-Dreamina-3D-Plugin-Architecture.zh_CN.md)
- [Technical solution](docs/Codex-Dreamina-3D-Plugin-Technical-Solution.md) / [中文](docs/Codex-Dreamina-3D-Plugin-Technical-Solution.zh_CN.md)
- [设计规格](docs/superpowers/specs/2026-09-11-codex-dreamina-3d-plugin-design.md)
- [实施计划](docs/superpowers/plans/2026-09-11-codex-dreamina-3d-plugin-implementation.md)

## Clean-room 证据

官方 Blender 1.0.0 包仅用于行为研究。观察到相机渲染/本地视频、临时设置恢复、H.264 MP4、协议限制和本地 Web Bridge。本项目会独立实现 CLI 交接，不复制源码或 Bridge。
