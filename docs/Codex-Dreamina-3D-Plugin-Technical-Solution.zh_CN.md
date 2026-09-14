# Codex Dreamina 3D 插件技术方案

> **文档信息**
>
> | 字段 | 值 |
> |---|---|
> | 状态 | 已实现；离线与夹具门禁已验证 |
> | 范围 | 编排如何构建、如何集成、如何验证 |
> | 读者 | 扩展或评审本插件的实现者 |
> | 运行证据 | `docs/verification/` |

## 1. 技术决策

实现一个回执驱动的编排插件。只通过稳定的本机 JSON 契约与 Skill 能力发现做集成；不导入伴随插件的实现模块。

### 备选方案

| 备选方案 | 被否的原因 |
|---|---|
| 直接导入伴随插件的 Python 模块 | 在模块层耦合，任何一次伴随插件重构都会打断本插件 |
| 在清单里声明硬跨插件依赖 | Codex 清单目前不提供可靠的硬依赖契约 |
| 重实现上传或生成步骤 | 会重复认证、计费与供应商行为，而这些都已有归属 |
| 自动安装缺失的伴随插件 | 静默改动用户环境，且可能未经同意就花钱 |
| 重试结果含糊的提交 | 有第二次付费动作的风险，且无法证明哪次成功 |

## 2. 已实现的布局

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

| 路径 | 职责 |
|---|---|
| `scripts/capability_probe.py` | 发现兼容的伴随插件安装与版本 |
| `scripts/dcc_handoff.py` | 与 DCC 适配器的 argv 与 JSON 边界 |
| `scripts/design_handoff.py` | 与 Design 插件的边界；幂等提交 |
| `scripts/handoff_validator.py` | 带回执类型化失败的校验 |
| `scripts/auto_orchestrator.py` | 把单个任务推进到完成或真实外部门禁 |
| `scripts/job_ledger.py` | 以 `submit_id` 为键的原子操作回执 |
| `skills/`（6 个） | 路由、按来源的入口与恢复指令 |

## 3. 任务状态

`Draft -> DccSelected -> PreviewSpecified -> PreviewValidated -> CapabilityResolved -> Quoted -> Approved -> Submitted -> Querying -> Completed|Failed|Unknown`。

每次状态迁移都原子写入回执。`Unknown` 只能查询与核对。预览哈希、Prompt、模型、分辨率、比例、时长或参考输入的任何变化，都会让报价与批准失效。

| 状态 | 写入方 | 触发条件 |
|---|---|---|
| Draft | 台账 | 任务已存在 |
| DccSelected | 台账 | 已选定来源插件 |
| PreviewSpecified | 台账 | 预览参数已固定 |
| PreviewValidated | 交接校验器 | DCC 回执通过校验 |
| CapabilityResolved | 能力探测 | 找到兼容的伴随插件集合 |
| Quoted | Design 交接 | 取得报价 |
| Approved | Design 插件 | 用户批准该报价 |
| Submitted | Design 交接 | 发生一次提交；`submit_id` 已持久化 |
| Querying | Design 交接 | 观察到非终态 |
| Completed / Failed / Unknown | 台账 | 终态或含糊结果 |

## 4. 配置与集成面

| 设置 | 位置 | 说明 |
|---|---|---|
| 伴随插件发现 | 运行时探测 | 不假定清单级依赖 |
| 操作台账 | 由 `scripts/job_ledger.py` 写入 | 带单调 revision 的原子写 |
| 批准 | 由 `codex-dreamina-design` 持有 | 本插件等待，不做决策 |
| Schema | `schemas/3d_job.schema.json` | 与伴随插件交换的回执结构 |

## 5. 错误模型

| 类型 | 字段 | 含义 |
|---|---|---|
| `ValidatorError` | `.code` | 某份回执未通过契约规则 |
| `AdapterError` | `.status` | 伴随插件调用返回带类型的失败 |

会触发校验错误的契约规则：缺少必填回执字段、预览过期、哈希不匹配、媒体不受支持，以及还原未确认。每次失败都会点名它违反的规则，使调用方无需解析文字就能处理。

## 6. 洁净室实现

观察到的供应商行为用于指导测试：相机渲染与本地视频路径、状态还原、保持宽高比的分辨率、H.264 MP4 与协议限制。实现只使用公开的 DCC 与 Dreamina CLI 契约，不使用供应商 Python/JavaScript、UI 文案、二进制 ffmpeg 或桥协议。

## 7. 测试策略

契约测试校验生产方兼容性与媒体回执。状态测试覆盖伴随插件缺失、预览过期、报价变化、重复提交、超时、恢复与产物不匹配。端到端测试使用假伴随插件 CLI；真实 Blender/Maya/Dreamina 测试是单独的、需授权的门禁。

| 层次 | 证明 | 命令 |
|---|---|---|
| 契约 | 伴随插件兼容性与回执结构 | `python3 -m unittest discover -s tests -v` |
| 状态 | 伴随插件缺失、预览过期、报价变化、重复提交、超时、恢复、不匹配 | 同一套件中的状态类 |
| 端到端 | 使用假伴随插件的多步流程 | 同一套件中的端到端类 |
| TRACE | 逐 Skill 的行为契约 | `python3 scripts/trace_gate.py` |
| 严格门禁 | 以上全部，加上分发与 TRACE | `python3 scripts/ci_gate.py --strict` |
| 本地安装 | Marketplace 注册行为 | `python3 scripts/local_install.py --verify` |

## 8. 兼容性与上线

| 方面 | 立场 |
|---|---|
| Python | 3.13 |
| 伴随插件 | `codex-blender` 与 `codex-dreamina-design`，均固定到已验证版本 |
| 路由 | Blender、即梦网页与自动 Seedance |
| 未运行面 | Maya 运行期、付费的 3D 到 Design 端到端路径，以及官方网页路径（上传器未安装前保持阻塞） |

## 9. 证据映射

| 断言 | 证据 |
|---|---|
| 伴随插件发现 | `scripts/capability_probe.py` |
| 回执校验规则 | `scripts/handoff_validator.py` |
| 幂等提交 | `scripts/design_handoff.py` 与 `scripts/job_ledger.py` |
| 离线范围 | `docs/verification/offline.md` |
| 运行期记录 | `docs/verification/end-to-end.md`、`docs/verification/maya-path.md` |
