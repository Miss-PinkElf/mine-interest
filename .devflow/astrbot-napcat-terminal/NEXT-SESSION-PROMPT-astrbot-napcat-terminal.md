# 下次对话提示词

## Metadata（元数据）
- 创建时间（Created At）：2026-10-01 14:36:39 UTC。
- 作者（Author）：Codex。
- 目的（Purpose）：提供可复制的新对话恢复指引。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-napcat-terminal/`。
- 原始需求（Raw Input）：`zzz-prompt-debug/prompt-2.md`。
- 当前状态（Status）：已暂停（Paused）。
- 文档边界（Scope / Boundary）：恢复提示词，不是安装、迁移或实施授权。

## 可复制的提示词

请恢复 `.devflow/astrbot-napcat-terminal/` 的上下文，默认先只读 `state.md` 与 `checkpoints.md`。需要详细背景时再读 `handoffs/2026-10-01-001-终端部署调研暂缓交接.md` 和 `deferred/终端联启暂缓范围与待讨论事项.md`，不要默认读取其他任务的历史。

上一轮只完成调研，我决定“暂时这样”，保持现有桌面部署。Mac 已安装 uv，但当前 uv 工具列表为空，没有通过默认 uv 工具目录安装 AstrBot。现有 AstrBot 网页管理界面（WebUI）6185、反向连接（Reverse WebSocket）6199，主配置在 `~/.astrbot/data/cmd_config.json`；NapCat 本机配置因系统隐私权限未读到，本轮没有安装、启动、迁移或修改插件。

我倾向未来 AstrBot 用 uv，但 NapCat 用何种方案尚未批准。联启脚本、终端切换、配置与登录态迁移明确暂缓；两端分别可运行还是同账号同时在线、两版数据隔离与首版范围仍未讨论完成。不要把它们当成已批准任务，也不要永久放弃。

请先根据我在新对话提出的需求确认是否恢复部署工作；未明确恢复时保持暂停。恢复后先讨论方案，完成对齐（Align），再在当前任务的 `plans/` 落盘计划（Plan）与任务（Tasks），之后才实施（Apply）。禁止直接执行 `astrbot init` 或改现有配置。只改本任务相关内容，遵守仓库根目录协作约束。
