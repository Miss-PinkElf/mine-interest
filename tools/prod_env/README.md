# 生产环境一键脚本（NapCat + AstrBot）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-31 23:05:00 +08:00
- 更新时间（Updated At）：2026-10-31 23:05:00 +08:00
- 作者（Author）：rin（Claude 协助）
- 目的（Purpose）：用一个脚本启动/停止生产 NapCat 容器与生产 AstrBot（CLI），并与 `tools/napcat_e2e` 的 E2E 环境划清边界。
- 关联仓库或项目（Related Repository / Project）：`mine-interest-source-hub`（`.`）
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`
- 关联计划（Related Plan）：`.devflow/astrbot-plugin-e2e/plans/2026-10-31-生产环境一键启动脚本-plan.md`
- 当前状态（Status）：已实现（Implemented）
- 文档边界（Scope / Boundary）：使用说明；生产数据与运行时配置以 `~/napcat`、`~/.astrbot` 为准。

## 作用

`tools/prod_env/prod.sh` 管理生产侧的两个服务：

| 角色 | 实际对象 | 端口 |
|---|---|---|
| 生产 NapCat（17号） | `~/napcat` 下的容器 `napcat` | OneBot `13001`、WebUI `16099` |
| 生产 AstrBot | `~/.astrbot`，CLI `astrbot run` | Dashboard `6185`、反向 WS `6199` |

它**不管理** E2E 环境（`napcat-e2e-bot` / `napcat-e2e-sender` / `~/.astrbot-e2e`）。

## 快速开始

```bash
cd /Users/mobius/Documents/111AAA-code/mine-interest.worktrees/mine-interest-source-hub

# 启动（幂等；已运行则不动）
bash tools/prod_env/prod.sh start

# 显式重启
bash tools/prod_env/prod.sh start --restart

# 不开 iTerm：在当前终端前台运行 AstrBot
bash tools/prod_env/prod.sh start --no-iterm

# 状态
bash tools/prod_env/prod.sh status

