# 视频情感化转写工作流 Checkpoints Archive

## Metadata（元数据）

- 创建时间（Created At）：2026-07-10 15:15:33 +08:00
- 更新时间（Updated At）：2026-07-10 16:40:38 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：归档当前 mission 超出恢复热路径上限的旧 checkpoint，保留历史可追溯性。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-prompt-debug/origin/设想/prompt.md`
- 当前状态（Status）：已归档（Archived）
- 文档边界（Scope / Boundary）：本文件是历史 checkpoint 存档，不是当前恢复热路径真相源，不触发实现。

## 已归档 checkpoint

### 2026-07-10 15:15:33 +08:00 - 正式实施计划完成，等待 OpenSpec

- 完成内容：创建 `plans/2026-07-10-video-emotion-transcript-mvp-implementation-plan.md`，按工程初始化、领域模型、双音轨预处理、工具编排、转写、专用证据、云端融合、审核、API、React、端到端与基准测试拆分为 14 个可验证任务。
- 计划口径：先形成可审核的本地纵向闭环，再接入真实模型与云端融合；每项行为先写失败测试；不在任务中实现已确认延期项。
- 自查：无占位符；补齐了基准 runner 和 benchmark manifest 的创建路径；验证了文档格式检查。
- 下一步：调用 openspec-propose，将已确认 Plan 落为 OpenSpec 的 proposal、design 和 tasks；完成前不得进入 Apply。

### 2026-07-10 15:05:09 +08:00 - MVP 对齐获确认并升级为重型路径

- 完成内容：基于 `zzz-prompt-debug/origin/设想/` 的原始设想重新完成对齐，写入已确认 MVP 对齐文档。
- 已确认架构：React + Vite 浏览器工作台、FastAPI 本地服务、确定性工具管线、状态化 Agent、云端多模态 LLM 和后续可选 n8n。
- 已确认核心原则：按需预处理并保留原始/轻处理与 STT 就绪双音轨；专用模型优先提供事实证据，LLM 负责有依据的语义解释；低置信度或证据冲突进入人工审核。
- 已确认审核能力：分段回放、视频/关键帧对照、文本/结论编辑、切分/合并/删除、局部重分析和 JSON / Markdown 导出。
- 阶段变化：从已关闭的轻量调研路径升级为重型 MVP 构建路径。下一步必须由用户审阅对齐文档后写 Plan（计划），不得直接实施。

### 2026-06-10 15:45:35 +08:00 - 收尾 handoff 并明确 MVP 延期边界

- 完成内容：补充候选文档中的“第一版范围与明确延期矩阵（MVP Scope and Deferred Scope Matrix）”，创建 mission handoff 和下一会话入口。
- 第一版聚焦：本地文件输入、音频质量报告、SenseVoice-Small / WhisperX baseline、基础抽帧、多模态 LLM 画面描述、低置信度人工审核列表、Markdown / JSON 输出。
- 明确延期：平台自动下载、自动评论抓取、反向搜图、n8n workflow、复杂前端 UI、自训练情绪模型、全自动梗理解。
- 最新 handoff：`handoffs/2026-06-10-001-resume-ready.md`
- 下一会话入口：`NEXT-SESSION-PROMPT.md`

### 2026-06-10 15:34:26 +08:00 - 完成候选路线文档 v2 完善

- 完成内容：更新 `zzz-docs/设想/视频情感化转写可行性路线.md`，吸收 `STT-情感视频理解-可行性分析.md` 与 `数据集处理.md` 的可借鉴点。
- 新增重点：SenseVoice-Small（FunASR）、audio-separator、emotion2vec+、LangGraph、音频预处理细化方案（Audio Preprocessing Recipe）、工程实施路线（Engineering Roadmap）和资源估算口径（Resource Estimate）。
- 关键口径：保留候选项（Candidate）状态；不把“唯一”“最强”“价格”等易变信息写成最终事实；实施阶段必须以样本集 benchmark（基准测试）确认。
- 后续入口：如果继续推进，应先确认 MVP 范围和样本集，再写 PRD（Product Requirements Document，产品需求文档）或 OpenSpec（开放规格）。

### 2026-06-10 11:47:50 +08:00 - 完成视频情感化转写可行性调研文档

- 完成内容：基于原始需求和联网调研，产出 `zzz-docs/设想/视频情感化转写可行性路线.md`。
- 核心结论：整体可行，但应作为多阶段媒体理解 Agent（multistage media understanding agent）处理，不能期待单一 STT（Speech to Text）模型完成情绪、表情、梗和语境理解。
- 推荐路线：Python pipeline 承载 FFmpeg、Demucs、WhisperX、pyannote.audio、MediaPipe 等重计算；Agent tool layer 负责搜索、反向搜图、评论区和多模态融合；n8n workflow 负责编排、人审和结果分发。
- 验证证据：已执行文件存在性检查，5 个目标文件均返回 `True`；已执行关键小节检索，命中 Metadata（元数据）、候选项（Candidate）、结论、候选技术栈、推荐工作流、Agent / n8n、MVP 和 Deferred Scope。
- 后续入口：确认 MVP（Minimum Viable Product，最小可行产品）范围后，进入 PRD（Product Requirements Document，产品需求文档）或 OpenSpec（开放规格）。

### 2026-07-10 15:23:33 +08:00 - OpenSpec 就绪，等待 Apply 授权

- 完成内容：创建 `spec/proposal.md`、`spec/design.md` 和 `spec/tasks.md`，并补齐 origin、state history、development overview 与明确延期范围。
- 当前状态：用户明确要求本轮不进入 Apply；没有应用代码、依赖安装或模型 benchmark。
- 下一步：新会话先读 `state.md`、`checkpoints.md`、`spec/tasks.md`；只有用户明确授权后才从正式 Plan 的 Task 1 开始实施。

### 2026-07-10 16:24:25 +08:00 - Task 1 工程骨架与验证完成

- 完成内容：建立 `backend/.venv`（Python 3.11）、FastAPI 健康检查和本地 CORS；建立 React + Vite + Ant Design 前端骨架、`/api` 本地代理和前端依赖锁文件。
- 验证证据：后端 `pytest -q` 通过 2 项、`pip check` 通过；前端 `npm run build` 通过。CORS 预检覆盖 `localhost:5173` 与 `127.0.0.1:5173`。
- 环境决策：清华 npm 镜像不提供可用 Registry，用户已授权改用默认 npm / PyPI 源；不执行提交。
- 下一步：Task 2，先为 `Segment.raw_text` 不可被人工修订覆盖编写失败测试，再实现领域模型。

