# Docker 双容器 E2E 启动脚本

## Metadata（元数据）

- 创建时间（Created At）：2026-10-31 01:55:00 +08:00
- 更新时间（Updated At）：2026-10-31 02:45:00 +08:00
- 作者（Author）：rin（Claude 协助）
- 目的（Purpose）：用 Docker Compose 启动两个 NapCat 容器（测试机器人 + 测试发送者）与测试 AstrBot，提供一键与分开启动脚本。
- 关联仓库或项目（Related Repository / Project）：`mine-interest-source-hub`（`.`）
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`
- 关联计划（Related Plan）：`.devflow/astrbot-plugin-e2e/plans/2026-10-31-Docker双容器E2E启动脚本-plan.md`
- 当前状态（Status）：已实现（Implemented）
- 文档边界（Scope / Boundary）：使用说明；测试断言逻辑仍以 `tools/astrbot_e2e/` 为准。

## 如何生成 / 首次部署

本目录的脚本和 compose 已经入库，**不需要代码生成器**。首次部署只需要运行脚本，脚本会自动生成运行配置。

### 前置条件

- macOS + OrbStack/Docker（`docker info` 可用）
- iTerm2（一键脚本会打开三个标签；没有 iTerm2 时用 `--no-iterm` 打印手动命令）
- AstrBot CLI（`~/.local/bin/astrbot`）与 `backend/.venv`
- `tools/astrbot_e2e/config.local.json`（本地配置，不入库）
- 两个 QQ 账号 + 专用测试群（默认 `701292201`）
- 首次运行能手动扫码登录两个 QQ

可选：复制本地覆盖文件：

```bash
cp tools/napcat_e2e/.env.example tools/napcat_e2e/.env
# 按需修改账号、端口、token；.env 已在 .gitignore 中忽略
```

### 首次启动步骤

1. 启动两个 NapCat 容器（会停掉占用 17号 的生产容器）：

   ```bash
   bash tools/napcat_e2e/start-all.sh --stop-production
   ```

2. 在前两个 iTerm2 标签扫码登录 17号 和 C#。

3. 第三个标签会自动等待 `6200/6201` 登录就绪，然后启动测试 AstrBot（`--detach` 后台启动）。

4. 环境自检：

   ```bash
   PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor \
     --config tools/astrbot_e2e/config.local.json
   ```

5. 跑用例：

   ```bash
   PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run-suite \
     --cases-dir tools/astrbot_e2e/cases \
     --config tools/astrbot_e2e/config.local.json --attach
   ```

### 脚本会生成什么

- `~/.qq-e2e-docker/bot/config/`：
  - `napcat.json`、`napcat_<bot_qq>.json`
  - `onebot11_<bot_qq>.json`（OneBot 服务端 6200 + 反向 WS 6198）
  - `webui.json`
- `~/.qq-e2e-docker/sender/config/`：同结构，OneBot 服务端 6201，不连 AstrBot。
- 已存在的配置不会被覆盖。
- QQ 登录态在 `~/.qq-e2e-docker/{bot,sender}/QQ`。
- **测试 AstrBot 不是新下载**：同一个 `astrbot` CLI，数据根是 `~/.astrbot-e2e`，端口 6186/6198；测试插件会被复制到 `~/.astrbot-e2e/data/plugins`，不改生产插件目录。

## 拓扑

| 角色 | 容器/进程 | 宿主端口 | 说明 |
|---|---|---|---|
| 测试机器人 17号 | `napcat-e2e-bot` | `6200`、`16299`（WebUI） | 反向 WS → `host.docker.internal:6198` |
| 测试发送者 C# | `napcat-e2e-sender` | `6201`、`16398`（WebUI） | E2E 工具直连 6201 发送 |
| 测试 AstrBot | 本机 `~/.astrbot-e2e` | `6186`、`6198` | 由 `astrbot_e2e.cli start-instance` 启动 |
| 生产容器（可能运行） | `napcat` | `16099` 等 | 与测试共用 17号，测试前需停止 |

运行数据放在仓库外：

```text
~/.qq-e2e-docker/
  bot/{QQ,config,plugins}
  sender/{QQ,config,plugins}