# 停止
bash tools/prod_env/prod.sh stop
```

## 启动后的 iTerm2 表现

默认会打开 **一个窗口、两个标签**，不设置自定义标签名：

| 标签 | 运行内容 | 关闭标签的影响 |
|---|---|---|
| 1 | `docker logs -f --tail 200 napcat` | 只关闭日志，不影响 NapCat 容器 |
| 2 | `cd ~/.astrbot && echo $$ > .prod-run.pid && exec astrbot run` | **AstrBot 前台运行，关闭标签即停止服务** |

- 窗口 ID 记录在 `~/.astrbot/.prod-iterm-window-id`，只用于内部复用，不显示为标签名。
- `start --restart` 复用同一个窗口：旧 AstrBot 标签关闭后，在原窗口新增一个 AstrBot 标签；NapCat 日志标签继续跟随。
- 窗口被手动关闭后，下次启动会新建一个双标签窗口。
- 未安装 iTerm.app 或 AppleScript 失败时，脚本打印手动命令并以非 0 退出；NapCat 容器可能已启动。

## 重复执行与重启

`start` 是**幂等**的：

- NapCat 与 AstrBot 都在运行：打印「已在运行」和入口，退出 0；不重启、不新增进程、不新增标签。
- 只有一边在运行：只补齐缺失的一边；不重启已在运行的一边。
- 需要重启：必须显式加 `--restart`。

`--restart` 的动作：

1. 按 `~/.astrbot/.prod-run.pid` 停生产 AstrBot（旧标签关闭）；
2. `docker compose restart napcat`（登录态保留，NapCat 日志标签继续）；
3. 在原 iTerm 窗口新增 AstrBot 标签；
4. 等待 `6185/6199` 与 OneBot 就绪。

如果 `6185` 被 AstrBot 桌面 App 或其他未知进程占用、又没有有效的 PID 文件，`--restart` 会**拒绝执行**，不会杀未知进程。

## 可覆盖变量

一般不需要改；特殊环境下可在命令前临时覆盖：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `PROD_COMPOSE_DIR` | `~/napcat` | 生产 compose 与配置目录 |
| `PROD_CONTAINER` | `napcat` | 生产容器名 |
| `PROD_ASTRBOT_ROOT` | `~/.astrbot` | 生产 AstrBot 数据根 |
| `PROD_ASTRBOT_PORT` | `6185` | AstrBot Dashboard 端口 |
| `PROD_ASTRBOT_REVERSE_PORT` | `6199` | AstrBot 反向 WS 端口（仅状态展示） |
| `PROD_QQ` | `3254276668` | 生产 QQ；决定读取哪个 `onebot11_<qq>.json` |
| `ASTRBOT_BIN` | 自动查找 `astrbot` | AstrBot CLI 路径 |
| `ASTRBOT_WAIT_SECONDS` | `120` | 等待 Dashboard 上线秒数 |
| `ONEBOT_WAIT_SECONDS` | `600` | 等待 OneBot 登录就绪秒数 |

## 停止

`stop` 会：

1. 停生产 AstrBot（PID 文件对应的进程；没有 PID 时不杀未知进程，只提示）；
2. `docker compose stop napcat`（保留容器与数据卷）；
3. 关闭脚本创建的 iTerm 窗口，清理窗口 ID 与 PID 文件。

`stop` **不会**停止 E2E 容器和测试 AstrBot。

## 状态文件

| 文件 | 作用 |
|---|---|
| `~/.astrbot/.prod-run.pid` | 前台 AstrBot 的 PID；由标签里的 shell 写入 |
| `~/.astrbot/.prod-iterm-window-id` | 脚本创建的 iTerm 窗口 ID，用于重启复用 |

两者都在生产数据根下，不入库；`stop` 会清理。

## 与 E2E 的边界

| 脚本 | 负责 | 不负责 |
|---|---|---|
| `tools/napcat_e2e/start-all.sh` | E2E 两容器 + 测试 AstrBot；`--stop-production` 停生产并写标记 | 不启动生产 AstrBot |
| `tools/napcat_e2e/stop-all.sh` | 停 E2E 两容器 + 测试 AstrBot；按标记恢复生产容器 | 不停止生产 AstrBot |
| `tools/prod_env/prod.sh` | 生产 `napcat` + 生产 AstrBot；启动前自动停 E2E 机器人 | E2E 发送者、测试 AstrBot、测试用例 |

规则：

1. 同一个 17号 只能一套在线；`prod.sh start` 检测到 `napcat-e2e-bot` 会自动 `docker stop` 它。
2. `~/.qq-e2e-docker/production-stopped` 标记由 E2E 写入；`prod.sh start` 成功启动生产后会清理过期标记。
3. `prod.sh stop` 不写、不删标记，只提示。

## 常见问题（FAQ）

### `start` 重复执行会重启吗？

不会。`start` 只保证服务在运行；重启用 `start --restart`。

### 关闭 AstrBot 标签后服务还在吗？

不在。AstrBot 在前台标签运行，关闭标签会发送 SIGHUP 并停止服务。之后用 `prod.sh start` 可重新拉起。

### 关闭 NapCat 日志标签会停容器吗？

不会。NapCat 是 Docker 容器；停止容器用 `prod.sh stop` 或 `docker compose stop napcat`。

### 提示 6185 被占用、`--restart` 拒绝执行？

通常是 AstrBot 桌面 App 占用了同一数据根。请先退出桌面 App，再执行 `prod.sh start --restart`。

### 等待 OneBot 超时？

打开脚本打印的 NapCat WebUI（默认 `http://127.0.0.1:16099/webui`）检查是否需要重新扫码。脚本不会自动登录。

### 脚本为什么自动停 E2E 机器人？

生产 NapCat 和 E2E 机器人登录同一个 17号，不能同时在线。启动生产前停止 E2E 机器人是既定策略；如果正在跑 E2E 用例会被中断。

### 窗口 ID 记录失效怎么办？

手动关闭窗口后 ID 会过期；脚本检测不到窗口时会自动新建并覆盖记录。也可以删除 `~/.astrbot/.prod-iterm-window-id` 强制新建。

## 验证入口

```bash
bash -n tools/prod_env/prod.sh
bash tools/prod_env/prod.sh status
bash tools/prod_env/prod.sh start
bash tools/prod_env/prod.sh status
bash tools/prod_env/prod.sh start          # 幂等：应提示已在运行
bash tools/prod_env/prod.sh start --restart
bash tools/prod_env/prod.sh stop
```

## 本轮不做 / 后续阶段（Deferred）

- 自动扫码登录、登录态失效通知。
- iTerm 标签命名、颜色、徽章等个性化设置（按需求不做）。
- E2E 脚本自动暂停/恢复生产 AstrBot。
- 微信等其他平台的启动编排。
