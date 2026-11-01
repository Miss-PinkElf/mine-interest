# Metadata（元数据）

- 创建时间（Created At）：2026-10-23 17:05:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：跟踪需求 9「star 列表归类」的实施任务与验证证据。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联 mission（Related Mission）：`.devflow/multi-source-hub/`。
- 关联计划（Related Plan）：`plans/2026-10-23-需求9-GitHub-star列表归类-plan.md`。
- 当前状态（Status）：实施中（In Progress）；2026-11-01 修复 mutation 返回字段并完成真实补做，待重载后做消息链路验证。
- 文档边界（Scope / Boundary）：当前切片任务真相源；勾选只代表对应证据已存在。

# Tasks（实施任务）

- [x] T1：共享库新增 GraphQL 调用、列表查询与归属 mutation，保留其他列表；三副本字节一致。证据：`tests/test_github_actions.py` 6 项新测试通过。
- [x] T2：检查插件接入 `github_star_list` 配置并传给 `GithubAutomation`。
- [x] T3：B 站插件接入 `github_star_list` 配置并传给 `GithubAutomation`。
- [x] T4：两个 `_conf_schema.json` 与 README 补充配置说明。
- [x] T5：版本与部署。检查插件 `0.6.5`、B 站 `0.3.7`；两个现场目录 `diff -rq` 一致；`py_compile` 通过；全量离线 **174 项通过**。
- [x] T6a：真实 GraphQL mutation 验证（2026-11-01）：`gh auth refresh -h github.com -s user` 后，对 5 个已 star 未归类仓库一次性补做，全部成功；`viewer.lists` 核对 `bilibili_star`=4、`qq_star`=1，其他 4 个列表条目数未变。证据：`bug-log.md` 2026-11-01 条目、`plans/2026-11-01-需求9-fix-star列表mutation返回字段-plan.md`。
- [ ] T6b：重载 AstrBot 后，用**尚未 star** 的仓库经 QQ 消息与 B 站 @ 各触发一次，确认回复「已 star（已加入列表「…」）」且其他列表保留。需要用户提供测试仓库链接（会产生真实副作用）。

## 验证边界

- 列表匹配为**名称完全匹配**；留空、找不到、分页截断、GraphQL 失败均回退或跳过，不阻塞 star。
- 已 star 的仓库不重新查询列表，也不移动历史归属。
- 列表数量或单列表条目超过 100 时放弃归属，避免误删手动归属。

## 延期（Deferred Scope）

- 历史已 star 仓库的批量归类；触发条件：用户明确要求整理历史 star。
- 自动创建不存在的列表；触发条件：用户要求按名称自动建列表。
- 超过 100 条目的完整分页；触发条件：真实列表规模超过上限。
- slug/别名/模糊名称匹配；触发条件：用户要求更宽松匹配。
