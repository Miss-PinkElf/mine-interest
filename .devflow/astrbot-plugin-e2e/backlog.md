# Backlog（未决问题、首版限定与轻量后续）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 22:40:00 CST。
- 更新时间（Updated At）：2026-10-31 22:55:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录本次对话中未讨论完的问题、首版限定与轻量后续想法，避免只留在聊天里。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：持续维护；候选项不等于已批准方案。
- 文档边界（Scope / Boundary）：未决问题与轻量后续的真相源；明确延期仍以 `deferred/` 为准。

## 未决问题（Open Questions）

| 编号 | 问题 | 现状与影响 | 需要谁决策 | 建议阶段 |
| --- | --- | --- | --- | --- |
| Q1 | 生产 bot `3254276668（17号）` 继续兼任测试机器人，还是改用独立测试机器人？ | 当前测试群消息会进入生产 bot；测试群专用、风险可控，但生产号仍承担测试流量 | 用户 | 第二版前 |
| Q2 | 生产 NapCat 的 `6198` 测试客户端是否长期保留？ | 保留可随时测试；不保留需按备份回滚 `onebot11_3254276668.json` 并重启生产 QQ；测试实例停止时每 30 秒重试 | 用户 | 收尾后 |
| Q3 | 测试 AstrBot 实例是否常驻？ | 当前用例结束即停止；常驻可消除 `6198` 重试，但占资源且需要管理生命周期 | 用户 | 第二版前 |
| Q4 | 根目录 `.gitignore` 的两行忽略规则是否提交？ | 本地已忽略 `tools/astrbot_e2e/config.local.json` 与 `tools/astrbot_e2e/reports/`；按收尾约定未提交，未来 `git add .` 有误提交密钥或证据的风险 | 用户 | 下次提交前 |
| Q5 | 报告保留与脱敏策略？ | `reports/` 本地 gitignored，但含 QQ 号、消息与日志；未定义保留天数、脱敏规则与清理命令 | 用户 | 第二版前 |
| Q6 | LLM 语义判定的稳定性、重试与阈值？ | 当前单次调用 + JSON `pass/reason`；未做多判、重试、分数阈值与模型对比 | 用户/实现 | 第二版 |
| Q7 | 是否支持 Linux/Windows？ | 当前仅验证 macOS 双开路径；`NAPCAT_WORKDIR`、App Sandbox 等平台差异未处理 | 用户 | 有跨平台需求时 |
| Q8 | 测试数据清理策略？ | `~/.astrbot-e2e` 长期保留；未定义重置、清理与磁盘占用上限 | 用户 | 第二版 |
| Q9 | 多插件同时启用时的用例隔离？ | 当前按用例重写 `cc_qq` 配置；多个插件监听同一测试群可能互相干扰 | 实现 | 第二版 |
| Q10 | 日志断言的稳定性？ | 断言依赖插件日志文案与格式；插件改日志会直接破坏用例 | 实现 | 第二版 |
| Q11 | 返回图片卡片的命令如何验证？ | 实测 cc-qq `/help` 返回图片帮助卡片，首版文本断言无法验证；已约定标记 `testability=rich_media` 并跳过自动用例，需要人工确认或实现富媒体断言 | 用户/实现 | 富媒体阶段 |
| Q12 | QQ 7.0.2 + NapCat 的稳定启动方式？ | 实测应用注入后外层签名失效；`codesign --deep` 会破坏 Helper 导致 Worker `SIGKILL`。需要固定「仅外层签名 + 保留 entitlements」或 NapCat 安装器标准流程，并处理 App 管理权限 | 用户/实现 | 环境收尾 |
| Q13 | E2E 是否改用独立测试 bot 账号，允许生产 bot 与测试并行？ | 当前 17号 只能二选一；测试时用 `--stop-production` 停生产容器，测完 `stop-all.sh` 恢复 | 用户 | 需要并行回归时 |
| Q14 | probe 与 cc-qq 如何隔离？ | 测试实例同时加载两个插件时，cc-qq 先回执行回执，`probe_echo` 被拦截；需要 probe-only 测试根或测试群禁用 cc-qq | 实现 | 下次跑 probe 前 |
| Q15 | `cc_qq_multi_turn` 的 `/info` 断言何时更新？ | 实际回复「当前会话 #N…状态」，用例仍期望 `/new`；属于测试资产过期 | 实现 | 下次会话优先 |
| Q16 | Docker 镜像何时升级？ | 本地 `mlikiowa/napcat-docker:latest` 为 2026-03 构建 / NapCat 4.17.46；升级需重验 Packet/rkey/图片下载 | 用户/实现 | 镜像更新时 |
| Q17 | 微信/其他平台 E2E 驱动？ | 当前只有 OneBot/NapCat；微信适配器（`weixin_oc`/`wecom`/公众号）没有 OneBot 驱动，需单独 Align | 用户 | 确定微信渠道后 |
| Q18 | 是否给 `prod.sh` 增加 `restart` 别名与未知命令提示？ | 用户曾误用 `prod.sh --restart` / `prod.sh --staus`；当前只打印 usage。别名可降低误用，但会增加入口语义 | 用户 | 下次使用前 |
| Q19 | `start --restart --no-iterm` 是否要清理旧 iTerm 窗口？ | 该组合会在当前终端前台运行 AstrBot，但旧窗口可能残留 NapCat 日志标签；当前不处理 | 用户 | 需要无 GUI 重启时 |
| Q20 | 生产 NapCat 登录/QQ 安全风险 168 如何恢复？ | 当前 `napcat` 运行但未登录；需用户在最新手机 QQ 按提示恢复账号后扫码 | 用户 | 恢复生产前 |
| Q21 | 生产 AstrBot Dashboard 是否收口到 `127.0.0.1`？ | `~/.astrbot/data/cmd_config.json` 的 `dashboard.host` 为 `0.0.0.0`，日志提示安全风险；本次未改生产配置 | 用户 | 安全加固时 |
| Q22 | 生产 `start` 是否需要顺带停 `napcat-e2e-sender`？ | 发送者 C# 与生产 17号 不冲突，当前只停 `napcat-e2e-bot`；残留发送者容器可能占用 6201/16398 | 用户 | 需要彻底清理 E2E 时 |
| Q23 | 手动关闭 NapCat 日志标签后如何感知？ | 脚本只能按窗口 ID 复用窗口；手动关单个标签无法检测，重启时只补 AstrBot 标签 | 实现 | 下次迭代 |

