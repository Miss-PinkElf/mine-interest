# Metadata（元数据）

- 更新时间（Updated At）：2026-11-01 13:00:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：给新对话的可复制恢复提示。
- 关联仓库（Related Repository / Project）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：需求 9 star 列表归类缺陷已修复并部署，历史 5 个仓库已补做；待重载后做消息链路验证。
- 文档边界（Scope / Boundary）：提示词，不是任务真相源。以 `state.md`、`checkpoints.md`、`spec/2026-10-23-需求9/tasks.md`、`spec/2026-10-23-需求8/tasks.md` 为准。

# 下次对话提示

先读 `.devflow/multi-source-hub/state.md`、`checkpoints.md`、`handoffs/2026-11-01-022-star列表mutation修复与历史补做.md`；需求 9 读 `plans/2026-11-01-需求9-fix-star列表mutation返回字段-plan.md`、`plans/2026-10-23-需求9-GitHub-star列表归类-plan.md` 与 `spec/2026-10-23-需求9/tasks.md`；需求 8 读 `spec/2026-10-23-需求8/tasks.md`。需要完整过程时读 `development-overview.md`；溯源时读 `origin.md`、`state-history.md`、`decision-log.md`、`deferred/`。

## 当前进度（2026-11-01）

- 已部署：检查插件 `0.6.6`、B 站插件 `0.3.8`；三副本字节一致；现场目录 `diff -rq` 一致；`py_compile` 通过。
- 已有环境：QQ 接入在 Docker NapCat（`~/napcat`，17号 `3254276668`，端口 `13000/13001/16099`，`restart: unless-stopped`）；切换同 `self_id` 后必须重启 AstrBot。
- 现场配置：B 站 `github_star_list=bilibili_star`、检查插件 `github_star_list=qq_star`；`github_enabled=true`；代理 `http://127.0.0.1:7897`；`gh` 账号 `Miss-PinkElf`，scopes 已含 `user`。
- 需求 9 修复：mutation 选择集 `list` → `lists`；mutation 复用 `_graphql` 解析 `errors`；新增 2 条回归测试；全量离线 **176 项通过**。
- 历史补做：`bilibili_star` 补入 4 个仓库、`qq_star` 补入 1 个；`viewer.lists` 核对其他 4 个列表条目数未变。
- 代码提交：`23e0bef`，未推送。

## 下一步（按顺序）

1. 重载 AstrBot，确认加载 `astrbot_plugin_sourcehub_inspector (0.6.6)` 与 `astrbot_plugin_sourcehub_bilibili (0.3.8)`；日志应出现 `GitHub 自动化：开`。
2. 用**尚未 star** 的仓库链接分别经 QQ 消息与 B 站 @ 触发，确认回复「已 star（已加入列表「qq_star」/「bilibili_star」）」，并且原有其他列表保留。
3. B 站日志观察：确认出现「收到 N 条 B 站通知」「开始采集 B 站通知」「已保存 B 站条目」。
4. QQ 接入：确认 Docker NapCat 容器运行；重启 AstrBot 后等 30 秒让反向 WebSocket 重连。
5. 继续老账：需求 4 Verify、需求 7 Close、需求 8 T7 勾选、`@机器人 整理` 端到端。

## 未讨论 / 只做第一版 / 明确延期

- **历史已 star 仓库的全量批量归类**：本轮只补了已知失败的 5 个仓库，不做全量整理；触发条件：用户明确要求。
- **自动创建不存在的列表**：暂不做，避免拼写错误生成多余列表。
- **超过 100 条目/100 个列表的完整分页**：暂不做，截断时放弃归属。
- **slug/别名/模糊名称匹配**：暂不做，名称必须完全匹配。
- **列表移除、列表改名同步**：暂不做。
- **一个插件配置多个列表 / 按来源或链接类型分流**：**未讨论**；当前是「每个插件一个列表」。
- **插件转发展开健壮性**：`fetch_forward_messages` 短重试 + `forward_unexpanded` gap；**未写 Plan、未批准**。
- 需求 8 原有延期：QQ 合并转发内层链接、fork 冲突自动解决、私有上游同步、同步频率配置化。
- 详见 `deferred/需求9-star列表首版边界.md` 与 `deferred/需求8首版边界与待验收.md`。

## 仍然开放的老账

- 需求 4 Verify 未关；需求 7 未 Close；需求 8 T7 未勾选。
- `@机器人 整理` 端到端确认仍未做（来自 014 交接）。
- 暂缓未变：`remote_private_unverified`、B 站直连 DNS、旧文档重采、超过 100MB 的视频、未识别 `link_type`、`BV1aVjMzeE96`。

## 不要做

- 未获用户允许不要 commit 或推送。
- 不要顺手提交 `.claude/settings.local.json`、`.vscode/controlled-explorer.json`、`zzz-prompt-debug/*`、`.claude/skills/rc-draw-generate/*`。
- 不要修改 NapCat、`devflow-handoff.md`（只读）或 B 站/QQ 之外的插件。
- 不要把 QQ 合并转发内层链接纳入 GitHub 自动化；本轮已明确延期。
- 不要用真实仓库做离线测试；离线测试使用假 runner。真实 star/列表验证需用户确认仓库与列表。
- 补做历史仓库时复用 `_assign_star_list`，不要手工在 GitHub 页面拖动；GitHub Lists 写操作需要 `user` scope。
