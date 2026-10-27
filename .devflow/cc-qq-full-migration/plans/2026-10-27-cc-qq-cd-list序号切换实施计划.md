# cc-qq `/cd list` 与序号切换实施计划（Implementation Plan）

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 23:10:00 +08:00
- 更新时间（Updated At）：2026-10-27 23:10:00 +08:00
- 作者（Author）：Claude
- 目的（Purpose）：记录需求 6「cd list 列出允许目录并按序号切换」的对齐结论、实施范围与验证方式。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md` 需求 6
- 当前状态（Status）：计划中（Planned）
- 文档边界（Scope / Boundary）：本文件是本次改动的计划真相源（source of truth）；经用户确认后进入实施（Apply）。

## 一、需求与对齐结论

原始需求：

> 目前 cd 命令，就是有点不友好，能不能这样，加一个 cd list 命令，输出所有被允许的工作目录，然后，cd cd-list 的目录序号然后就可以切换目录

对齐结论（用户 2026-10-27 当面确认）：

1. `/cd list` 直接输出配置项 `allowed_work_dirs` 的内容，**按配置顺序编号**，不扫描磁盘、不展开子目录、不加任何过滤。
2. `/cd <序号>` 按同一份配置顺序切换。
3. 入口**仅斜杠命令**，不识别无斜杠的 `cd list`。
4. 权限沿用现有 `/cd`：仅 owner／管理员（`ROLE_ADMIN`）。

明确不做（本轮）：

- 不扫描 `allowed_work_dirs` 下的一级子目录。
- 不做两级列表、不做分页。
- 不新增无斜杠命令解析，避免普通聊天被误判为命令。

## 二、现状

- `commands/registry.py` 注册了 `/cd <工作目录>`，最小角色 `ROLE_ADMIN`。
- `service.py::_change_work_dir` 校验：空参数 → 用法提示；未配置根目录 → 提示；`resolve_path` + `allowed_work_dir` 校验 → 越界拒绝；非目录拒绝；代理执行中拒绝；通过后写 `work_dir_override` 并结束会话。
- `permissions.py::workspace_roots(config)` 已按配置顺序返回 `Path` 列表，是列表数据的现成来源。
- 当前生效目录来自 `settings.work_dir`（已合并 override 与群规则默认值）。

## 三、改动范围

### 3.1 命令入口解析（`service.py`）

在 `_change_work_dir` 之前加一层分派：

| 参数 | 行为 |
| --- | --- |
| 空 | 保持现有 `CD_USAGE_REPLY`，并补充提示可用 `/cd list` |
| `list`（大小写不敏感） | 输出编号列表 |
| 纯数字 | 按序号切换到 `allowed_work_dirs[n-1]` |
| 其余 | 走现有路径切换逻辑，行为不变 |

序号越界 → 新提示文案，列出可用范围（`1-N`）。

### 3.2 列表与切换的边界校验

- 列表与序号切换都基于 `workspace_roots(config)`，即配置里的 `realpath` 归一化后的路径。
- 序号切换复用现有校验链路：`allowed_work_dir` → `is_dir` → `is_running` 拒绝 → 写 override → 结束会话。不为序号另开一条不校验的旁路。
- 配置为空时，`/cd list` 与 `/cd <n>` 都返回 `CD_NOT_CONFIGURED_REPLY`。

### 3.3 文案（`constants.py`）

新增具名常量，不散落硬编码：

- `CD_LIST_HEADER`：列表标题
- `CD_LIST_ITEM_TEMPLATE`：`{index}. {path}`，当前目录加标记
- `CD_LIST_EMPTY_REPLY`：无可用目录
- `CD_LIST_TEMPLATE`：整体列表模板（含当前目录行）
- `CD_INDEX_OUT_OF_RANGE_TEMPLATE`：序号越界提示
- `CD_INDEX_INVALID_REPLY`：序号非正整数

### 3.4 展示（`commands/session.py`）

新增 `cd_list_text(roots, current_work_dir)`，与 `cd_success_text` 等同层，保持 service 只做编排。

### 3.5 版本

`0.2.2` → `0.2.3`：`metadata.yaml`、`constants.py::PLUGIN_VERSION`。

### 3.6 文档

- `README.md`：命令章节补 `/cd list` 与 `/cd <序号>`。
- `_conf_schema.json`：`allowed_work_dirs` 的 hint 补一句「顺序即 `/cd list` 编号」。
- `spec/tasks.md`：新增 T05.12 并勾选。
- `state.md`、`checkpoints.md`、`decision-log.md`：记录本轮结论。

## 四、测试计划

新增/扩展 `tests/test_commands.py`：

1. `/cd list` 输出顺序与配置一致，且带序号。
2. 当前生效目录在列表中有标记。
3. `/cd 2` 切到第 2 项并持久化 override。
4. `/cd 0`、`/cd 99` → 越界提示，且 override 不变。
5. `/cd list` 在未配置根目录时 → `CD_NOT_CONFIGURED_REPLY`。
6. 原路径切换用例保持通过。
7. `/cd` 对 member 仍无权限，`/cd list` 同样无权限。

## 五、验证标准

- `backend/.venv` 下跑 `astrbot_plugin_cc_qq` 单元测试全绿（87 + 新增）。
- `python -m py_compile` 全部改动文件通过。
- 安装目录同步到 `0.2.3`，等用户重载 AstrBot 后在 QQ 内实测 `/cd list` 与 `/cd 2`。

## 六、风险

- 配置顺序变化会导致历史序号失效；列表每次实时读配置，序号只在当次展示内有效，提示文案中说明「按当前配置顺序」。
- 目录名为纯数字的极端场景会被当成序号；在文案中说明 `/cd ./123` 可走路径形式，不在代码里加特判。