## 首版限定（First-Version Only，不计划在本版扩展）

以下能力在首版有明确边界，不是缺陷，也不等于永久放弃；是否扩展按上表或 `deferred/` 决定。

| 能力 | 首版边界 | 说明 |
| --- | --- | --- |
| 交互方式 | 只提供 CLI | 没有 WebUI 页面；报告为 JSON/文本证据 |
| 用例模型 | 支持单次 `send` 与多轮 `steps` | 多轮已实现；复杂断言/条件分支仍延期 |
| 执行方式 | 串行 | 不支持并行用例；并行延期 |
| 账号与群 | 单测试群、双账号 | 测试机器人 + 测试发送者；专用测试 bot 未定（Q13） |
| 消息类型 | 文本为主，已有图片/长图用例 | 语音、文件、合并转发等富媒体断言仍延期（Q11） |
| 登录 | 人工扫码 | 不承诺自动登录；QQ 风控与人工确认 |
| 平台 | macOS 宿主 + Docker Linux 容器 | 原生双 QQ 仍作为回退；Windows 未验证 |
| 插件生命周期 | 每轮启动独立测试 AstrBot | `--attach` + `--reload` 可增量验证；常驻策略见 Q3 |
| 生产启动脚本 | 仅 macOS + iTerm2；只管理生产 NapCat/AstrBot | 不管理 E2E 发送者与测试 AstrBot；Linux/Windows 未验证；`--no-iterm` 为终端前台模式 |

## 明确延期（Deferred）

详见：

- `deferred/2026-10-27-post-mvp-deferred.md`：cc_qq 长任务、审批、多轮、富媒体、WebUI、CI、并行、自动登录、更深校验等。
- `deferred/2026-10-27-config-validation-deferred.md`：配置值形状与边界校验。
- `deferred/2026-10-27-case-validation-deferred.md`：用例值形状与边界校验。
- `deferred/2026-10-31-prod-env-deferred.md`：生产启动脚本的别名/提示、无 GUI 重启、自动扫码、Dashboard 收口、跨平台等。

## 轻量后续想法（候选，未批准）

- 用例失败时仅对网络抖动自动重试一次。
- `doctor` 增加 QQ 在线状态与测试群可达性检查。
- 报告生成 HTML 摘要，便于人工查看失败证据。
- 用例支持标签与分组，按插件或风险级别筛选。
- 报告自动脱敏 QQ 号、token 与长消息。
- **需求 2（2026-10-29 用户新增）**：把「启动两个 QQ、暂停生产、按被测插件制定测试流程、产出报告、具备自愈能力、适配不同 NapCat/AstrBot/运行环境」做成通用测试 skill；来源 `zzz-prompt-debug/插件自动化测试验证/prompt-01.md`。**已实施并验证（2026-10-30）**：引擎 127/127；cc-qq 多轮用例 PASSED；文本 suite 2/2 PASSED；报告脱敏通过；端口占用与残留实例两项自愈演练通过。skill 真源在 person-config，本仓库副本已同步。
- E2E 期间自动暂停/恢复生产 AstrBot：当前靠人工暂停；单人使用可接受，高频回归前再自动化。
- Docker 版一键启动脚本已入库：`tools/napcat_e2e/start-all.sh`（iTerm 三标签、`--restart`、`--force-tabs`、`--detach`）；旧原生 `~/.qq-e2e/start-e2e.sh` 保留作回退参考，旧数据已归档到 `~/.qq-e2e/archive-20261031/`。
- Docker 镜像升级、专用测试 bot 账号、微信/其他平台驱动、probe/cc-qq 隔离、`cc_qq_multi_turn` `/info` 断言更新：见 Q13–Q17，均为候选/待办，不是已批准实施项。
- 测试期间需要临时修改测试实例配置（`allowed_work_dirs`、`claude_setting_sources=user`、角色字段）；可评估把这些作为 `run` 的参数或 bootstrap 选项。
- 生产启动脚本可增加 `restart` 别名、未知命令提示（例如提示 `start --restart`）、`status` 短别名；属于 UX 候选，未批准。
- 生产 AstrBot Dashboard 当前监听 `0.0.0.0:6185`；可评估改为 `127.0.0.1`，但会影响远程访问，需用户确认。
- 生产启动前是否顺带停 `napcat-e2e-sender`：当前只停机器人容器，发送者与 17号 不冲突；需要彻底清理 E2E 时再处理。

以上均为候选项（Candidate），不是已批准计划（Plan），也未进入实施（Apply）。
