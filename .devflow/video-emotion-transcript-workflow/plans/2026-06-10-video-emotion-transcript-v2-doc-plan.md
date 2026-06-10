# 视频情感化转写候选文档 v2 完善 Plan

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 15:34:26 +08:00
- 更新时间（Updated At）：2026-06-10 15:34:26 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：规划对 `zzz-docs/设想/视频情感化转写可行性路线.md` 的 v2 完善，吸收本目录补充材料中的可借鉴点。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-docs/设想/prompt.md`
- 关联补充材料（Related References）：`zzz-docs/设想/STT-情感视频理解-可行性分析.md`、`zzz-docs/设想/数据集处理.md`
- 当前状态（Status）：已完成（Completed）
- 文档边界（Scope / Boundary）：本文件是候选文档 v2 完善计划（Plan），不代表进入代码实现（Apply）。

## 成功标准

- 补入 SenseVoice-Small（FunASR）、audio-separator、emotion2vec+、LangGraph 等候选路线。
- 补入来自 `数据集处理.md` 的音频预处理（audio preprocessing）经验：人声分离、去混响、谨慎降噪、响度统一、VAD 切片、字幕优先和人工校对。
- 补入工程实施路线（engineering roadmap）、资源估算（resource estimate）和本地模型环境风险。
- 降级“唯一”“最强”“固定价格”等强断言，统一标注为候选判断或需实施时核验。
- 完成后验证关键新增内容可检索。

## 执行步骤

- [x] 读取当前候选路线文档。
- [x] 对照 `STT-情感视频理解-可行性分析.md`，提取可吸收项与需降级断言。
- [x] 对照 `数据集处理.md`，提取可迁移音频处理经验。
- [x] 联网核对关键技术源：SenseVoice、audio-separator、LangGraph、OpenAI / Gemini pricing 等。
- [x] 更新 `zzz-docs/设想/视频情感化转写可行性路线.md`。
- [x] 更新 devflow 状态、决策和 checkpoint。

## 本轮不做 / 后续阶段（Deferred Scope）

- 暂不做对象或能力：不实现 Python worker、不验证真实模型安装、不跑样本视频、不创建 n8n workflow JSON。
- 本轮暂不做原因：当前目标是候选文档完善，不是原型实现或 benchmark（基准测试）。
- 后续触发条件或推荐阶段：用户确认 v2 文档方向后，进入 PRD（Product Requirements Document，产品需求文档）或 OpenSpec（开放规格）阶段，再设计样本集和 MVP 实测任务。
- 说明：这些延期项是后续阶段入口，不是永久放弃。
