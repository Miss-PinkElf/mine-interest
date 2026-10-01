# AstrBot / NapCat 终端联启调研与候选方案

## Metadata（元数据）
- 创建时间（Created At）：2026-10-01 14:20:00 UTC。
- 更新时间（Updated At）：2026-10-01 14:36:39 UTC。
- 作者（Author）：Codex。
- 目的（Purpose）：回答终端运行形态、当前配置位置与跨平台部署选择。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-napcat-terminal/`。
- 原始需求（Raw Input）：`zzz-prompt-debug/prompt-2.md`。
- 当前状态（Status）：候选项（Candidate）。
- 文档边界（Scope / Boundary）：调研证据与候选建议；不是已批准计划（Plan），不会触发实施（Apply）。

## 当前结论与暂停边界
- 用户选择暂时保持现有桌面部署。本文仍是候选项（Candidate），未批准安装、迁移或联启，不作为下次自动执行依据。
- 首版（First Version）尚未定义；下面的脚本入口与部署组合均是待讨论候选，不是已批准范围。

## 官方资料与证据

2026-10-01 已在线读取以下官方原文。网络搜索工具未返回可用内容，终端代理 127.0.0.1:7897 不可连接；经过授权，使用直连读取官方资料。

- AstrBot 官方中文说明：https://github.com/AstrBotDevs/AstrBot/blob/master/README_zh.md 。快速开始明确列出 `uv tool install astrbot --python 3.12`、首次 `astrbot init`、`astrbot run`，另有容器部署（Docker / Docker Compose）。
- AstrBot 官方部署入口：https://docs.astrbot.app/deploy/astrbot/cli.html 。本轮启动命令以实际取得的官方中文说明为证据，不声称该部署页面正文已读取。
- NapCat 命令行启动说明：https://github.com/NapNeko/NapCatDocs/blob/main/src/guide/boot/Shell.md 。包含 Windows Shell、Linux Installer、Docker 和 macOS 安装工具；macOS 安装工具需要 macOS 12.0 或以上。不能仅由安装工具推导出“原生 macOS 可完全不运行 QQ 图形进程”。
- NapCat 框架说明：https://github.com/NapNeko/NapCatDocs/blob/main/src/guide/boot/Framework.md 。提示 QQ 9.9.19 后 LiteLoaderQQNT 维护不足，鼓励迁移 Shell。
- NapCat 官方容器说明：https://github.com/NapNeko/NapCat-Docker/blob/main/README.md 。支持 Linux/Amd64 和 Linux/Arm64，暴露端口 6099、3000、3001；网页管理入口为 `/webui`。
- 官方联启模板入口：https://github.com/NapNeko/NapCat-Docker/blob/main/compose/astrbot.yml 。容器说明明确指向该模板；脚本实施前仍需核对模板正文与连接配置。

## 结论

- AstrBot 不需要桌面应用，可以在终端运行，同时提供网页管理界面（WebUI）。
- NapCat 有命令行与 Linux 无头容器运行形态；仍依赖 QQ 运行时，不是摆脱 QQ 的独立协议客户端。
- WSL 建议以 WSL2 Linux 或容器运行；macOS 如要避免 QQ 图形应用，优先验证 Linux 容器方案。此为部署建议，不代表本机已安装并验证成功。
- 本机存在 `docker`、`uv` 命令，但尚未核实容器引擎（Docker Engine）是否运行；WSL 环境本轮不可访问。

## 后续核实：uv 安装状态与并存风险
- 本轮执行 `uv tool list` 返回 `No tools installed`；`uv tool dir` 指向默认工具目录，命令搜索路径（PATH）未找到 `astrbot`。结论为当前本机 `uv` 工具目录未安装 AstrBot，不能排除其他源码或环境中的安装。
- `uv` 已安装不等于 AstrBot 已通过 `uv` 安装；本轮没有执行安装或初始化。
- 安装并存（Coexistence）与同时运行（Concurrent Run）是不同问题：单独安装通常不覆盖桌面应用，但同时使用相同监听端口会冲突，共用数据目录会引入读写风险，同一机器人消息如何分发也需确认。
- 未来切换建议为先备份、核对运行版本与数据根目录、每次只运行一个后端实例；这是候选策略，尚未执行。

## 本机现场：已核实与未核实分开

以下是仓库外运行数据，使用用户目录记法，禁止把凭据写入仓库。

| 对象 | 配置位置或值 | 本轮证据 |
| --- | --- | --- |
| AstrBot 桌面应用版本 | 4.27.5 | 应用元信息（Info.plist），不等同于已单独核实的后端版本 |
| AstrBot 主配置 | `~/.astrbot/data/cmd_config.json` | 文件已只读解析 |
| AstrBot 插件配置 | `~/.astrbot/data/config/` | 目录存在 |
| AstrBot 插件安装目录 | `~/.astrbot/data/plugins/` | 目录存在 |
| AstrBot 插件数据 | `~/.astrbot/data/plugin_data/` | 数据目录列表 |
| AstrBot 数据库 | `~/.astrbot/data/data_v4.db` | 数据目录列表 |
| AstrBot 网页管理界面 | 开启，监听 `0.0.0.0:6185` | 主配置，地址供本机访问使用 `127.0.0.1:6185` |
| QQ 协议平台 | `Test-01`，`aiocqhttp`，启用 | 主配置 |
| 反向连接（Reverse WebSocket） | `0.0.0.0:6199` | 主配置 |
| 其他平台 | `Rin` 和官方 QQ 平台均禁用 | 主配置 |
| 全局可用插件 | `astrbot_plugin_sourcehub_inspector`、`astrbot_plugin_cc_qq`、`astrbot_plugin_sourcehub_bilibili` | 主配置 |
| NapCat 历史配置位置 | `~/Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ/NapCat/config/onebot11_1961618848.json` | 历史记录 `.devflow/multi-source-hub/handoffs/2026-09-20-003-个人号转发展开跑通与媒体待落盘.md`，本轮系统返回无权限，未读到内容 |

本轮进程采样未发现 AstrBot、NapCat 或 QQ 命名匹配进程；仅能描述采样时刻，不保证其他启动方式不存在。

本机打包后端路径工具明确支持 `ASTRBOT_ROOT`，桌面环境默认根目录为 `~/.astrbot`，普通运行默认根目录为工作目录，数据落在根目录的 `data/`。因此不能只更换启动命令而忽略数据根目录；新安装版本需要重新核实相同规则。

容器说明给出的 NapCat 持久化目录：配置 `/app/napcat/config`、QQ 登录数据 `/app/.config/QQ`、插件 `/app/napcat/plugins`。宿主机应单独挂载，不假设 macOS 登录态可直接复制到 Linux。

## 候选方案（Candidate）

1. **原生 AstrBot + 容器 NapCat，推荐。** AstrBot 使用官方终端发行方式，保留宿主机代理命令环境；NapCat 在 Linux 容器中无头运行。需要设置容器到宿主机的反向连接，macOS 与 WSL 的宿主寻址分别验证。
2. **二者全部使用容器。** 官方已有联启模板，跨平台运行结构一致；但当前插件涉及宿主机代理命令，需要额外核查命令、认证和路径挂载，不应直接假设无缝迁移。
3. **二者全部原生运行。** WSL 的 Linux 方案可以进一步验证；macOS NapCat 安装方案不等于原生无头方案，不作为当前优先推荐。

## 待确认的设计边界

- “WSL 和 mac 上面一起运行”是两端均支持启动，还是同一个 QQ 账号需要两台设备同时在线？后者需要单独讨论重复事件、登录互踢和消息处理归属。
- 候选脚本提供启动、停止、状态和日志入口；只管理本脚本启动的进程或容器，不使用宽泛进程终止。
- 端口、数据位置、实例名集中配置，不写死本机绝对路径；凭据不入库。初始化、下载安装与配置迁移不作为普通启动的隐式副作用。
- 网页管理界面优先仅绑定回环地址（Loopback）；不自动将现有配置的 `0.0.0.0` 改写为公网可访问设置。
- 启动成功与 QQ 登录成功分开判断，二维码登录不能被脚本保证或绕过。

## 本轮不做 / 后续阶段

用户已明确暂缓；详见 `../deferred/终端联启暂缓范围与待讨论事项.md`。以下触发条件均以用户明确恢复本任务为前提，不因新对话自动满足。

- 不写联启脚本：等待用户批准部署组合后，先创建实施计划与任务，再实现。
- 不修改、迁移配置或复制登录态：尚未完成备份，NapCat 配置不可读，跨系统登录态复用未知；批准部署路径并获得权限后再处理。
- 不承诺双端同账号同时在线：先确认用户意图与处理归属，再验证，不能靠启动脚本推断安全性。
- 不改插件逻辑：此需求是运行方式调整；如容器方案引出宿主工具访问问题，再单独对齐改动范围。