```

## 一键启动

```bash
cd /Users/mobius/Documents/111AAA-code/mine-interest.worktrees/mine-interest-source-hub
bash tools/napcat_e2e/start-all.sh --stop-production
```

`--stop-production` 的作用：

- 生产容器 `napcat` 也登录 17号；不停止它会和测试机器人抢同一账号。
- 脚本停止生产容器并写入标记；`stop-all.sh` 会自动 `docker start napcat` 恢复。

脚本会：

1. 检查 Docker / 测试 AstrBot 前置文件；
2. 生成两个容器的 NapCat 配置（已存在则不覆盖）；
3. 启动 `napcat-e2e-bot` 与 `napcat-e2e-sender`；
4. 打开 iTerm2 三个标签：
   - 机器人日志（扫码登录 17号）
   - 发送者日志（扫码登录 C#）
   - 测试 AstrBot 启动 + 日志

首次运行需要分别扫码。二维码会出现在两个 NapCat 标签的日志里，也可以打开脚本打印的 WebUI 地址扫码。

如果原生 QQ 正在运行，脚本默认中止（Docker 发送者登录 C# 会把它顶下线）。确认可以顶下线后加：

```bash
bash tools/napcat_e2e/start-all.sh --stop-production --allow-native-qq
```

不想打开 iTerm2：

```bash
bash tools/napcat_e2e/start-all.sh --stop-production --no-iterm
```

## 启动顺序与等待

- `start-all.sh` 先启动两个 NapCat 容器，再打开标签。
- 测试 AstrBot 标签使用 `start-astrbot.sh --detach`：
  它会在后台等待 `6200`（机器人）和 `6201`（发送者）上线，也就是等你扫码登录两个 QQ；
  两个端口都上线后才调用 `start-instance`。
- 如果你单独先跑 `start-astrbot.sh`，它会提示「等待 6200/6201」，最多等 30 分钟；
  不想等可以加 `--no-wait`（会更快失败）。
- `start-instance` 失败会自动重试 3 次（间隔 3 秒），用于 NapCat 刚重启/重连时的瞬时断连（`Server disconnected`）。
- 手动排查时注意：AstrBot CLI 的 `get_astrbot_root()` 实际按**当前工作目录**判断根目录；
  请先 `cd ~/.astrbot-e2e` 再运行 `astrbot run`，或直接用本脚本。
- 后台等待/启动日志：`~/.astrbot-e2e/bootstrap-run/start-instance.log`。

## 重复执行与关闭终端

- `docker compose up -d` 是幂等的：容器名、端口、卷固定，不会创建重复容器。
- 两个容器和测试 AstrBot 都已在运行时，`start-all.sh` 默认跳过打开新标签；
  需要新的日志窗口请加 `--force-tabs`。
- 需要重启：加 `--restart`。它会 `docker restart` 两个 NapCat 容器（数据卷和登录态保留），
  并让测试 AstrBot 先 `stop-instance` 再重新启动。
- `start-astrbot.sh` 有启动锁和 6186 端口检查：已有启动流程或实例在跑时，只 tail 日志，不会重复启动。
- **关闭终端**：
  - Docker 容器由 OrbStack 管理，关闭终端不会停止它们；
  - 测试 AstrBot 在 `start-all.sh` 里用 `--detach` 后台启动，关闭标签一般不会停止它；
  - 如果手动用前台模式 `start-astrbot.sh`（不加 `--detach`），关闭终端可能导致它被 SIGHUP 杀掉。
- 需要彻底停止：`bash tools/napcat_e2e/stop-all.sh`。

## 分开启动

```bash
# 机器人容器（17号）
bash tools/napcat_e2e/start-bot.sh --stop-production

# 发送者容器（C#）
bash tools/napcat_e2e/start-sender.sh

# 测试 AstrBot（默认加载 astrbot_plugin_cc_qq）
bash tools/napcat_e2e/start-astrbot.sh

# 指定被测插件
bash tools/napcat_e2e/start-astrbot.sh --plugin astrbot_plugin_sourcehub_inspector
```

启动后可跟日志：

```bash
bash tools/napcat_e2e/start-bot.sh --logs
bash tools/napcat_e2e/start-sender.sh --logs
```

## 停止与状态

```bash
bash tools/napcat_e2e/status.sh
bash tools/napcat_e2e/stop-all.sh
```

`stop-all.sh` 会：

1. `docker compose down --remove-orphans` 停止两个测试容器（数据卷保留）；
2. 停止测试 AstrBot 实例；
3. 如果存在生产停止标记，恢复 `napcat` 生产容器。

## 首次扫码与登录

WebUI 地址（脚本会打印实际 token）：

- 机器人：`http://127.0.0.1:16299/webui?token=<bot-token>`
- 发送者：`http://127.0.0.1:16398/webui?token=<sender-token>`

