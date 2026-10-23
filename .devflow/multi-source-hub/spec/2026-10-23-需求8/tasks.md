# Metadata（元数据）

- 创建时间（Created At）：2026-10-23 11:35:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：跟踪需求 8 的轻量实施任务与验证证据。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联 mission（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 60–67 行。
- 计划（Plan）：`plans/2026-10-23-需求8-GitHub链接自动star-fork与Cookie提醒-plan.md`。
- 当前状态（Status）：实施中（In Progress），待重载后的页面与真实链接验收。
- 文档边界（Scope / Boundary）：当前切片任务真相源；勾选只代表对应证据已存在。

# Tasks（实施任务）

- [x] T1：共享库 `github_links.py`，提取/规范化 GitHub 仓库链接并识别独立 `/fork`。证据：`tests/test_github_links.py` 5 项通过。
- [x] T2：共享库 `github_actions.py`，star、fork、默认分支同步工作流、代理回退、权限分类、状态去重。证据：`tests/test_github_actions.py` 14 项通过。
- [x] T3：三份共享库字节级一致。证据：`tests/test_sourcehub_vendoring.py` 通过。
- [x] T4：B 站插件接入 GitHub 自动化；`login/status` 实时校验并返回 `valid/status/message/checked_at`；页面新增 GitHub 区块。证据：`tests/test_bilibili_github_hook.py` 7 项通过；真实凭据只读检查返回 `healthy`。
- [x] T5：QQ 检查插件接入权限判断与成功/失败回复。证据：`tests/test_sourcehub_github_gate.py` 4 项通过。
- [x] T6：版本与部署。B 站 `0.3.4`、检查插件 `0.6.2`；两插件目录已覆盖并与仓库 `diff -rq` 一致；现场配置新增键且 `github_enabled=false`。
- [ ] T7：重载后验收。代码提交 `b9ef0fc`。已完成：全量离线 **160 项通过**；`gh auth status` 与 `gh api user` 只读调用成功（`Miss-PinkElf`，直连）；工作流 YAML 可解析。待做：用户重载插件 → 打开 B 站插件页确认 Cookie 实时状态与 GitHub 区块 → 打开 `github_enabled` 后用真实链接验证 star/fork/回复。

## 延期（Deferred Scope）

- QQ 合并转发内部消息里的链接不处理；只处理发送者本条正文。触发条件：用户明确要求转发内链接也生效。
- 上游与 fork 冲突时不自动解决，Actions 失败并通知仓库所有者。触发条件：出现真实冲突并要求自动处理。
- 私有上游仓库的 fork 同步不在首版保证范围。触发条件：真实 fork 私有仓库。
- 同步频率固定每 6 小时 + 手动触发，暂不做配置化。触发条件：用户要求调整频率。
