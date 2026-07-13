# 视频情感化转写（Video Emotion Transcript）

个人本地使用的视频/音频情感化转写与审核工作台。

## 架构概览

- 前端：React + Vite + Ant Design（本地工作台）
- 后端：FastAPI + SQLite + 本地产物目录
- 本地：媒体预处理、STT/证据工具（可替换适配器）
- 云端：多模态 LLM 证据融合（Provider Adapter）

## 本地运行

## 一键启动（推荐）

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

## 验证命令

```bash
cd backend && .venv/bin/python -m pytest -q
cd frontend && npm run test && npm run build
```

## 范围说明

第一版聚焦单机审核闭环。Electron、多人云端部署、平台下载、n8n、模型训练等见：

`.devflow/video-emotion-transcript-workflow/deferred/2026-07-10-mvp-deferred-scope.md`
