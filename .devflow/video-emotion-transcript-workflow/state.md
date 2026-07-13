# 视频情感化转写工作流 State

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-07-13 14:27:21 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：保存当前 mission 的恢复热路径（resume hot path）状态。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-prompt-debug/origin/设想/prompt.md`
- 当前状态（Status）：MVP 代码任务已完成，进入真实模型加深阶段（Completed Code Tasks / Next Real Models）
- 文档边界（Scope / Boundary）：本文件是当前 mission 的当前状态真相源（source of truth），不保存完整历史。

## 当前目标

在个人本地场景落地视频/音频「情感化转写（emotion-aware transcription）」MVP：可上传、可审核、可导出；专用模型出事实、LLM 出有依据解释。

## 当前阶段

- 路径：重型 Apply 已完成 `spec/tasks.md` 全部勾选。
- 性质：**第一版（V1）代码与可替换适配层已落地**；**真实 FFmpeg / STT / MediaPipe / 云端推理与 Windows CUDA 实测**属于下一阶段加深，不是本轮未完成的勾选任务。

## 已完成（本会话 + 既有 Apply）

- Task 1-5 与阶段 2-5：持久化、API、前端工作台、媒体/预处理/转写适配、审核操作、Tool Registry、Orchestrator、证据、融合、重分析、导出、benchmark 清单、README。
- 验证：后端 `pytest -q` 21 passed；前端 vitest 2 passed + `npm run build` 通过。
- 本地提交：`8252994` … `a34d16b`（分支 `wxl/auto-stt`，ahead of origin）。

## 第一版已实现但刻意保持“适配层”的能力

以下**已做第一版**（接口/路由/测试齐），**未绑定生产真实重模型**：

| 能力 | 第一版形态 | 后续加深触发 |
| --- | --- | --- |
| 媒体探测 / 质量报告 | 可注入探测器 + 文件名启发 | 需要真实 BGM/噪声指标时接入 FFmpeg 分析 |
| 预处理产物 | 路由 + 占位轨写入，原始轨不覆盖 | 接入真实分离/降噪工具链 |
| STT / diarization | `TranscriptionEngine` + Fake engine | 接入 SenseVoice / WhisperX / pyannote |
| 视觉 / 姿态 / 表情 | Orchestrator 标准化输出桩 | 接入 MediaPipe 等本地模型 |
| 云端融合 | OpenAI-compatible 协议 + 本地回退 | 配置真实 Provider 与 Key 后走 HTTP |
| Playwright E2E | 规格已落盘，默认无服务时跳过 | 安装浏览器并设 `E2E_BASE_URL` |

## 明确延期（未做、非放弃）

见 `deferred/2026-07-10-mvp-deferred-scope.md` 与本会话补充的 `deferred/2026-07-13-v1-adapter-vs-deferred.md`。

## 关键产物

- 最新 handoff：`handoffs/2026-07-13-007-session-close-context-handoff.md`
- 恢复提示：`NEXT-SESSION-PROMPT-video-emotion-transcript-workflow.md`
- 任务清单：`spec/tasks.md`（全部 `[x]`）
- Benchmark：`benchmarks/2026-07-13-sample-matrix.md`
- README：`README.md`

## 下次建议（新对话优先）

1. 读 `state.md` + `checkpoints.md` + 最新 handoff。
2. 按 benchmark 矩阵选 1-2 个真实样本，接入 **一个** 真实能力（建议先 FFmpeg 质量报告或 STT）。
3. 不要重新扩大延期范围；先把适配层换成可验证的真实实现。
