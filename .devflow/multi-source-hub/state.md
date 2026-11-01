# Metadata（元数据）

- 更新时间（Updated At）：2026-11-01 13:00:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：提供当前 mission 的短恢复入口。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38、50–67 行；需求 9 来源见 `origin.md`。
- 最新计划（Latest Plan）：`plans/2026-11-01-需求9-fix-star列表mutation返回字段-plan.md`。
- 最新任务清单（Latest Tasks）：`spec/2026-10-23-需求9/tasks.md`。
- 最新交接（Latest Handoff）：`handoffs/2026-11-01-022-star列表mutation修复与历史补做.md`。
- 当前状态（Status）：需求 9 的列表归类缺陷已修复并部署（检查插件 `0.6.6`、B 站 `0.3.8`）；历史 5 个仓库已补做归类；**待重载 AstrBot 并用新仓库做消息链路端到端验证**。
- 文档边界（Scope / Boundary）：本任务记录；不代表需求 4 / 需求 7 已关闭。

# 当前状态（2026-11-01 星标列表修复后）

- **需求 9 两个根因（均已解决）**：
  1. mutation 选择集写成 `list { id name }`，而 `UpdateUserListsForItemPayload` 只有 `lists` 字段 → GraphQL 校验整体拒绝，列表从未写入。
  2. gh token 缺 `user` scope → `INSUFFICIENT_SCOPES`；此前被 `undefinedField` 遮蔽。用户已执行 `gh auth refresh -h github.com -s user`，scopes 现含 `user`。
- **修复内容**：模板改 `lists`；mutation 复用 `_graphql` 统一解析 `errors`；新增 2 条回归测试；全量离线 **176 项通过**；三副本字节一致，现场目录 `diff -rq` 一致，`py_compile` 通过。
- **历史补做（真实副作用，已完成）**：
  - `bilibili_star`：`ssamurias/dsh-fish`、`Mieksido/surfcore`、`SAOS-3624/dsh-video-storyboard`、`foxletters-hq/BaiShou-Next`。
  - `qq_star`：`shareAI-lab/learn-claude-code`。
  - `viewer.lists` 复核：`bilibili_star`=4、`qq_star`=1；`自动化日常`=4、`AI相关`=9、`Useful`=8、`Want to Learn`=9，原有归属未变。
- **QQ 侧说明**：检查插件与 B 站插件共用同一个 `sourcehub/github_actions.py`，一次修复两边同时生效，无需单独修 QQ。
- **现场配置**：B 站 `github_star_list=bilibili_star`、检查插件 `github_star_list=qq_star`；`github_enabled=true`；代理 `http://127.0.0.1:7897`。
- **代码提交**：`23e0bef`（本次修复与回归测试），未推送。
- **运行环境**：QQ 接入仍在 Docker NapCat（`~/napcat`，17号 `3254276668`，端口 `13000/13001/16099`）；切换同 `self_id` 后必须重启 AstrBot。

## 下一步

1. 重载 AstrBot，确认加载 `astrbot_plugin_sourcehub_inspector (0.6.6)` 与 `astrbot_plugin_sourcehub_bilibili (0.3.8)`；日志出现「GitHub 自动化：开」。
2. 用**尚未 star** 的仓库链接分别经 QQ 与 B 站触发，确认回复「已 star（已加入列表「qq_star」/「bilibili_star」）」，且其他列表保留。
3. B 站日志观察：确认「收到 N 条 B 站通知」「开始采集 B 站通知」「已保存 B 站条目」。
4. 老账：需求 4 Verify、需求 7 Close、需求 8 T7 勾选、`@机器人 整理` 端到端。
5. QQ 接入：确认 Docker NapCat 容器运行，重启 AstrBot 后等 30 秒让反向 WebSocket 重连。

## 本轮不做 / 后续阶段（Deferred Scope）

- **star 列表历史批量归类**：本轮只补了 5 个已知遗漏，未做全量整理；触发条件：用户明确要求整理全部历史 star。
- **自动创建不存在的列表**：暂不做，避免拼写错误生成多余列表；触发条件：用户要求按名称自动建列表。
- **超过 100 条目/100 个列表的完整分页**：暂不做，截断时放弃归属；触发条件：真实规模超上限。
- **slug/别名/模糊名称匹配**：暂不做；触发条件：用户要求更宽松匹配。
- **列表移除、列表改名同步**：暂不做；触发条件：用户另行提出。
- **一个插件配置多个列表 / 按来源或链接类型分流**：未讨论；触发条件：用户提出。
- **E2E Docker 双容器启动脚本**：归属 `.devflow/astrbot-plugin-e2e/`，本 mission 不重复维护。
- **专用测试 bot 账号（Deferred）**：当前 17号 只能「生产或 E2E」二选一。
- **微信渠道适配（Deferred）**：需单独 Align。
- **Docker 镜像升级（Deferred）**：升级后需重验 Packet/rkey/图片下载。
- **插件转发展开健壮性（待写 Plan，未批准）**：`fetch_forward_messages` 短重试 + `forward_unexpanded` gap。
- 需求 8 原有延期不变：QQ 合并转发内层链接、fork 冲突自动解决、私有上游同步、同步频率配置化。
- 详见 `deferred/需求9-star列表首版边界.md` 与 `deferred/需求8首版边界与待验收.md`。
