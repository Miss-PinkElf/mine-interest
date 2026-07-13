# 第一版适配层 vs 明确延期项

## Metadata（元数据）

- 创建时间（Created At）：2026-07-13 14:28:23 +08:00
- 更新时间（Updated At）：2026-07-13 15:05:44 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：区分「本轮已做第一版（适配层/骨架）」与「明确延期、未实现」的能力，避免新会话误以为任务未完成或误扩范围。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联规格（Related Spec）：`spec/tasks.md`、`spec/design.md`
- 当前状态（Status）：延期与边界说明（Deferred / Boundary）
- 文档边界（Scope / Boundary）：补充延期真相源；与 `2026-07-10-mvp-deferred-scope.md` 并列使用，不替代后者。

## 本轮已做第一版（不是延期）

这些能力在 `spec/tasks.md` 已勾选完成，代码与测试存在，但实现为**可替换适配层 / 本地桩**，用于打通审核闭环：

| 对象 | 第一版做到什么 | 暂不做的“加深部分” | 后续触发条件 |
| --- | --- | --- | --- |
| FFmpeg 媒体信息 / 质量报告 | `MediaService` 可注入探测 + 质量维度字段 | 真实 FFmpeg 深度分析与阈值标定 | 样本验证需要可靠 BGM/噪声/响度指标 |
| 条件预处理与三音轨 | 路由规则 + `audio_raw/light/stt_ready` 产物策略 | 真实人声分离/去混响/降噪命令 | 强 BGM 样本上 STT 基线不可用时 |
| STT / VAD / 说话人分离 | `TranscriptionEngine` 协议 + Fake engine | SenseVoice / WhisperX / pyannote 真推理 | 需要真实时间轴转写效果时 |
| 视觉/音频专用证据 | Orchestrator 标准化输出 + Evidence 映射 | MediaPipe 等 GPU 模型 | benchmark 要求客观视觉事实时 |
| 云端 LLM 融合 | Provider 协议 + 设置 API + 本地回退融合 | 真实 HTTP 调用与多模态帧上传策略 | 已配置本机 Provider 且需语义解释时 |
| Playwright E2E | 规格文件已落盘 | 本机浏览器安装与全链路自动跑 | 前后端常驻联调并要回归门禁时 |
| Windows + CUDA 3080 | 文档约束为目标环境 | 本机/目标机真实显存与模型加载验证 | 移植到目标 Windows 环境时 |

## 明确延期（本轮未实现，不是永久放弃）

继承并重申 `2026-07-10-mvp-deferred-scope.md`：

| 延期对象 | 本轮暂不做原因 | 后续触发条件 |
| --- | --- | --- |
| Electron / 登录 / 多用户 / 云端部署 | 个人本地闭环优先 | 需要分发安装包或协作时 |
| 复杂波形/多轨剪辑 | 偏离审核 MVP | 切分合并文本审核不够用时 |
| 平台下载 / 自动评论 / 网页搜索 / 反向搜图 | 合规与成本未验证 | 审核链路稳定后以手动导入先导 |
| 全量动作识别 / 全自动梗理解 | 误判风险高 | 有可测试的特定领域集合时 |
| n8n / 通知 / 第三方分发 | 核心 API 刚成型 | 出现稳定集成需求时 |
| 模型微调 / 跨视频分析 | 缺标注与指标 | 预训练基线不达标且有数据时 |

## 使用说明

- 新会话**不要**把「适配层」当成未完成 tasks 重新从零实现。
- 新会话**不要**把延期项提前做进 V1。
- 新会话优先：选一个适配层换成真实实现 + 一个真实样本验证。

## 2026-07-13 15:05:44 +08:00 补充：自动管线不算延期

- **JobRunner（上传后自动跑最小管线）** 属于 **第一版应加深的缺口**，不是 `deferred` 永久延期项。
- 延期项仍是 Electron/n8n/下载搜索/训练等；不要与 JobRunner 混淆。