也可以直接看日志里的 ANSI 二维码：

```bash
docker logs -f napcat-e2e-bot
docker logs -f napcat-e2e-sender
```

登录态持久化在 `~/.qq-e2e-docker/{bot,sender}/QQ`，容器重启一般不需要重新扫码。

## 运行测试

环境自检：

```bash
cd /Users/mobius/Documents/111AAA-code/mine-interest.worktrees/mine-interest-source-hub
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli doctor \
  --config tools/astrbot_e2e/config.local.json
```

运行用例：

```bash
PYTHONPATH=tools backend/.venv/bin/python -m astrbot_e2e.cli run-suite \
  --cases-dir tools/astrbot_e2e/cases \
  --config tools/astrbot_e2e/config.local.json --attach
```

退出码：`0` 通过，`1` 失败，`2` 用例/配置错误，`3` 环境错误。

## 注意事项

1. **同一 QQ 账号不能双端在线**：生产容器 `napcat` 与测试 `napcat-e2e-bot` 都用 17号；测试前必须停一个。
2. **测试 AstrBot 只连 6198**：测试机器人容器只配置 `AstrBot-E2E` 客户端，不连生产 6199，所以生产 AstrBot 不需要暂停。
3. **原生 QQ 与 Docker 发送者**：如果原生 QQ 登录了 C#，Docker 登录会把它顶下线；脚本默认中止，需 `--allow-native-qq` 放行。
4. **切换同 `self_id` 的 NapCat 后**：如果 AstrBot 出现“消息能收但插件主动调用失败”，重启 AstrBot 并等 30 秒让 NapCat 重连。
5. **不要提交 `~/.qq-e2e-docker`**：里面是 QQ 登录态与真实配置。
6. **token**：`.env` 已在 `.gitignore` 中忽略；默认值仅用于本地测试。不要把真实 token、rkey 写入仓库。

## 旧原生 e2e 数据（已归档）

2026-10-31 已将旧原生双 QQ e2e 的日志与测试 NapCat 工作目录移动到：

```text
~/.qq-e2e/archive-20261031/
  production-qq.log
  qq-e2e.log
  NapCat-e2e/
```

- 归档目录权限为 `700`，内容含真实聊天日志与旧登录配置，不要提交或外传。
- `~/.qq-e2e/start-*.sh` 等原生脚本仍保留作回退参考，Docker 方案不依赖它们。
- **保留**：`~/.astrbot-e2e`（本方案使用的测试 AstrBot 数据）、`~/napcat`（生产 Docker NapCat 数据）。
- Docker 方案的运行数据在 `~/.qq-e2e-docker`，与旧原生数据完全隔离。

## 常见问题（FAQ）

### 为什么只看到一个 `napcat` 容器？

- `napcat` 是**生产容器**，来自 `~/napcat`，只跑 17号 一个 QQ。
- E2E 的两个容器是 `napcat-e2e-bot` / `napcat-e2e-sender`，只有执行 `start-all.sh` 才会创建。
- 执行 `start-all.sh --stop-production` 后，生产 `napcat` 会被停掉，OrbStack 里应看到两个 `napcat-e2e-*` 容器。
- 一个容器只跑一个 QQ；不是把两个 QQ 塞进一个容器。

### 为什么测试 AstrBot 报 `Server disconnected`？

- 通常是 NapCat 刚启动/重连时的瞬时断连，或者容器还在扫码登录。
- 脚本现在会：
  - 等待 `6200/6201`；
  - 用 `wait_onebot.py` 实际调用 `get_login_info` 确认账号就绪；
  - `start-instance` 失败重试 3 次（间隔 3 秒）。
- 仍失败时用：

  ```bash
  bash tools/napcat_e2e/start-astrbot.sh --restart --detach
  ```

- 手动排查时注意：AstrBot CLI 的根目录判断实际用**当前工作目录**，请先 `cd ~/.astrbot-e2e`，或直接用脚本。

### `doctor` 通过但 `probe_echo` 失败？

- 测试群里同时启用了 `astrbot_plugin_cc_qq` 时，cc-qq 会先回「已收到，正在处理…」，探针命令被它拦截。
- 探针测试应使用只加载 `astrbot_plugin_e2e_probe` 的测试实例，或在测试群禁用 cc-qq。
- 这不是 Docker/NapCat 链路问题；测试 AstrBot 已经收到消息说明链路是通的。

