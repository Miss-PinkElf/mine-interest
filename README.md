# 视频情感化转写（Video Emotion Transcript）

个人本地使用的视频/音频情感化转写与审核工作台。

## 架构概览

- 前端：React + Vite + Ant Design（本地工作台）
- 后端：FastAPI + SQLite + 本地产物目录
- 本地：媒体预处理、STT/证据工具（可替换适配器）
- 云端：多模态 LLM 证据融合（Provider Adapter）

## 本地运行

## 一键启动（推荐）

Windows PowerShell 7：

```powershell
# 在仓库根目录
./scripts/start-local-dev.ps1
```

使用已有的 `backend/.venv/Scripts/python.exe` 和 `frontend/node_modules`。默认后端端口为 `8000`、前端端口为 `5173`；若被占用，自动使用后续空闲端口，不会结束原占用进程。前端保留 Vite 热更新，后端以单进程启动，修改后端代码需重启脚本。启动后以终端显示的地址为准，按 `Ctrl+C` 停止本次启动的服务。日志位于 `.dev-logs/`，也可指定端口：

```powershell
./scripts/start-local-dev.ps1 -BackendPort 8010 -FrontendPort 5180
```

macOS / Linux（Bash）：

```bash
# 在仓库根目录
./scripts/start-local-dev.sh
```

行为说明：

- 默认后端 `8000`、前端 `5173`
- 端口被占用时先尝试结束占用进程；无法结束则自动切换到后续空闲端口
- 前端通过环境变量 `BACKEND_TARGET` 代理 `/api`
- 日志写在 `.dev-logs/backend.log` 与 `.dev-logs/frontend.log`
- `Ctrl+C` 会停止本脚本拉起的前后端

也可手动指定端口：

```bash
BACKEND_PORT=8010 FRONTEND_PORT=5180 ./scripts/start-local-dev.sh
```



### 后端

```bash
cd backend
python3.11 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 `http://127.0.0.1:5173`。开发服务器会把 `/api` 代理到 FastAPI。

## 演示转写（Demo Transcription）

在「任务」页选择本地媒体，勾选「使用演示转写（Fake STT）」后开始任务。页面会自动刷新状态；进入「待审核」后，可在「片段审核工作台」修改文本、确认片段，再回到「任务」页导出 Markdown 或 JSON。刷新浏览器后，当前标签页会恢复最近的任务。

全部片段确认后，任务显示「已确认」；导出成功后显示「已导出」。已经确认且文字未改变的片段不能重复确认，修改文字后可重新确认。
修复前创建的演示任务若片段已全部确认，刷新页面后也会恢复正确的任务状态。

演示片段由假语音转文字引擎（Fake STT）生成，**不代表媒体中的真实语音**。任务页、审核页和导出文件均显示演示来源。真实语音转文字（STT）接入属于后续阶段。

## 验证命令

```bash
cd backend && .venv/bin/python -m pytest -q
cd frontend && npm run test && npm run build
```

## 范围说明

第一版聚焦单机审核闭环。Electron、多人云端部署、平台下载、n8n、模型训练等见：

`.devflow/video-emotion-transcript-workflow/deferred/2026-07-10-mvp-deferred-scope.md`
