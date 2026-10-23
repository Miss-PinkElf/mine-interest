# Metadata（元数据）

- 创建时间（Created At）：2026-10-23 11:09:32 +08:00。
- 更新时间（Updated At）：2026-10-23 12:00:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：把需求 8（GitHub 链接自动 star/fork、fork 自动同步、代理回退提示、QQ 回复、B 站 Cookie 失效提醒）落成可执行的轻量计划。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联 mission（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 60–67 行。
- 轻量任务（Light Tasks）：`spec/2026-10-23-需求8/tasks.md`。
- 当前状态（Status）：已实施并部署，待重载后的页面与真实链接验收（In Progress）。代码提交 `b9ef0fc`。
- 文档边界（Scope / Boundary）：本计划是当前切片的实施顺序与范围真相源；不代表真实 star/fork 已发生或已通过端到端验收。

# 需求 8 轻量计划（GitHub 自动化与 Cookie 提醒）

## 本轮目标

1. 采集内容里出现 GitHub 仓库链接时自动 star。
2. 触发文本包含 `/fork` 时自动 fork，并在 fork 内安装只同步默认分支的 GitHub Actions 工作流。
3. GitHub 直连失败时自动回退到本机 `127.0.0.1:7897` 代理；权限或未登录问题明确提示，不误报成网络问题。
4. QQ 侧成功与失败都回复；B 站侧不回复，写入日志和插件页状态。
5. B 站插件页打开时实时校验 Cookie，失效时红色提示重新扫码。

## 已对齐的边界（Mini Align 结论）

| 项 | 结论 |
| --- | --- |
| QQ 落点 | `astrbot_plugin_sourcehub_inspector` |
| QQ 权限 | 配置的 owner/admin QQ 号 + AstrBot 管理员；首批账号 `2844973553`、`1961618848` |
| B 站扫描范围 | 整篇采集内容（触发评论、上级/根评论、简介、专栏正文、动态正文） |
| `/fork` 识别 | 本次触发评论文本；大小写不敏感，按独立 token 识别 |
| 自动同步 | fork 内安装 GitHub Actions；只同步默认分支；工作流用 `git fetch upstream` + `git merge` + `git push` |
| Cookie 提醒 | 打开插件页实时校验；网络未知不报失效；后台告警链路保持原样 |
| 开关 | 实施与部署时 `github_enabled` 保持关闭，验收后再打开 |

## 本轮不做（Deferred Scope）

- QQ 合并转发内部消息里的 GitHub 链接：只处理发送者本条消息的正文。原因：转发内容可能来自无权限的人。触发条件：需求明确要求“转发里的链接也处理”时。
- 同步冲突自动解决：上游与 fork 冲突时让 Actions 失败并通知仓库所有者。原因：自动合并冲突风险高。触发条件：出现真实冲突且用户要求自动处理时。
- 私有上游仓库的 fork 同步：首版只保证公开仓库；私有仓库的 `git fetch upstream` 需要额外凭据。触发条件：实际 fork 私有仓库时。
- 同步频率配置化：首版固定每 6 小时 + 手动触发。触发条件：用户提出更密集或更稀疏的同步需求时。
- star 的取消/收藏夹管理、fork 后的 PR 自动化：均不在需求 8 范围内。

## 实施顺序与任务

### T1：共享库新增 GitHub 链接解析

文件：`backend/src/sourcehub/github_links.py`

- 提供 `extract_repository_links(text) -> list[str]`，返回去重后的 `owner/repo`。
- 支持 `https://github.com/owner/repo`、`/tree/...`、`/blob/...`、`.git` 后缀、查询参数与锚点。
- 过滤 `features`、`topics`、`sponsors`、`marketplace`、`settings`、`apps`、`login` 等非仓库路径。
- 提供 `fork_requested(text) -> bool`，只识别独立 `/fork` token。
- 纯函数，无网络、无文件依赖。

验证：新增 `tests/test_github_links.py`，覆盖正常链接、子路径、重复、非仓库路径、`/fork` 边界。

### T2：共享库新增 GitHub 自动化服务

文件：`backend/src/sourcehub/github_actions.py`

- `GithubRunner`：封装 `subprocess.run`，默认超时 30 秒；解析 `gh` 可执行文件（配置 → `shutil.which` → `/opt/homebrew/bin/gh` → `/usr/local/bin/gh`）。
- 直连执行；仅当错误属于连接类（DNS、超时、连接拒绝、TLS、EOF、proxyconnect）时，用 `HTTPS_PROXY`/`HTTP_PROXY=http://127.0.0.1:7897` 重试一次。
- 权限、未登录、404 等错误不重试，返回明确类别。
- `GithubAutomation`：
  - `handle(repositories, fork_requested, source) -> list[ActionResult]`。
  - star：`gh api -X PUT /user/starred/{owner}/{repo}`。
  - fork：先取当前登录账号；仓库属于自己则跳过；否则 `gh repo fork {owner}/{repo} --clone=false --remote=false --default-branch-only`。
  - 工作流：校验 fork 默认分支，读取/写入 `.github/workflows/sourcehub-fork-sync.yml`；内容含托管标记，非本插件文件不覆盖；安装后尝试 `gh workflow enable`。
  - 状态文件：JSON，记录每个仓库的 star/fork/工作流时间和最近 50 条动作；原子写入。
  - 每个仓库最多处理一次 star；fork 命令重复执行时只补装工作流。
- 工作流模板常量：`cron: 17 */6 * * *` + `workflow_dispatch`，`permissions: contents: write`，只对默认分支 fetch/merge/push。

验证：新增 `tests/test_github_actions.py`，用假 runner 覆盖直连成功、直连失败后代理成功、权限失败不重试、去重、工作流模板生成与“非本插件文件不覆盖”。

