# Metadata（元数据）

- 创建时间（Created At）：2026-11-01 12:00:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：修复需求 9「GitHub star 列表归类」中 mutation 返回字段写错导致列表始终为空的问题，并处理已 star 但未归类仓库。
- 关联仓库（Related Repository / Project）：mine-interest-source-hub（`.`）。
- 关联 mission（Related Mission）：`.devflow/multi-source-hub/`。
- 关联计划（Related Plan）：`plans/2026-10-23-需求9-GitHub-star列表归类-plan.md`。
- 关联任务（Related Tasks）：`spec/2026-10-23-需求9/tasks.md`。
- 当前状态（Status）：实施中（In Progress），代码与测试已完成，等待 gh 补授 `user` scope 后真机验证。
- 文档边界（Scope / Boundary）：用户已批准方案 A 与「一次性脚本补做」；本文件记录计划与实施证据，不代表真机验证已通过。

# 需求 9 修复：star 成功但不进入 GitHub Lists

## 一、问题现象

- 用户配置：两个插件页 `github_star_list` 均填写 `bilibili_star`（B 站）、`qq_star`（检查插件）。
- GitHub 实际列表存在且名称完全一致：`bilibili_star`（slug `bilibili-star`）、`qq_star`（slug `qq-star`），当前 `items.totalCount = 0`。
- star 动作成功，但仓库没有进入列表；插件动作记录里出现：

  ```
  已 star，但加入列表「bilibili_star」失败：gh 执行失败：{"errors":[{"path":["mutation","updateUserListsForItem","list"],
  "extensions":{"code":"undefinedField","typeName":"UpdateUserListsForItemPayload","fieldName":"list"}}]}
  ```

- 受影响记录（`~/.astrbot/data/plugin_data/*/github_actions.json`）：

  | 插件 | 仓库 | 时间 |
  | --- | --- | --- |
  | B 站 | `ssamurias/dsh-fish` | 2026-10-27 |
  | B 站 | `Mieksido/surfcore` | 2026-10-27 |
  | B 站 | `SAOS-3624/dsh-video-storyboard` | 2026-10-29 |
  | B 站 | `foxletters-hq/BaiShou-Next` | 2026-10-31 |
  | 检查插件 | `shareAI-lab/learn-claude-code` | 2026-10-26 |

## 二、问题原因

1. **主因（代码缺陷）**：`STAR_LIST_MUTATION_TEMPLATE` 的返回选择集写了 `list { id name }`。
   GitHub GraphQL 内省确认 `UpdateUserListsForItemPayload` 只有
   `clientMutationId / item / lists / user`，没有 `list`。
   `undefinedField` 属于**请求校验错误**，GitHub 会在执行前整体拒绝 mutation，因此列表成员从未写入。
2. **次因（错误处理不一致）**：列表归属 mutation 直接调用 `runner.run_with_fallback`，没有复用 `_graphql` 的 `errors` 解析；
   本次靠 `gh` 返回非零退出码才识别出失败，若某次返回 HTTP 200 + `errors` 会被误判为成功。
3. **无法自愈**：star 成功后已写入 `starred_at`，后续再发同一链接会走「已经 star，跳过」，永远不会补做列表归属。
4. **测试盲区**：`tests/test_github_actions.py` 使用假 runner，只断言 query 字符串包含 `updateUserListsForItem` 与 `listIds`，
   不校验选择集字段是否真实存在，故离线 174 项全绿仍漏掉该缺陷。

## 三、影响范围

- 只在「配置了 `github_star_list`」时触发；未配置列表的用户不受影响。
- star 与 fork 本身不受影响；仅列表归类失效。
- 历史 5 个仓库已 star 成功，但未进入任何列表；其余历史 star 无列表归属需求。

## 四、候选方案

### 方案 A（推荐）：修正字段 + 统一错误处理 + 补测试

