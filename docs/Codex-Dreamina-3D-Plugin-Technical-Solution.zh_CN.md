# Codex Dreamina 3D 插件技术方案

## 技术决策

实现回执驱动的编排插件，只通过稳定本地 JSON 契约和 Skill 能力发现联动，不导入伴随插件实现模块。

## 已实现目录

```text
.codex-plugin/plugin.json
skills/codex-dreamina-3d-use/
skills/codex-dreamina-3d-from-blender/
skills/codex-dreamina-3d-from-maya/
scripts/capability_probe.py
scripts/handoff_validator.py
schemas/3d_job.schema.json
tests/
```

## 作业状态

`Draft -> DccSelected -> PreviewSpecified -> PreviewValidated -> CapabilityResolved -> Quoted -> Approved -> Submitted -> Querying -> Completed|Failed|Unknown`。

每次迁移原子保存回执。`Unknown` 只能查询/对账。预览哈希、Prompt、模型、分辨率、比例、时长或参考输入变化后，报价和批准立即失效。

## Clean-room 实现

供应商行为只用于形成测试：相机渲染和本地视频、状态恢复、保持宽高比的分辨率、H.264 MP4 和协议限制。实现基于公开 DCC 与 Dreamina CLI 契约，不使用供应商 Python/JavaScript、UI 字符串、ffmpeg 二进制或 Bridge 协议。

## 测试

契约测试验证生产者兼容性和媒体回执；状态测试覆盖缺少伴随插件、过期预览、报价变化、重复提交、超时、恢复和产物不一致。端到端测试使用 fake companion CLI；真实 Blender/Maya/Dreamina 测试是独立授权门禁。