### T3：共享库同步到两个插件副本

- 把 `github_links.py`、`github_actions.py` 复制到：
  - `integrations/astrbot/astrbot_plugin_sourcehub_inspector/sourcehub/`
  - `integrations/astrbot/astrbot_plugin_sourcehub_bilibili/sourcehub/`
- 保持三份字节级一致，现有 `test_sourcehub_vendoring` 必须通过。

### T4：B 站插件接入

文件：`integrations/astrbot/astrbot_plugin_sourcehub_bilibili/`

- `constants.py`：新增 `GITHUB_ENABLED_KEY`、`GITHUB_PROXY_KEY`、`DEFAULT_GITHUB_PROXY`、状态文件名与动作上限。
- `main.py`：构造 `GithubAutomation`，传入 Poller；从配置读取开关与代理。
- `poller.py`：`Store.save` 成功后调用自动化；扫描 `doc.text`，从触发评论/`source_content` 判断 `/fork`；用 `asyncio.to_thread` 执行，避免阻塞事件循环；失败只记日志。
- `webui.py`：`login/status` 改为实时校验（`BilibiliAuth.check`），返回 `valid`、`status`、`message`、`checked_at`；新增 `github/status` 路由返回最近动作。
- `pages/login/index.html`：标题版本更新；登录状态按 `valid` 显示绿/红/未知；新增「GitHub 自动化」区块；登录状态请求超时放宽到 35 秒。
- `_conf_schema.json`：新增 `github_enabled`（默认 `false`）、`github_proxy`（默认 `http://127.0.0.1:7897`）。
- `metadata.yaml` / 页面版本：`0.3.3 → 0.3.4`。

验证：新增触发文本提取与登录状态映射的单元测试；现有 B 站测试不回归。

### T5：QQ 检查插件接入

文件：`integrations/astrbot/astrbot_plugin_sourcehub_inspector/`

- `constants.py`：新增 `GITHUB_ENABLED_KEY`、`GITHUB_OWNER_QQ_IDS_KEY`、`GITHUB_ADMIN_QQ_IDS_KEY`、`GITHUB_REPLY_ENABLED_KEY`、`GITHUB_PROXY_KEY`、默认代理。
- `github_gate.py`（新模块）：纯函数 `is_authorized(event, config)`，判断 AstrBot 管理员或 QQ 白名单；`message_plain_text(event)` 只取本条消息文本。
- `main.py`：
  - 构造 `GithubAutomation`，状态文件放在 `StarTools.get_data_dir(PLUGIN_NAME)`。
  - `inspect_message` 在原采集流程后处理 GitHub 链接；有权限且开关打开才执行。
  - 用 `event.plain_result(...)` 回复成功/失败；回复开关可关。
- `_conf_schema.json`：新增五个配置项，`github_enabled` 默认 `false`，owner/admin 白名单默认空数组。
- `metadata.yaml`：`0.6.1 → 0.6.2`。

验证：新增权限判断与回复文案的单元测试；现有 22+ 项检查插件测试不回归。

### T6：版本、文档与部署

- 更新两个插件 `README.md` 的相关配置说明。
- 同步三份 `sourcehub`，运行 `py_compile`。
- 生成/覆盖安装目录（先备份 `~/.astrbot/data/plugins/` 下两个插件目录）。
- 现场配置写入新增键：`github_enabled=false`、owner/admin 名单为两个 QQ 号、代理默认 7897；不启用。
- 不修改 NapCat、AstrBot 核心、`devflow-handoff.md`。

### T7：验证

- 离线全量测试（命令必须带 `-t .`）：
  `PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'`
- 编译检查：`python -m compileall` 两个插件目录。
- 只读真实验证：`gh auth status`、`gh api user`、`gh repo view` 可访问；不执行真实 star/fork。
- 部署后由用户重载插件，打开 B 站插件页确认 Cookie 状态实时显示。
- 真实 star/fork 与 QQ 回复由用户在打开 `github_enabled` 后触发一条带 GitHub 链接的消息验收；不以测试仓库制造真实副作用。

## 风险与回滚

| 风险 | 处置 |
| --- | --- |
| AstrBot 进程找不到 `gh`（PATH 不含 Homebrew） | 自动搜索常见路径；失败时 QQ 回复明确提示，B 站页面记录错误 |
| fork 仓库未启用 Actions | 安装后尝试 `gh workflow enable`；失败时在 QQ 回复和 B 站状态里提示需手动启用 |
| GitHub token 缺 `workflow` 权限 | 当前 token 已含 `workflow`；缺失时明确回报权限问题，不回退成网络错误 |
| 工作流与上游冲突 | 该次 Actions 失败并通知仓库所有者；不自动强推 |
| B 站页面实时校验拖慢 | 请求超时 35 秒；网络错误显示“暂时无法确认”，不影响二维码与采集 |
| 外部副作用误触发 | `github_enabled` 默认关闭；只处理 body 中的仓库链接；过滤非仓库路径；状态去重 |

回滚：代码按本轮 commit 反向修改；部署前备份插件目录；现场配置只新增键，回滚时删除新增键即可。

## 验收标准

1. 单元测试覆盖 URL 提取、`/fork` 识别、代理回退、权限判断、去重和工作流模板，全量测试通过。
2. 两个插件与 `backend/src/sourcehub` 三份共享库字节级一致。
3. B 站插件页能显示 Cookie 有效、失效、未知三种状态，失效为红色提示。
4. 开关关闭时，任何 GitHub 链接都不会产生 star/fork 副作用。
5. 开关打开后，QQ 有权限发送者能得到成功或失败回复；B 站动作可在页面状态中看到。
6. fork 后工作流只同步默认分支，且保留工作流文件。
