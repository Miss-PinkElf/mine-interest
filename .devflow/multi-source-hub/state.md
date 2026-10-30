# Metadata（元数据）

- 更新时间（Updated At）：2026-10-31 02:31:26 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：提供当前 mission 的短恢复入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38、50–67 行；需求 9 来源见 `origin.md`。
- 最新计划（Latest Plan）：`plans/2026-10-23-需求9-GitHub-star列表归类-plan.md`。
- 最新任务清单（Latest Tasks）：`spec/2026-10-23-需求9/tasks.md`。
- 最新交接（Latest Handoff）：`handoffs/2026-10-30-021-Docker-NapCat迁移与rkey修复.md`。
- 当前状态（Status）：QQ 接入已迁移到 Docker NapCat 并完成转发 3 图端到端验证（`attachments=3`、`gaps=[]`）；需求 8 star/fork 真实验收完成；需求 9 star 列表归类已部署、待真实仓库验证；B 站日志补全待观察。两插件 `github_enabled` 均已打开。
- 文档边界（Scope / Boundary）：本任务记录；不代表需求 4 / 需求 7 已关闭。

# 当前状态（2026-10-30 Docker 迁移后）

- **2026-10-30 QQ 接入迁移到 Docker NapCat（当前运行环境）**：
  - 原因：macOS 原生 QQ `6.9.89-45758` 的签名 entitlements 缺少 `com.apple.security.cs.disable-library-validation`，NapCat `4.18.42` 的 arm64 `napi2native` ad-hoc 模块无法加载 → `packetBackend` 不可用 → 原生 rkey（Rkey）失败 → 两个远程 rkey 服务也失效 → 回退硬编码占位 rkey → `gchat.qpic.cn` 返回 400 `download url has expired` → sourcehub 记为 `media_failed`。经只读验证，**不是代理（Proxy）问题**。
  - 处置：改用 `~/napcat` 的 Docker NapCat（`mlikiowa/napcat-docker:latest`，linux/arm64，NapCat `4.17.46`，登录 17号 `3254276668`）；`Napi2NativeLoader` 与 `PacketHandler` 加载成功，`get_rkey` 返回真实签名。
  - 端口与自启：`127.0.0.1:13000->3000`、`13001->3001`、`16099->6099`（避开 multica 占用的 3000）；`restart: unless-stopped`；备份 `~/napcat/compose.yaml.bak-20261030-181758`。
  - 账号边界：17号 在 Docker；个人号 C# `1961618848` 仍在原生 QQ。切换同 `self_id` 的 NapCat 后**必须重启 AstrBot**，否则旧反向 WebSocket（reverse WebSocket）API 客户端残留会让插件的 `get_forward_msg` 静默失败。
  - 验证：合并转发 3 图条目 `qq:forward:1747617391`，`attachments=3`、`gaps=[]`，3 个媒体哈希均为有效 JPEG。
  - 详见 `handoffs/2026-10-30-021-Docker-NapCat迁移与rkey修复.md`。
  - 原理与证据完整说明见 `notes/2026-10-31-Rkey与Docker-NapCat原理说明.md`。

- 版本：检查插件 `0.6.5`、B 站插件 `0.3.7`；两个现场目录与仓库 `diff -rq` 一致，已验证可编译。全量离线 **174 项通过**（命令须带 `-t .`）。
- 需求 8 验收：star 成功（`Blinue/Magpie`）；fork 成功（`Miss-PinkElf/Magpie`，默认分支 `dev`，`sourcehub-fork-sync.yml` 已安装）。
- 本轮修复：
  - `_github_reply` 布尔属性遮蔽同名方法 → 属性改名 `_github_reply_enabled`，新增静态守卫。
  - `gh repo fork` 误带 `--remote=false` → 去掉该参数，保留 `--clone=false --default-branch-only`。
  - B 站正常流程无日志 → 补充收到通知、开始采集、失败原因、保存成功与 GitHub 动作日志。
- 需求 9：新增 `github_star_list`（两个插件独立配置）。只对本次新 star 生效；按名称完全匹配；加入目标列表时保留其他列表；留空/不匹配/查询失败回退默认位置。REST 无 Lists 接口，使用 `gh api graphql`。
- 代码提交：`b9ef0fc`（需求 8 首版）；本轮修复与需求 9 已在收尾时提交，未推送（提交号见 `git log`）。
- 现场配置：owner `1961618848`、admin `2844973553`，`github_enabled=true`，代理 `http://127.0.0.1:7897`；`github_star_list` 尚未填写。
- 备份：`~/.astrbot/data/plugin-backup-20261023-112324/`。

## 下一步

1. 需求 9 真实验证：重载两插件 → 填写 `github_star_list`（现有列表：自动化日常、AI相关、Useful、Want to Learn）→ 用尚未 star 的仓库验证「已加入列表」且其他列表保留。
2. B 站日志观察：重载后在 B 站 @ 机器人，确认「收到 N 条 B 站通知」「开始采集」「已保存」出现。
3. 老账：需求 4 Verify、需求 7 Close、需求 8 T7 勾选、`@机器人 整理` 端到端。
4. QQ 接入：确认 Docker NapCat 容器 `napcat` 运行、AstrBot `Test-01` 只连 Docker 的 17号；重启 AstrBot 后等 30 秒让 NapCat 反向 WebSocket 重连，再做转发验证。

## 本轮不做 / 后续阶段（Deferred Scope）

- **E2E Docker 双容器启动脚本（归属 `.devflow/astrbot-plugin-e2e/`）**：已实现于 `tools/napcat_e2e/`（两个 NapCat 容器 + 测试 AstrBot）；本 mission 只保留 QQ 接入/rkey 文档，不重复维护脚本。详见 `.devflow/astrbot-plugin-e2e/handoffs/2026-10-31-003-Docker双容器E2E启动脚本.md`。
- **专用测试 bot 账号（Deferred）**：当前 17号 只能「生产或 E2E」二选一；E2E 时用 `--stop-production` 停生产容器，恢复用 `stop-all.sh`。需要生产与测试并行时再新增专用账号与独立适配器。
- **微信渠道适配（Deferred）**：AstrBot 有 `weixin_oc` / `wecom` / 公众号适配器，但 sourcehub/cc-qq 当前依赖 QQ/OneBot 的转发、图片与群语义；接微信需要单独 Align，不能直接换渠道。
- **Docker 镜像升级（Deferred）**：当前 `mlikiowa/napcat-docker:latest` 为 2026-03 构建 / NapCat 4.17.46；升级后需重验 Packet/rkey/图片下载。
- **插件转发展开健壮性（待写 Plan，未批准）**：`forward_expander.fetch_forward_messages` 增加短重试（建议 3 次、间隔 1 秒），并在最终失败时把 `forward_unexpanded` 写入 `gaps`，避免当前 `except Exception: continue` 静默吞掉异常、只留下「转发消息获取失败」告警。触发场景：转发资源尚未就绪、反向 WebSocket API 短暂不可用、同 `self_id` 旧连接残留。状态：2026-10-30 记录，**未写 Plan、未改代码**；获用户批准后再按 devflow 落 `plans/` 并实施。
- star 列表：历史已 star 仓库批量归类、自动创建不存在的列表、超过 100 条目的完整分页、slug/别名/模糊名称匹配；详见 `deferred/需求9-star列表首版边界.md`。
- 需求 8 原有延期不变：QQ 合并转发内层链接、fork 冲突自动解决、私有上游同步、同步频率配置化。
- 详见 `deferred/需求8首版边界与待验收.md` 与 `deferred/需求9-star列表首版边界.md`。
