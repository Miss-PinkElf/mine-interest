# Docker 双容器 E2E 启动脚本实施计划

## Metadata（元数据）

- 创建时间（Created At）：2026-10-31 01:48:58 +08:00
- 更新时间（Updated At）：2026-10-31 01:48:58 +08:00
- 作者（Author）：rin（Claude 协助）
- 目的（Purpose）：把 macOS 原生双 QQ 的 E2E 启动方式迁移为 Docker 双容器，并提供一键与分开启动脚本。
- 关联仓库或项目（Related Repository / Project）：`mine-interest-source-hub`（`.`）
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`
- 关联文档（Related Documents）：
  - `tools/astrbot_e2e/README.md`
  - `~/` 下的旧脚本 `~/.qq-e2e/start-e2e.sh`（本地脚本，不入库）
- 当前状态（Status）：用户已明确要求实施（2026-10-31）
- 文档边界（Scope / Boundary）：本计划只覆盖 Docker 启动脚本与编排；不改变测试工具断言逻辑，不迁移生产容器。

## 目标

1. 用 Docker Compose 启动两个 NapCat 容器：
   - `napcat-e2e-bot`：测试机器人 17号（3254276668），OneBot WS 6200，反向 WS 连测试 AstrBot 6198。
   - `napcat-e2e-sender`：测试发送者 C#（1961618848），OneBot WS 6201，不连 AstrBot。
2. 复用现有测试 AstrBot（`~/.astrbot-e2e`，WebUI 6186 / 反向 WS 6198）。
3. 提供一键脚本：启动两个容器、启动测试 AstrBot，并打开 iTerm2 三个标签页（两个 NapCat 日志 + 测试 AstrBot 日志），由用户扫码登录。
4. 提供分开启动脚本：bot / sender / 测试 AstrBot 各自可单独启动。
5. 提供停止与状态脚本。
6. 所有脚本与 compose 文件带中文注释；敏感值走占位/本地 `.env`，不入库。

## 拓扑与端口

| 角色 | 容器/进程 | 宿主端口 | 说明 |
|---|---|---|---|
| 测试机器人 17号 | `napcat-e2e-bot` | `6200`、`16299`（WebUI） | 反向 WS → `host.docker.internal:6198` |
| 测试发送者 C# | `napcat-e2e-sender` | `6201`、`16398`（WebUI） | E2E 工具直连 6201 发送 |
| 测试 AstrBot | 本机 `~/.astrbot-e2e` | `6186`（WebUI）、`6198`（反向 WS） | 由现有 `astrbot_e2e.cli start-instance` 启动 |
| 生产容器（可能运行） | `napcat` | `16099` 等 | 与测试共用 17号，测试前需停止或加 `--stop-production` |

令牌与 `tools/astrbot_e2e/config.local.json` 保持一致：

- bot WS：`e2e-bot-token`
- sender WS：`e2e-sender-token`
- 反向 WS：`e2e-reverse-token`

## 文件清单

```text
tools/napcat_e2e/
  compose.yaml          # 两个 NapCat service、端口、卷、注释
  common.sh             # 共享变量、配置生成、预检函数
  start-all.sh          # 一键：容器 + 测试 AstrBot + iTerm2 三标签
  start-bot.sh          # 单独启动机器人容器
  start-sender.sh       # 单独启动发送者容器
  start-astrbot.sh      # 单独启动测试 AstrBot（可 tail 日志）
  stop-all.sh           # 停止容器、测试 AstrBot，按需恢复生产容器
  status.sh             # 容器/端口/WebUI/生产容器状态
  .env.example          # 本地覆盖示例（不入库真实值）
  .gitignore            # 忽略 .env / 日志
  README.md             # 用法、拓扑、首次扫码、排障
```

运行数据放仓库外：`~/.qq-e2e-docker/{bot,sender}/{QQ,config,plugins}`。

## 关键决策

- **测试容器不自动重启**：`restart: "no"`，避免开机自动拉起测试 bot 干扰生产；需要时由脚本启动。
- **生产容器冲突显式处理**：若 `napcat` 正在运行且占用 17号，`start-all.sh` 默认中止；加 `--stop-production` 才停止并记录标记，`stop-all.sh` 可恢复。
- **原生 QQ 检查**：若检测到原生 QQ 运行，默认中止（发送者 C# 会被 Docker 顶下线）；加 `--allow-native-qq` 放行。
- **配置预生成**：为两个账号生成 `napcat.json`、`napcat_<qq>.json`、`onebot11_<qq>.json`、`webui.json`；已存在则不覆盖，避免破坏手工修改。
- **测试 AstrBot 复用现有 CLI**：`PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli start-instance/stop-instance`，不另写启动器。
- **不提交敏感信息**：token 使用本地测试默认值/`.env` 覆盖；不写真实 rkey、完整鉴权 URL。

## 验证

1. `bash -n` 检查所有脚本语法。
2. `docker compose -f tools/napcat_e2e/compose.yaml config` 校验编排（需导出变量）。
3. 启动后确认：
   - `docker ps` 两个容器 Up；
   - `docker logs` 出现 `Napi2NativeLoader 加载成功` / `PacketHandler 初始化成功`；
   - 测试 AstrBot 6186/6198 就绪；
   - 两个 QQ 扫码后 `get_login_info` 正常；
   - `doctor` 通过；
   - 跑一条探针用例验证发送/接收链路。
4. 不修改插件源码，不改变测试断言。

## 停止与回滚

- `bash tools/napcat_e2e/stop-all.sh`：`docker compose down` + `stop-instance`；若存在生产停止标记则 `docker start napcat`。
- 数据卷保留在 `~/.qq-e2e-docker`，删容器不丢登录态。
- 删除脚本目录即可完全回滚（不影响现有 `tools/astrbot_e2e`）。

## 延期

- 不把测试容器接入生产 AstrBot（只接测试 6198）。
- 不实现专用测试 bot 账号；继续用 17号 兼任，测试时停生产容器。
- 不自动扫码；二维码仍需用户手动扫描。
- 不为微信渠道提供驱动；本计划只覆盖 QQ/NapCat。
