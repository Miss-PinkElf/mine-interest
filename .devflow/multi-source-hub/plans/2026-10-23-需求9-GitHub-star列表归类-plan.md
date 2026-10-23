# Metadata（元数据）

- 创建时间（Created At）：2026-10-23 16:51:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：把自动 star 的仓库按配置归入 GitHub Lists（星标列表），并提供默认回退。
- 关联仓库（Related Repository / Project）：mine-interest-source-hub（`.`）。
- 关联 mission（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：2026-10-23 用户会话「gh star 时放到不同的 star 文件夹，可配置；不填或不匹配走默认；两个插件都要」。
- 当前状态（Status）：计划中（Planned），待实施。
- 文档边界（Scope / Boundary）：本文件是本次实施计划；实施结果以 `tasks.md`、`bug-log.md` 和交接为准。

# 需求 9：GitHub star 列表归类

## 一、目标

自动 star 仓库时，如果配置了目标 GitHub Lists（星标列表）名称，就把该仓库加入对应列表；未配置、名称不匹配或列表查询失败时，仍然完成普通 star（默认位置），不阻塞原流程。检查插件（QQ）与 B 站插件共用同一套实现。

## 二、已确认的行为决策

| 决策点 | 结论 |
| --- | --- |
| 已 star 的仓库 | 只在本次**新 star** 时加入列表；已有 `starred_at` 的仓库保持「已经 star，跳过」，不移动历史 star |
| 已属于其他列表 | **保留其他列表**：先查当前归属，再与目标列表取并集，不覆盖移除 |
| 列表匹配方式 | 按列表**名称完全匹配**（去除首尾空白）；不区分大小写以外的模糊匹配不做 |
| 名称找不到 | 正常 star，回复中说明「列表不存在，放入默认位置」 |
| 列表加入失败 | star 仍保留（`starred_at` 已记录），动作标记失败并说明「已 star，但加入列表失败」 |
| 未配置列表 | 完全保持现有行为 |

## 三、GitHub API 可行性（已实测）

- REST `/user/lists` 返回 404，**没有公开 REST Lists 接口**。
- GraphQL 可用：
  - `viewer.lists` 可读取列表 `id`、`name`、`items`；
  - `updateUserListsForItem(input: {itemId, listIds})` 用于设置条目所属列表，语义是「更新条目属于哪些列表」，因此必须传完整集合以保留其他列表；
  - 仓库 node id 通过 `repository(owner, name) { id }` 获取。
- 调用方式仍是 `gh api graphql`，不引入新依赖。

## 四、配置设计

两个插件各新增一个配置键：

```json
"github_star_list": {
  "description": "GitHub star 列表名称（Star List Name）",
  "type": "string",
  "hint": "填写 GitHub Lists 中的列表名称；留空或找不到时只 star，不加入列表。",
  "default": ""
}
```

常量名：`GITHUB_STAR_LIST_KEY = "github_star_list"`，分别加入两个插件的 `constants.py`。

## 五、实现方案

### 5.1 共享库 `sourcehub/github_actions.py`

1. `GithubAutomation.__init__(state_path, runner, star_list: str = "")`，保存 `self.star_list`。
2. 新增 `_graphql(query, variables)`：通过 `gh api graphql -f query=... -f key=value` 调用，解析 `data`，同时检查 HTTP 与 GraphQL `errors`。
3. 新增 `_list_membership(repository)`：
   - 一次 GraphQL 查询同时取 `repository.id` 与 `viewer.lists(first:100)` 的 `id/name/items(first:100)/pageInfo`；
   - 定位目标列表（名称完全匹配）；
   - 计算该仓库当前所属列表 ID 集合；
   - 若任何列表或列表项出现 `hasNextPage=true`，视为无法安全计算，返回「跳过」而不是覆盖。
4. 修改 `_star`：
   - 已是 star 状态 → 原样返回「已经 star，跳过」；
   - 未配置列表 → 保持现有 REST star；
   - 配置了列表 → 先 star（REST），成功后执行列表归属；列表不存在时返回「已 star（列表「X」不存在，放入默认位置）」；
   - 列表归属失败时返回失败动作，消息包含「已 star，但加入列表失败：…」。
5. 列表归属 mutation 的 `listIds` 直接嵌入查询串，但只接受 `UL_` 开头的合法 ID（正则校验）；`owner/name` 继续用 GraphQL 变量，避免注入。

### 5.2 插件接入

- 检查插件 `_build_github_automation`：传入 `str(self.config.get(GITHUB_STAR_LIST_KEY) or "")`。
- B 站插件 `_build_github_automation`：同上。
- 两个 `_conf_schema.json` 增加配置项。
- 现场配置 JSON 增加 `github_star_list` 键（默认空字符串），便于页面直接填写。

### 5.3 版本

- 检查插件：`0.6.4` → `0.6.5`。
- B 站插件：`0.3.6` → `0.3.7`。
- 三份 `sourcehub` 副本保持字节级一致。

## 六、失败与安全边界

- 列表查询失败、GraphQL 报错、网络错误：不影响 star 结果；消息中明确说明。
- 列表条目超过 100 或列表数超过 100：不执行归属（避免误删手动归属），记录警告。
- `starred_at` 一旦写入，后续不会因为列表失败而重复 star。
- 不自动创建列表；不按 slug/模糊名称匹配；不移动历史已 star 仓库。

## 七、测试计划

新增/修改 `tests/test_github_actions.py`：

1. 列表存在：star 成功后调用 mutation，`listIds` 包含目标列表。
2. 保留其他列表：仓库已在列表 A，目标为 B，mutation 的 `listIds` 同时包含 A、B。
3. 列表名不匹配：只 star，不调用 mutation，消息包含「放入默认位置」。
4. 已 star：不查询列表、不调用 mutation。
5. 分页截断：`hasNextPage=true` 时不调用 mutation，返回可读警告。
6. GraphQL 失败：star 仍成功，动作标记失败并带错误信息。

全量回归：`PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'`。

## 八、实施步骤

1. T1：共享库新增 GraphQL 调用与列表归属逻辑（三副本同步）。
2. T2：两个插件接入配置键与构造函数参数。
3. T3：两个 `_conf_schema.json` 与现场配置补充 `github_star_list`。
4. T4：补齐测试并跑全量离线。
5. T5：版本升级、覆盖现场插件目录、`diff -rq` 复核。
6. T6：重载后先用一个真实仓库验证 star + 列表归属（产生真实副作用，需用户确认仓库与目标列表）。

## 九、本轮不做（Deferred Scope）

- 已 star 仓库的历史归类迁移；触发条件：用户明确要求批量整理历史 star。
- 自动创建不存在的列表；触发条件：用户要求按名称自动建列表。
- 列表/条目超过 100 的完整分页；触发条件：真实列表规模超过上限并需要归类。
- 按 slug、别名或模糊名称匹配；触发条件：用户要求更宽松的匹配规则。
- 从列表移除、列表改名同步；触发条件：用户另行提出。
