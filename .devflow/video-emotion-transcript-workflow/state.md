# 视频情感化转写工作流 State

## Metadata（元数据）

- 创建时间（Created At）：2026-06-10 11:43:30 +08:00
- 更新时间（Updated At）：2026-07-13 15:05:44 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：保存当前 mission 的恢复热路径状态。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`zzz-prompt-debug/origin/设想/prompt.md`
- 当前状态（Status）：V1 代码任务完成；下一优先 = 上传后自动管线（先 Fake STT）
- 文档边界（Scope / Boundary）：当前快照真相源，不保存完整历史。

## 当前目标

个人本地「情感化转写」MVP：可上传、可审核、可导出；专用事实 + LLM 解释 + 人工审核。

## 完成度（核对后）

- `spec/tasks.md`：全部勾选（工程/适配层清单完成）。
- 产品可感知主路径：约 **35–45%**（缺 JobRunner 自动串联与真引擎）。
- 验证：后端 pytest 21 passed；前端 vitest 2 + build；一键启动脚本冒烟通过。

## 本会话额外交付

- `scripts/start-local-dev.sh`：端口占用先 kill，失败则换端口；Ctrl+C 清理。
- `frontend/vite.config.ts`：支持 `BACKEND_TARGET` / `FRONTEND_PORT`。
- README 补充一键启动说明。
- 与用户对齐：task 完成 ≠ 一键转写成品；下一步应串自动管线。

## 第一版已有 vs 未做

- **已有：** 双端壳、任务库、产物目录、API、设置、审核 API/UI 壳、导出服务、假管线模块与测试。
- **未串：** 上传后自动 预处理→STT→证据→review。
- **未真：** FFmpeg 深度分析、真 STT/视觉、CUDA 验收（Mac 无 ffmpeg；正式目标 Win+GPU）。
- **延期：** Electron/多人云/n8n/下载搜索/全量动作梗/训练等 → 见 `deferred/`。

## 关键产物

- 最新 handoff：`handoffs/2026-07-13-008-session-close-next-jobrunner.md`
- 恢复提示：`NEXT-SESSION-PROMPT-video-emotion-transcript-workflow.md`
- 边界：`deferred/2026-07-13-v1-adapter-vs-deferred.md`
- 启动：`scripts/start-local-dev.sh`

## 下次建议（新对话唯一优先）

1. 实现 **上传后自动最小管线**（可先 Fake STT 写 segments，状态到 review）。
2. 页面验收：有片段可确认 + 导出 Markdown。
3. 再考虑 FFmpeg 真抽轨或远程/本机轻量 STT；不碰延期项。
