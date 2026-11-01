# star 列表 mutation 修复与历史补做交接（2026-11-01）

## Metadata（元数据）

- 创建时间（Created At）：2026-11-01 13:00:00 +08:00
- 更新时间（Updated At）：2026-11-01 13:00:00 +08:00
- 作者（Author）：rin（Claude 协助）
- 目的（Purpose）：记录需求 9「star 成功但不进入 GitHub Lists」的排查、修复、真实补做与剩余验证，供下一会话继续。
- 关联仓库或项目（Related Repository / Project）：`mine-interest-source-hub`（`.`）
- 关联 mission（Related Mission）：`.devflow/multi-source-hub/`
- 关联文档（Related Documents）：`state.md`、`checkpoints.md`、`bug-log.md`、`decision-log.md`、`plans/2026-11-01-需求9-fix-star列表mutation返回字段-plan.md`、`spec/2026-10-23-需求9/tasks.md`
- 当前状态（Status）：已完成（Completed）；消息链路端到端待验证
- 文档边界（Scope / Boundary）：本轮缺陷修复与补做记录；不代替 `state.md`；不含 token、rkey 或完整鉴权 URL

## 结论

- **现象不是列表名配错**：`bilibili_star` / `qq_star` 名称与 GitHub 完全一致，但 `items.totalCount` 始终为 0。
- **根因一**：`STAR_LIST_MUTATION_TEMPLATE` 选择集写了 `list { id name }`；`UpdateUserListsForItemPayload` 只有 `item / lists / user / clientMutationId`。GraphQL 校验错误会在执行前整体拒绝 mutation，所以列表从未写入。
- **根因二**：修好字段后暴露 `INSUFFICIENT_SCOPES`——`updateUserListsForItem` 要求 token 具备 `user` scope，原 token 只有 `gist / read:org / repo / workflow`。此前被 `undefinedField` 遮蔽。
- **QQ 侧无需单独修**：检查插件与 B 站插件共用同一个 `sourcehub/github_actions.py`。

## 改动清单

| 文件 | 改动 |
| --- | --- |
| `backend/src/sourcehub/github_actions.py` | 模板 `list` → `lists`；mutation 复用 `_graphql` 解析 `errors` |
| `integrations/.../sourcehub/github_actions.py`（两份） | 与后端副本字节一致 |
| `tests/test_github_actions.py` | 新增选择集断言、HTTP 200 + errors 判失败；stub 返回 `lists` |
| 两个插件的 `constants.py` / `metadata.yaml` | 检查插件 `0.6.6`、B 站 `0.3.8` |

## 验证结果

- 全量离线：`PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'` → **176 项通过**。
- 三副本字节一致；现场目录 `diff -rq -x __pycache__` 一致；`py_compile` 通过。
- 用户执行 `gh auth refresh -h github.com -s user`，`gh auth status` scopes 含 `user`。
- 历史补做（复用 `_assign_star_list`，一次性脚本，不改源码/状态）：

  | 仓库 | 目标列表 | 结果 |
  | --- | --- | --- |
  | `ssamurias/dsh-fish` | `bilibili_star` | OK |
  | `Mieksido/surfcore` | `bilibili_star` | OK |
  | `SAOS-3624/dsh-video-storyboard` | `bilibili_star` | OK |
  | `foxletters-hq/BaiShou-Next` | `bilibili_star` | OK |
  | `shareAI-lab/learn-claude-code` | `qq_star` | OK |

- `viewer.lists` 复核：`bilibili_star`=4、`qq_star`=1；`自动化日常`=4、`AI相关`=9、`Useful`=8、`Want to Learn`=9，均未变化。

## 提交

- `23e0bef` `fix(github): 修正 star 列表 mutation 返回字段并补回归测试`，未推送。

## 剩余工作

1. 重载 AstrBot，确认加载 `astrbot_plugin_sourcehub_inspector (0.6.6)` 与 `astrbot_plugin_sourcehub_bilibili (0.3.8)`。
2. 用**尚未 star** 的仓库经 QQ 与 B 站各触发一次，确认回复「已 star（已加入列表「…」）」。
3. 老账不变：需求 4 Verify、需求 7 Close、需求 8 T7、`@机器人 整理`、B 站日志观察。

## 延期边界（未变）

- 历史 star 全量批量归类（本轮只补 5 个已知遗漏）。
- 自动创建列表、超过 100 条目分页、slug/模糊匹配、列表移除/改名同步。
- 一个插件多列表 / 按来源或链接类型分流（未讨论）。
- 详见 `deferred/需求9-star列表首版边界.md`。
