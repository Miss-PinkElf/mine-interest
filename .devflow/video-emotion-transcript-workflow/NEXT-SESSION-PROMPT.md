# 下一会话提示：视频情感化转写工作流

## Metadata（元数据）

- 更新时间（Updated At）：2026-07-13 15:05:44 +08:00
- 关联 mission：`.devflow/video-emotion-transcript-workflow/`
- 当前状态：V1 任务清单完成；下一优先 JobRunner
- 文档边界：恢复提示，不是自动实施授权。

请继续 mission：`video-emotion-transcript-workflow`。

## 默认先读

1. `.devflow/video-emotion-transcript-workflow/state.md`
2. `.devflow/video-emotion-transcript-workflow/checkpoints.md`
3. `.devflow/video-emotion-transcript-workflow/handoffs/2026-07-13-008-session-close-next-jobrunner.md`
4. `.devflow/video-emotion-transcript-workflow/deferred/2026-07-13-v1-adapter-vs-deferred.md`

## 当前进度

- `spec/tasks.md` **全部完成**（模块/适配层/测试）。
- **产品主路径未通：** 上传后不会自动 STT，审核页常无片段。
- 一键启动：`./scripts/start-local-dev.sh`（默认 5173/8000，端口冲突可杀可切换）。
- 用户已理解：task = 零件；缺总装 JobRunner。

## 本轮只做（建议）

**上传后自动最小管线（可先 Fake STT）→ 片段入库 → 状态 review → 前端可确认并导出。**

不要：重做脚手架；Electron/n8n/下载搜索；一上来全量真 GPU 模型。

## 验收标准

1. 上传文件后，无需手工插库，审核页出现至少 1 个片段。
2. 可确认片段并导出 Markdown/JSON。
3. 后端测试保持通过；补上管线相关测试。

## 启动

```bash
./scripts/start-local-dev.sh
# 前端 http://127.0.0.1:5173
```

## 注意

- `backend/.venv`；相对路径；文档中英术语。
- 本地运行数据在 `backend/data/`，不要提交。
- 未经允许不 commit（本收尾会话用户已要求提交相关文件）。
