# 原始输入索引

## Metadata（元数据）
- 创建时间（Created At）：2026-10-01 14:20:00 UTC。
- 更新时间（Updated At）：2026-10-01 14:36:39 UTC。
- 作者（Author）：Codex。
- 目的（Purpose）：追溯用户原始需求。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-napcat-terminal/`。
- 当前状态（Status）：已暂停（Paused）。
- 文档边界（Scope / Boundary）：原始输入索引真相源（source of truth）；不触发实现。

- 原始需求：`zzz-prompt-debug/prompt-2.md`。
- 用户要求先搜索 AstrBot、NapCat 的启动方式和运行形态，再检查当前配置位置，设计同时启动二者的脚本，并支持 WSL 与 macOS。
- 官方来源：AstrBot 官方文档和源码仓库、NapCat 官方文档和源码仓库；详细出处见候选调研文档。

## 后续原始输入（Raw Input）
- 2026-10-01，对话追加：“astrbot，有uv的安装方式，要不用这个，napcat这个你看看，这个有没有”。用途：探索终端安装方式；已吸收为 AstrBot 倾向选择 `uv`，不代表组合方案已批准。
- 2026-10-01，对话追加：“我astrbot有uv吗？同时我又安装图形界面，又安装uv版本的，会冲突吗”。用途：核查本机安装状态及并存风险；已核实工具安装列表，运行隔离策略尚未获批准。
- 2026-10-01，对话追加：“算了暂时这样吧”及收尾、保存延期项、仅提交本轮相关文件的要求。用途：明确暂停与提交授权；不构成部署实施授权。
- 收尾指导：`devflow-handoff.md`，仅阅读，不修改；本轮明确提交授权优先于该指导的默认询问提交要求。