### 重复执行 `start-all.sh` 会不会创建重复容器？

- 不会。`docker compose up -d` 是幂等的。
- 两个容器 + 测试 AstrBot 都在运行时，脚本默认跳过打开新标签；需要新日志窗口加 `--force-tabs`。
- 需要重启加 `--restart`（`docker restart` 容器 + 重启测试 AstrBot），不要进容器 `kill` QQ。

### 关闭终端会不会停服务？

- Docker 容器不会停（由 OrbStack 管理）。
- `start-all.sh` 里的测试 AstrBot 用 `--detach` 后台启动，关闭标签一般不会停。
- 如果手动前台运行 `start-astrbot.sh`（不加 `--detach`），关闭终端可能导致它被 SIGHUP 杀掉。
- 彻底停止用 `stop-all.sh`。

### 端口冲突怎么办？

- 默认端口：OneBot `6200/6201`，WebUI `16299/16398`，测试 AstrBot `6186/6198`。
- 用 `lsof -nP -iTCP:<port> -sTCP:LISTEN` 检查；也可以在 `.env` 中改 WebUI/账号/token（OneBot 端口与 `config.local.json` 需一起改）。
- 生产 Docker 容器使用 `13000/13001/16099`，不要混淆。

### iTerm2 没反应 / 报 `-2741`？

- iTerm2 3.6.7 的 AppleScript **应用名是 `iTerm`，不是 `iTerm2`**；用 `iTerm2` 会报 `-2741`/`-1728`，不会弹终端。
  脚本已改为 `tell application "iTerm"`。
- 首次执行可能提示「终端想控制 iTerm2」，选择允许。
- 不想自动化：用 `--no-iterm`，脚本会打印手动命令。

### 镜像会不会太旧？

- 当前本地镜像 `mlikiowa/napcat-docker:latest` 是 2026-03 构建（NapCat 4.17.46），当前可用。
- 需要更新时：`docker pull mlikiowa/napcat-docker:latest`，然后重启容器并重新验证 `get_rkey` 与图片下载。

## 文件说明

| 文件 | 作用 |
|---|---|
| `compose.yaml` | 两个 NapCat service、端口、卷、注释 |
| `common.sh` | 共享变量、配置生成、预检函数 |
| `start-all.sh` | 一键启动 + iTerm2 三标签 |
| `start-bot.sh` | 单独启动机器人容器 |
| `start-sender.sh` | 单独启动发送者容器 |
| `start-astrbot.sh` | 单独启动测试 AstrBot |
| `stop-all.sh` | 停止容器/测试实例，恢复生产容器 |
| `status.sh` | 容器、端口、WebUI、生产容器状态 |
| `.env.example` | 本地覆盖示例 |
| `.gitignore` | 忽略 `.env` / 日志 / 报告 |

## 排障

- 容器没起来：`docker ps -a`、`docker logs napcat-e2e-bot`。
- 端口冲突：`lsof -nP -iTCP:6200 -sTCP:LISTEN`；检查是否有其他 NapCat/测试实例。
- 扫码后没连上 AstrBot：看测试 AstrBot 日志 `~/.astrbot-e2e/data/logs/astrbot.log`，确认 6198 在监听、反向 token 一致。
- E2E 工具连不上 6200/6201：确认容器端口映射和 `onebot11_<qq>.json` 里的 token；必要时用 WebUI 重新保存网络配置并重启容器。
- 生产容器没恢复：检查 `~/.qq-e2e-docker/production-stopped` 标记，手动 `docker start napcat`，再删除标记。
- `doctor` 通过但 `probe_echo` 失败：检查测试群 `701292201` 是否同时启用了 `astrbot_plugin_cc_qq`。
  cc-qq 会先回「已收到，正在处理，完成后会回复」，探针命令会被它拦截；探针测试应使用只加载
  `astrbot_plugin_e2e_probe` 的测试实例，或在测试群禁用 cc-qq。
- `cc_qq_multi_turn` 的 `/info` 断言仍是旧文案（期望包含 `/new`）；当前实际回复是
  「当前会话 #N，代理：claude，状态：active。」。这是用例断言过期，不是插件故障；
  把断言改为包含「当前会话」或匹配「状态」即可。
- `Server disconnected`：通常是 NapCat 刚重启/重连时的瞬时断连；脚本会自动重试 3 次，
  仍失败可用 `--restart` 重启容器与测试 AstrBot。