1. `STAR_LIST_MUTATION_TEMPLATE`：`list { id name }` → `lists { id name }`。
2. mutation 改为复用 `_graphql(query, {"itemId": item_id})`，与查询共用 `errors` 解析与失败翻译。
3. `tests/test_github_actions.py`：
   - 断言 mutation 字符串包含 `lists {` 且**不包含** `list {`（防止回归）；
   - 新增用例：mutation 返回 `{"errors": [...]}` 时标记失败、消息含「加入列表失败」。
4. 三份 `github_actions.py` 保持字节级一致；版本升级：检查插件 `0.6.5 → 0.6.6`，B 站 `0.3.7 → 0.3.8`。
5. 覆盖现场插件目录并用 `diff -rq` + `py_compile` 复核；跑全量离线测试。

### 方案 B：只改字段（最小改动）

仅把 `list` 改成 `lists`，不动错误处理与测试。
- 优点：改动最小。
- 缺点：HTTP 200 + errors 场景仍会误报成功；无回归防护，下次 schema 调整仍可能复发。
- 不推荐。

## 五、历史 5 个仓库的补救（需单独选择）

- 选项 1（推荐）：一次性修复脚本/操作，对这 5 个仓库重新执行「star（幂等）+ 列表归属」，不修改源码。
- 选项 2：临时清空状态文件里这 5 个仓库的 `starred_at`，再按原流程发一次链接触发重放。
- 选项 3：本轮不动，用户自己在 GitHub 页面手动拖入列表。

## 六、验证方式

1. 离线：`PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'` 全绿。
2. 现场：重载 AstrBot，确认两个插件加载新版本且日志出现「GitHub 自动化：开」。
3. 真实副作用验证：用一个**尚未 star** 的仓库链接触发（需用户指定），确认：
   - 仓库进入 `bilibili_star` / `qq_star`；
   - 若该仓库原本属于其他列表，其他列表保留；
   - 动作记录出现「已 star（已加入列表「…」）」。
4. 历史仓库补救后，查询 `viewer.lists` 确认 `totalCount` 与条目正确。

## 七、实施进展（2026-11-01）

- 代码：`list { id name }` → `lists { id name }`；mutation 复用 `_graphql`。
- 测试：新增 `test_mutation_uses_lists_selection_set`、`test_mutation_graphql_errors_mark_failure`；全量离线 **176 项通过**。
- 版本与部署：检查插件 `0.6.6`、B 站 `0.3.8`；三副本字节一致；现场目录已覆盖，`diff -rq -x __pycache__` 一致；`py_compile` 通过。
- **新发现的阻塞（已解决）**：补做历史仓库时报 `INSUFFICIENT_SCOPES`——`updateUserListsForItem` 要求 token 具备 `user` scope，当前只有 `gist / read:org / repo / workflow`。用户已执行 `gh auth refresh -h github.com -s user`，复查 scopes 已含 `user`。
- 历史补做结果（2026-11-01）：5 个仓库全部成功；`viewer.lists` 核对 `bilibili_star` 4 条、`qq_star` 1 条，`自动化日常 / AI相关 / Useful / Want to Learn` 条目数未变。「QQ 收集消息」与 B 站共用同一份 `sourcehub/github_actions.py`，一次修复两边同时生效；检查插件现场目录已确认 `0.6.6`。
- 待办：重载 AstrBot 加载 `0.6.6` / `0.3.8`；用一个尚未 star 的仓库做 QQ / B 站真实端到端验证。

## 八、本轮不做（Deferred Scope）
- 历史 star 的批量归类（除上述 5 个补救外）；触发条件：用户明确要求整理全部历史 star。
- 自动创建不存在的列表；触发条件：用户要求按名称自动建列表。
- 超过 100 条目的完整分页；触发条件：列表规模超过上限。
- 列表移除/改名同步；触发条件：用户另行提出。
- 别名/slug/模糊匹配；触发条件：用户要求更宽松匹配。
