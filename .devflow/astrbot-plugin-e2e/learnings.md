# 经验记录（Learnings）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-31 02:31:26 CST。
- 更新时间（Updated At）：2026-10-31 22:55:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：沉淀 Docker 双容器 E2E 启动与排障中可复用的技术经验。
- 关联仓库或项目（Related Repository / Project）：当前仓库 `.`。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：已记录（Recorded）。
- 文档边界（Scope / Boundary）：经验参考，不是强制规范。

## 经验条目

1. **端口监听 ≠ 账号就绪**：NapCat 刚启动/重连时 6200/6201 可能已监听，但 OneBot WS 还不稳定。就绪探测应实际调用 `get_login_info` 并校验 `user_id`，而不是只 `lsof` 端口。
2. **启动顺序要显式等待**：测试 AstrBot 的 `start-instance` 依赖 6200/6201；应在账号就绪后再调用，失败时做有限重试，避免一次瞬断就失败。
3. **iTerm2 3.6.7 的 AppleScript 应用名是 `iTerm`**：用 `tell application "iTerm2"` 会报 `-2741`/`-1728`；脚本已统一。
4. **AstrBot CLI 根目录按 cwd 判断**：手动 `astrbot run` 要先 `cd ~/.astrbot-e2e`；虽然设置了 `ASTRBOT_ROOT`，CLI 实际仍以当前工作目录为准。
5. **Docker 容器重启用 `docker restart`**：不要进容器 `kill` QQ；入口脚本没有守护进程，kill 后容器可能退出。
6. **同一 QQ 不能双端在线**：生产 `napcat` 与 E2E `napcat-e2e-bot` 都用 17号 时必须停一个；`--stop-production` + `stop-all.sh` 成对使用。
7. **测试实例插件隔离**：同一测试群同时启用 cc-qq 与 probe 时，cc-qq 的执行回执会拦截探针命令；探针测试需 probe-only 或在群内禁用 cc-qq。
8. **iTerm 标签前缀**：OSC 1337 颜色/徽章/标题需要正确转义，不能把 `\033` 交给外层 `printf` 解释；原 `~/.qq-e2e/start-e2e.sh` 的写法可复用。
9. **生产 NapCat 持久登录态不等于免扫码**：即使 `~/napcat/ntqq` 保存了账号，Docker NapCat 仍可能走二维码登录；本次 QQ 返回安全风险 `168`，需手机 QQ 恢复账号后才能登录。
10. **前台服务用 `echo $$ > pid && exec` 记录 PID**：在 iTerm 标签里执行 `cd ~/.astrbot && echo $$ > .prod-run.pid && exec astrbot run`，`exec` 后 PID 文件仍指向 AstrBot；关闭标签由 SIGHUP 停服务，`stop` 仍可按 PID 兜底。
11. **先停服务再关 iTerm 窗口**：窗口里还有 `sleep`/长任务时 `close window` 可能弹确认并阻塞；`prod.sh stop` 先停 AstrBot 与容器，`docker logs -f` 随容器停止退出，再关窗口更稳。
12. **iTerm 窗口 ID 可内部复用**：用 `~/.astrbot/.prod-iterm-window-id` 记录窗口 ID，重启时在原窗口新增标签；不需要给标签起可见名字。窗口被手动关闭时校验失败，自动新建。
13. **`docker compose restart` 保持容器 ID**：`docker logs -f` 标签可以继续跟随；若用 `down`/`up` 重建容器，旧日志标签会失效。
14. **生产启动脚本用幂等 start + 显式 restart**：每次 `start` 都重启会误触打断生产对话；只补齐缺失服务更安全。
15. **命令形态要直白**：用户容易把 `--restart` 当成子命令、把 `status` 写成 `--staus`；未知命令应给出明确提示和示例。
