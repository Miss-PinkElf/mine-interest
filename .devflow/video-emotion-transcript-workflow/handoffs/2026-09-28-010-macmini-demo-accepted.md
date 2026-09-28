# Mac mini 演示验收与状态修复交接（Handoff 010）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 11:42:20 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：保存本次 Mac mini 演示验收、状态问题修复、能力边界和下一阶段恢复步骤。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-prompt-debug/origin/设想/prompt.md`、`.devflow/video-emotion-transcript-workflow/origin.md`
- 关联对齐与计划（Related Align / Plan）：`.devflow/video-emotion-transcript-workflow/plans/2026-09-28-review-confirmed-status-align.md`、`.devflow/video-emotion-transcript-workflow/plans/2026-09-28-review-confirmed-status-plan.md`
- 关联规格（Related Spec）：`.devflow/video-emotion-transcript-workflow/spec/design.md`、`.devflow/video-emotion-transcript-workflow/spec/tasks.md`
- 当前状态（Status）：交接就绪（Ready for Handoff）；演示状态修复已通过用户手动验收。
- 文档边界（Scope / Boundary）：会话交接记录，不替代 `state.md`、规格或下一阶段方案批准；不代表真实 STT（语音转文字）已完成。

## 当前目标与阶段

- 长期目标：个人本地视频/音频情感化转写与人工审核工作台。
- 本轮阶段：显式演示模式（Demo Mode）手动验收与任务状态修复已完成 Verify（验证）；按用户要求完成 Close（收尾）和跨会话交接。

## 当前进度与本轮完成

- Mac mini 已具备 Python 3.11、Node.js 及项目依赖；`scripts/start-local-dev.sh` 曾实测通过本机前后端与 API 代理健康检查。该启动脚本不是本轮代码改动。
- 用户上传媒体并使用假语音转文字（Fake STT）完成演示任务；手动验收发现片段 `confirmed`（已确认）而任务仍停留「待审核 70%」。
- 用户确认状态规则：全部片段确认后任务为「已确认 90%」，导出后为「已导出 100%」。后端已在确认事务中汇总任务状态、在读取旧任务时修复历史不一致记录；前端成功操作后刷新任务并显示明确反馈。
- 用户截图显示修订文本保留、片段已确认、重复确认按钮禁用、任务已导出 100%，随后回复“可以了”。自动验证：后端 32 项测试、前端 11 项测试和前端构建通过。
- 用户本轮明确授权先提交相关代码再收尾；提交范围只含当前 mission 相关代码和文档，保留无关 `.vscode/controlled-explorer.json`，默认不纳入 `config.ts`、`.gitignore`、`tsconfig.json`。

## 关键决策与原因

| 决策 | 原因 |
| --- | --- |
| 任务状态以全部片段确认结果推进，并在旧任务查询时修复不一致状态 | 用户旧任务已经确认，只有新确认路径修复会让其刷新后仍显示待审核 |
| 演示模式只验证上传、审核、导出交互 | 假转写引擎不读取媒体内容，不能把演示文本或空证据误写成真实识别结果 |
| 真实 STT、媒体回放和情绪证据留待下一阶段重新对齐 | 当前没有代表性样本、选型及真实结果验收标准；先收束已验证的第一版 |
| 大语言模型（LLM）自主选工具和 TTS（文字转语音）保持候选/未批准状态 | 本轮只是提及与概念澄清，没有对齐范围或授权实施 |

## 关键文件与真相源

- 热路径：`state.md`、`checkpoints.md`；进度追踪：`spec/tasks.md`；问题记录：`bug-log.md`。
- 本轮对齐与计划：`plans/2026-09-28-review-confirmed-status-align.md`、`plans/2026-09-28-review-confirmed-status-plan.md`。
- 第一版与延期边界：`deferred/2026-07-13-v1-adapter-vs-deferred.md`；轻量候选：`backlog.md`。
- 核心实现：`backend/app/services/jobs.py`、`backend/app/services/review.py`、`frontend/src/App.tsx`、`frontend/src/features/review/ReviewWorkspace.tsx`；启动说明：仓库根目录 `README.md`。

## 风险、开放问题与延期范围

- 演示转写文本与上传音频无关；播放器尚无媒体源，证据面板没有真实数据，云端 Provider 设置并不意味着演示任务会调用 LLM。导出文件目前写入后端本机目录，页面只显示路径；具体阶段与触发条件见 `deferred/2026-07-13-v1-adapter-vs-deferred.md`。
- 下一阶段真实 STT、媒体处理、回放与音视频情绪证据的实施顺序、目标环境和验收样本尚未讨论确认；不从本次演示验收直接推断真实能力完成。
- Electron、n8n、平台下载、训练等延期项继续保留；LLM 基于工具元数据选工具为候选项（Candidate）。TTS 本轮只做概念澄清，如用户提出明确用途再单独对齐。
- 本轮用户截图证明最终片段与导出状态，未单独留存「已确认 90%」中间截图；该状态转移有自动测试，用户随后口头确认整体验收通过。

## 立即下一步

1. 新会话先核对 `git log -1` 与 `git status --short`，确认本轮提交和无关工作区改动的边界；默认不重做已验收演示任务。
2. 询问用户下一阶段是否优先真实 STT（语音转文字），还是先讨论真实媒体处理/回放；收集 1～2 个代表性样本和可验收输出，再进入 Align（对齐）。
3. 对齐确认后写当前 mission 的 Plan（计划）与 OpenSpec（开放规格）任务，再实施；不得自动接入 LLM 自主选工具、TTS 或其他延期项。

## 恢复指引

默认先读 `state.md` → `checkpoints.md`；需要本轮细节再读本 handoff。完整阶段脉络见 `development-overview.md`，原始需求与延期追溯见 `origin.md`、`deferred/`。以当前仓库代码和最近记录为准。

## 可从活跃上下文移除的内容

本轮环境版本检查、沙箱中本机端口绑定失败与提权验证的操作输出、失败先行测试的详细日志和截图逐步解释已归纳为测试、问题日志与本 handoff；下次无需重放。
