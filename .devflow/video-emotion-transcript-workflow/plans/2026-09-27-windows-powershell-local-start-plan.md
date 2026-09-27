# Windows PowerShell 本地一键启动计划（Plan）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-27 12:20:23 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：为 Windows 开发环境增加同时启动前后端的 PowerShell 入口。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联原始需求（Related Source）：`.devflow/video-emotion-transcript-workflow/origin.md`
- 关联文件（Related Files）：`scripts/start-local-dev.sh`、`scripts/start-local-dev.ps1`、`README.md`
- 当前状态（Status）：已完成（Completed），2026-09-27 12:26:52 +08:00 已验证
- 文档边界（Scope / Boundary）：本轮轻量计划真相源；用户已明确要求直接写计划、实施并测试，随后明确授权提交代码。

## 最小对齐（Mini Align）

- 目标：在 Windows PowerShell 中用一个命令同时启动本地 FastAPI 后端与 Vite 前端，使用现有 `backend/.venv/Scripts` 环境。
- 行为：检查依赖、自动选择空闲端口、等待健康检查、显示访问地址与日志路径；脚本结束时清理它启动的进程。
- 端口策略：占用时自动寻找后续空闲端口，不结束原占用进程；前端代理随实际后端端口调整。
- 边界：保留现有 Bash 脚本；不改业务逻辑、数据库或依赖。

## 任务与验收

1. 新增 `scripts/start-local-dev.ps1`。验证：PowerShell 7 能启动两个服务，后端健康检查和前端页面均可访问。
2. 更新 `README.md`，给出 Windows 启动命令和日志位置。验证：说明与实际脚本一致。
3. 验证端口占用时自动换端口，并在终止脚本后确认只清理本次启动的服务。
4. 运行 `git diff --check`，记录实际验证结果；不执行 Git 提交（commit）。

## 本轮不做 / 后续阶段

- 不重写 Unix Bash 启动脚本：本轮只补 Windows 入口；若后续要求两平台行为完全统一，再单独对齐。
- 不增加常驻服务或开机自启：当前仅需开发会话运行；用户提出常驻需求时再规划。

## 验证结果

- PowerShell 语法解析通过；默认端口启动后，`8000/api/health`、`5173/api/health` 与前端页面分别返回正常响应。
- 使用独立监听器占用 `8000` 与 `5173` 后，脚本自动改用 `8001` 与 `5174`；新前端 API 代理返回 `ok`。
- 两次运行均通过 `Ctrl+C` 停止本次启动的服务；占用默认端口的测试监听器保持运行。
- 首次测试发现 Windows 下后端 `--reload` 的多进程行为与当前执行环境不兼容，Windows 入口改为单进程后端；Vite 前端仍保持开发热更新。
