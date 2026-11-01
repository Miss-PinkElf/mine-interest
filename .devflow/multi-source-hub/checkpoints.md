# Metadata（元数据）

- 更新时间（Updated At）：2026-11-01 13:00:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：记录最近三个检查点。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：需求 9 列表归类缺陷已修复并部署；历史 5 个仓库已补做；待重载后做消息链路端到端验证。
- 文档边界（Scope / Boundary）：本任务记录；不代表需求 9 的消息链路端到端已验证。

# 最近检查点

## 2026-11-01 13:00:00 +08:00：star 列表 mutation 修复与历史补做

- 根因一：mutation 选择集写 `list`，而 `UpdateUserListsForItemPayload` 只有 `lists` → GraphQL 校验整体拒绝，列表从未写入。
- 根因二：gh token 缺 `user` scope，被 `undefinedField` 遮蔽；用户执行 `gh auth refresh -h github.com -s user` 后解除。
- 修复：模板改 `lists`；mutation 复用 `_graphql` 统一解析 `errors`；新增 2 条回归测试；全量离线 **176 项通过**。
- 版本与部署：检查插件 `0.6.6`、B 站 `0.3.8`；三副本字节一致；现场 `diff -rq` 一致；`py_compile` 通过。
- 历史补做：5 个仓库全部成功；`bilibili_star`=4、`qq_star`=1；其他 4 个列表条目数未变。
- 提交：`23e0bef`（未推送）。
- **下一步**：重载 AstrBot → 用尚未 star 的仓库经 QQ / B 站触发，验证消息链路端到端。
- 详见 `handoffs/2026-11-01-022-star列表mutation修复与历史补做.md`。

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
- 当时下一步：重载两个插件 → 填写 `github_star_list` → 用新仓库验证列表归属，后续由 2026-11-01 检查点接管。
