# 问题清单（Bug Log）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-31 02:31:26 CST。
- 更新时间（Updated At）：2026-10-31 22:55:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录 Docker 双容器 E2E 启动脚本实施与验证中发现的问题、根因与处置。
- 关联仓库或项目（Related Repository / Project）：当前仓库 `.`。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：大部分已修复；1 条测试断言待修；1 条生产登录环境阻塞待用户处理。
- 文档边界（Scope / Boundary）：问题记录，不替代 `state.md` 或 `handoff`。

## B1：`start-instance` 报 `Server disconnected`

- **现象**：`start-instance` 在 6200/6201 已监听后仍失败，日志 `测试实例未就绪: Server disconnected`。
- **原因**：NapCat 容器刚启动/重连时，端口已开但账号 OneBot WS 还没有稳定；`start-instance` 立即连接并校验账号，遇到瞬时断连。
- **处置**：
  - `start-astrbot.sh` 先等待 6200/6201；
  - 新增 `tools/napcat_e2e/wait_onebot.py`，实际连接 OneBot 并校验 `get_login_info.user_id`；
  - `start-instance` 失败自动重试 3 次（间隔 3 秒）；
  - 仍失败用 `start-astrbot.sh --restart` 或 `start-all.sh --restart`。
- **状态**：已修复；2026-10-31 `--restart` 验证成功。

## B2：iTerm AppleScript 报 `-2741` / `-1728`，不弹终端

- **现象**：`start-all.sh` 报 `syntax error: 预期是“,”，却找到类名称。(-2741)`，没有打开 iTerm 标签。
- **原因**：iTerm2 3.6.7 的 AppleScript **应用名是 `iTerm`**，不是 `iTerm2`；`tell application "iTerm2"` 无法解析术语。
- **处置**：`start-all.sh` 改为 `tell application "iTerm"`；并用 `osacompile` 与实跑验证三标签打开。
- **状态**：已修复（2026-10-31 02:45）。

## B3：`probe_echo` 被 cc-qq 拦截

- **现象**：`probe_echo` FAILED，机器人回复「已收到，正在处理，完成后会回复。期间可发送 /! 中断。」，测试 AstrBot 日志有 `[Test-E2E] C#: /e2e_echo hello-e2e`，但没有 `[e2e_probe] echo`。
- **原因**：测试实例同时加载 `astrbot_plugin_cc_qq` 与 `astrbot_plugin_e2e_probe`；cc-qq 先处理该群消息并发送执行回执，探针命令被拦截。
- **处置**：探针测试使用只加载 probe 的测试根，或在测试群禁用 cc-qq；cc-qq 自身用 cc-qq 用例验证。
- **状态**：测试隔离方案待实施（Deferred）。

## B4：`cc_qq_multi_turn` 的 `/info` 断言过期

- **现象**：`/pwd` PASSED；`/info` FAILED，实际回复「当前会话 #5，代理：claude，状态：active。」，用例期望包含 `/new`。
- **原因**：插件 `/info` 文案已变化，用例断言仍是旧版。
- **处置**：把断言改为包含「当前会话」或匹配「状态」；重跑用例。
- **状态**：待修（Pending）。

## B5：手动运行 `astrbot run` 用错根目录

- **现象**：手动执行 `ASTRBOT_ROOT=~/.astrbot-e2e astrbot run` 报 `.../mine-interest-source-hub is not a valid AstrBot root directory`。
- **原因**：AstrBot CLI 的根目录判断实际使用**当前工作目录**；`ASTRBOT_ROOT` 在 CLI 层未按预期生效。
- **处置**：先 `cd ~/.astrbot-e2e` 再运行；`tools/astrbot_e2e` 启动时已设置 `cwd` 为测试根，所以脚本路径正常。
- **状态**：已知限制，文档已记录。

## B6：生产容器与 E2E 机器人抢 17号

- **现象**：生产容器 `napcat` 与 `napcat-e2e-bot` 都登录 17号，不能同时在线。
- **原因**：同一 QQ 账号不能双端在线。
- **处置**：`start-all.sh --stop-production` 停止生产容器并写标记；`stop-all.sh` 恢复生产容器。不要手动同时启动两者。
- **状态**：已处理。

## B7：进容器 `kill` QQ 后容器可能退出

- **现象**：直接 `docker exec ... kill` QQ 进程不可靠；入口脚本没有守护进程。
- **原因**：entrypoint 启动 QQ 后由 bash 等待，kill 后容器可能直接退出。
- **处置**：使用 `docker restart napcat-e2e-bot` / `docker compose restart`，数据卷与登录态保留。
- **状态**：已写入脚本与 README。

## B8：生产 `start` 幂等路径未校验 OneBot 就绪

- **现象**：`napcat` 容器与 AstrBot `6185` 都在运行，但 NapCat 未登录时，`prod.sh start` 只提示「已在运行」并退出 0。
- **原因**：幂等判断只检查容器与 Dashboard 端口，没有检查 OneBot `get_login_info`。
- **处置**：幂等路径增加一次快速 `get_login_info` 检查；未就绪时警告并提示打开 NapCat WebUI。
- **状态**：已修复（2026-10-31）。

## B9：生产 `start` 在 OneBot 超时时仍返回 0

- **现象**：首次 `start` 等待 OneBot 超时后，脚本打印警告但退出码为 0，自动化会误判成功。
- **原因**：`wait_for_onebot` 失败只 `warn`，没有传递到退出码。
- **处置**：默认 iTerm 模式记录 `onebot_ok`；失败时保留服务但 `exit 1`。
- **状态**：已修复（2026-10-31）。

## B10：生产 NapCat 启动后要求扫码，QQ 返回安全风险 168

- **现象**：`napcat` 容器启动后日志显示二维码；扫码前 `get_login_info` 无法返回 17号。日志同时出现「你的账号近期存在安全风险…」错误码 `168`。
- **原因**：QQ 账号侧安全风控，需要用户在最新手机 QQ 按提示恢复；不是脚本或 NapCat 链路故障。
- **处置**：脚本按预期超时并提示 NapCat WebUI；需用户处理账号后扫码，再执行 `prod.sh start` 复测。
- **状态**：待用户处理（Pending，环境侧）。

## B11：生产启动脚本命令形态误用

- **现象**：用户执行 `prod.sh --restart` 与 `prod.sh --staus`，脚本只打印 usage。
- **原因**：`--restart` 是 `start` 的参数，`status` 是子命令；未知参数没有额外提示。
- **处置**：文档与 `NEXT-SESSION-PROMPT` 写明正确用法；是否增加 `restart` 别名与未知命令提示，见 `backlog.md` Q18。
- **状态**：非代码缺陷；候选改进（Candidate）。
