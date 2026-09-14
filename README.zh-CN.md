# Codex Dreamina 3D 插件

![Codex × Dreamina 3D — 将已验证场景转化为电影级 3D](assets/dreamina-3d-hero.png)

<img src="assets/logo.png" alt="Dreamina 3D Logo" width="128">

> 面向生产的 Blender 到 Dreamina 3D 编排插件。

[English](README.md) | [简体中文](README.zh-CN.md)

## 状态与版本

`codex-dreamina-3d` 是回执驱动的组合插件，而不是 DCC 实现。当前生产范围为 macOS、Blender 5.2.1 LTS 与 Dreamina Design MCP。Blender 预览验证、可恢复状态、三入口路由和真实 Seedance canary 分别保留证据。Maya 仅保留实验性夹具兼容，运行状态为 `NOT_RUN`。

## 快速开始

```bash
codex plugin marketplace add partme-ai/codex-dreamina-3d-plugin --ref main
codex plugin add codex-dreamina-3d@partme-ai-dreamina-3d
```

重启 Codex 或 ChatGPT 桌面应用，新建任务，让 Codex 把已验证的 Blender 预览转交给 Dreamina 3D。插件只负责传递配方，并在提交上游 CLI 前等待你明确批准。

## 可以做什么

`codex-dreamina-3d` 通过固定的三步路由，把已验证的 Blender 预览编排成 Dreamina 3D 产物。

```text
Blender 场景
  -> codex-blender
  -> 已验证预览回执
  -> codex-dreamina-3d 交接
  -> codex-dreamina-design 批准/提交/恢复
  -> 已验证 Seedance 产物
```

插件不重复实现 Blender、上游上传器或 Dreamina CLI；只持有路由契约与每一步的回执校验。

## 边界与契约

- 不重复实现 Blender、媒体、认证、计费或 Dreamina CLI 逻辑。
- 不静默安装伴随插件或 DCC 软件。
- 不复制供应商上传器、不捆绑 ffmpeg、不仿制本地浏览器 Bridge 或私有 API。
- 本地预览完成和远程生成完成是两个独立门禁。

### 实验性兼容

仓库保留 Maya 回执夹具和实验 Skill，用于契约演进；当前不对外声明或验收 Maya 生产运行能力。

## 文档导航

- [Architecture](docs/Codex-Dreamina-3D-Plugin-Architecture.md) · [架构文档](docs/Codex-Dreamina-3D-Plugin-Architecture.zh_CN.md)
- [Technical solution](docs/Codex-Dreamina-3D-Plugin-Technical-Solution.md) · [技术方案](docs/Codex-Dreamina-3D-Plugin-Technical-Solution.zh_CN.md)
- [设计规格](docs/superpowers/specs/2026-09-11-codex-dreamina-3d-plugin-design.md)
- [实施计划](docs/superpowers/plans/2026-09-11-codex-dreamina-3d-plugin-implementation.md)

### Clean-room 证据

官方 Blender 1.0.0 包仅用于行为研究。观察到相机渲染/本地视频、临时设置恢复、H.264 MP4、协议限制和本地 Web Bridge。本编排器使用独立的 `codex-blender` CLI 回执契约，不复制该源码或 Bridge。

## 许可证

Apache-2.0，见 [LICENSE](LICENSE)。
