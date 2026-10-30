# Metadata（元数据）

- 更新时间（Updated At）：2026-10-30 18:45:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录最近三个检查点。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：QQ 接入已迁移到 Docker NapCat，转发 3 图验证通过；需求 8 star/fork 已真实验收；需求 9 已部署，待真实列表归属验证。
- 文档边界（Scope / Boundary）：本任务记录；不代表需求 9 的真实列表归属已验证。

# 最近检查点

## 2026-10-30 18:45:00 +08:00：QQ 接入迁移到 Docker NapCat，转发 3 图验证通过

- 根因：macOS QQ `6.9.89-45758` 缺 `disable-library-validation` → NapCat native Packet 不可用 → 占位 rkey → 腾讯 400；**不是代理（Proxy）问题**。
- 处置：Docker NapCat（`mlikiowa/napcat-docker:latest`，NapCat `4.17.46`，17号 `3254276668`）接管；`Napi2NativeLoader`/`PacketHandler` 加载成功，`get_rkey` 返回真实签名。
- 二次故障：切换同 `self_id` 账号后旧反向 WebSocket API 客户端残留，插件 `get_forward_msg` 静默失败；重启 AstrBot 后恢复。
- 验证：`qq:forward:1747617391`，`attachments=3`、`gaps=[]`，3 个媒体均为有效 JPEG。
- 端口：`13000/13001/16099`；`restart: unless-stopped`；备份 `~/napcat/compose.yaml.bak-20261030-181758`。
- 延期：`fetch_forward_messages` 短重试 + `forward_unexpanded` gap（待 Plan，未批准）。
- 详见 `handoffs/2026-10-30-021-Docker-NapCat迁移与rkey修复.md`。

## 2026-10-23 17:02:00 +08:00：需求 9 star 列表归类已实施

- 新能力：`github_star_list` 配置；新 star 的仓库按名称加入 GitHub Lists；保留原有其他列表；留空、不匹配、分页截断或 GraphQL 失败时回退默认位置。
- 实现：REST 无 Lists 接口（`/user/lists` 404），改用 `gh api graphql` 的 `viewer.lists` 与 `updateUserListsForItem`。
- 版本与部署：检查插件 `0.6.5`、B 站 `0.3.7`；两个现场目录 `diff -rq` 一致，`py_compile` 通过。
- 测试：全量离线 **174 项通过**（新增 6 项列表行为测试）。
- **下一步**：重载两个插件 → 在插件页填写 `github_star_list`（本机现有列表：自动化日常、AI相关、Useful、Want to Learn）→ 用新仓库链接验证列表归属与其他列表保留。

## 2026-10-23 16:36:00 +08:00：补全 B 站插件正常流程日志

- 问题：B 站插件只有异常时才写日志，收到 @、开始采集、保存成功都没有记录，平台日志里看不到运行状态。
- 修法：`Poller.scan` 记录收到数量；`Poller.process` 记录开始采集、采集失败原因、保存成功；GitHub 动作日志统一加 `[SourceHub Bilibili]` 前缀；自动化关闭但检测到链接时记录跳过原因。
- 版本与部署：B 站插件 `0.3.6`，现场目录已覆盖且 `diff -rq` 一致；新增 4 项日志测试，全量离线 **168 项通过**。
- **下一步**：重载 B 站插件 → 在 B 站 @ 机器人 → 平台日志应出现「收到 N 条 B 站通知」「开始采集 B 站通知：…」「已保存 B 站条目：…」。

