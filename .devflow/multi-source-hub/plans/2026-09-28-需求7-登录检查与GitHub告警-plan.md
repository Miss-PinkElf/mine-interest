# Metadata（元数据）

- 创建时间（Created At）：2026-09-28 16:16:18 +08:00。
- 更新时间（Updated At）：2026-09-28 17:05:00 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：把 B 站与 QQ 登录检查、自动刷新及专用 GitHub 告警拆成可验证实施步骤。
- 关联仓库（Related Repository / Project）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 50–52 行。
- 已批准对齐（Approved Align）：`plans/2026-09-28-需求7登录告警与B站文档排版-align.md`。
- 当前状态（Status）：实施中、真实告警待验收（In Progress）。
- 文档边界（Scope / Boundary）：实施计划（Plan）真相源；不代表已连接真实告警仓库或已发送邮件。

# 需求 7：登录检查与 GitHub 告警 Implementation Plan

> **面向实施者（For agentic workers）**：按本 mission 的 `tasks.md` 顺序执行；每个任务验证后再继续。用户已授权 Plan 后进入 Apply，并在 2026-09-28 收尾时明确授权提交本次相关代码。

**实施快照（Implementation Snapshot）：** B 站独立扫码/刷新、QQ 保守状态探针、告警状态机与私有 Git 发布器已有离线代码和测试；真实扫码、专用仓库推送与邮件尚未验收。任务状态以 `spec/2026-09-28-需求7/tasks.md` 为准，首版边界见 `deferred/需求7首版边界与真实验收.md`。

**目标（Goal）：** B 站采集账号和 QQ 登录/连接异常产生准确、去重、可恢复的专用私有 GitHub 仓库推送邮件，并在恢复时再次提醒。

**架构（Architecture）：** 平台探针（Platform Probe）只产生有证据的状态，状态机（Alert State Machine）负责确认故障、去重和恢复，独立告警发布器（Alert Publisher）把最小信息推送到专用私有仓库。B 站采集插件自己持有扫码与刷新凭据；QQ 状态由 AstrBot/NapCat 适配器提供，不以无消息推断离线。网络错误为“未知”，不得归类为登录失效。

**技术栈（Tech Stack）：** Python、AstrBot、NapCat/OneBot、B 站登录接口、独立 Git 仓库、`unittest`。

---

## 文件职责

| 文件 | 责任 |
| --- | --- |
| `integrations/astrbot/astrbot_plugin_sourcehub_bilibili/auth.py` | B 站登录有效性、扫码和刷新，凭据只保存在本地插件配置。 |
| `integrations/astrbot/astrbot_plugin_sourcehub_bilibili/client.py`、`main.py`、`_conf_schema.json` | 动态更新 Cookie、调度检查及登录入口。 |
| `integrations/astrbot/astrbot_plugin_sourcehub_inspector/qq_status.py`、`main.py`、`_conf_schema.json` | 从 AstrBot/NapCat 的明确信号判断 QQ 在线、需重登与持续断线。 |
| `backend/src/sourcehub/alerts.py` | 状态机、待发送事件账本和敏感信息最小化；同步到两个插件的共享库。 |
| `backend/src/sourcehub/alert_publish.py` | 独立私有 Git 告警仓库的验证、写入和推送；不得复用资料发布目录。 |
| `tests/test_sourcehub_alerts.py`、`tests/test_sourcehub_alert_publish.py`、`tests/test_bilibili_auth.py`、`tests/test_sourcehub_qq_status.py` | 验证分类、刷新、去重、失败重试、恢复及私有仓库边界。 |

## 实施步骤

### 任务 1：核实状态信号与告警仓库能力

- [ ] 核对本机 AstrBot/NapCat 可取得的在线与需要重新登录信号；记录具体对象、动作名和失败返回。若只能获得连接异常，不把它命名为“需要扫码”；前者按等待时间报“连接中断”，后者只有明确信号才报“登录失效”。
- [ ] 使用只读方式核对 B 站参考插件的 `check_cookie`、`check_need_refresh`、`refresh_cookie`、扫码流程与凭据落盘方式；不读取、复制或打印真实 Cookie。
- [ ] 为专用告警仓库确定独立目录和配置项：私有 SSH remote、分支、功能开关、QQ 断线等待时间与重试节奏；确认 GitHub 仓库设置中可配置推送邮件。真实仓库创建及邮箱配置留待端到端验收。

### 任务 2：先实现可测试的告警状态机

- [ ] 在 `tests/test_sourcehub_alerts.py` 写失败测试：同一账号故障首次确认产生一条、持续故障无新条、恢复产生一条、网络未知不改变登录状态、推送失败保留待发送事件、重启后不重放已成功事件。
- [ ] 在 `alerts.py` 实现 `observe(platform, account, status, observed_at)`、`pending()`、`mark_delivered(event_id)` 的小接口；事件仅含平台、脱敏账号标识、故障类别和时间。状态文件写到 Vault `spool/`，原子落盘；避免原始异常文本、Cookie 或 URL 参数进入告警。
- [ ] 运行 `PYTHONPATH=backend/src backend/.venv/bin/python -m unittest tests.test_sourcehub_alerts -v`，确认从失败变为通过。

### 任务 3：独立私有 Git 发布器

- [ ] 在 `tests/test_sourcehub_alert_publish.py` 使用临时 bare remote 写失败测试：仅允许预定告警文件、一个新状态只提交一次、远端不可证实为私有时拒绝推送、网络失败保留待送状态、恢复事件形成新提交。
- [ ] 在 `alert_publish.py` 实现独立工作目录、文件锁、私有性检查、中文提交信息和 `git push`；不读 Vault 的条目和媒体，不修改本仓库 Git 历史。复用现有 `sourcehub/publish.py` 的私有远端校验能力而不复用其资料投影目录。
- [ ] 运行 `PYTHONPATH=backend/src backend/.venv/bin/python -m unittest tests.test_sourcehub_alert_publish -v`，确认通过；审查测试仓库提交内容中没有凭据。

### 任务 4：B 站独立扫码、检查与刷新

- [ ] 在 `tests/test_bilibili_auth.py` 写失败测试：有效、需刷新且成功、刷新失败、缺少刷新令牌、DNS/超时未知、响应无新 Cookie 六类；检查失败不能清空旧凭据或误触发登录告警。
- [ ] 在 `auth.py` 实现独立凭据流程；可参考现有 BiliBot，但 B 站采集插件不能直接读取其配置。刷新后同步更新 `BilibiliClient` 会话 Cookie 并持久化刷新令牌。登录入口仅向本地管理员暴露，二维码与凭据不写入 Vault 或日志。
- [ ] 在 `main.py` 调度检查与状态机，配置开关和间隔由 `_conf_schema.json` 给出，业务阈值集中放常量；运行目标测试确认通过。

### 任务 5：QQ 登录与断线监测

- [ ] 在 `tests/test_sourcehub_qq_status.py` 写失败测试：明确需扫码、短暂断开、超过配置等待时间、重连恢复、无消息但状态在线、状态接口不可达。只在前两种明确故障下产生告警状态。
- [ ] 在 `qq_status.py` 只使用任务 1 已核实的 AstrBot/NapCat 信号实现探针；`main.py` 建立独立监测任务并在 `terminate` 取消。暂时无法得到 bot 句柄或接口失败时返回“未知”，不推断需重新登录。
- [ ] 运行目标测试，再与真实 NapCat 连接状态进行只读比对；不得通过主动给群发消息测试。

### 任务 6：集成和端到端验收

- [ ] 两插件共用状态机与发布器，确保同一故障在跨插件重启后仍只产生一次待送事件；告警仓库仅记录最小状态。同步共享库、递增改动插件的版本与 `metadata.yaml`。
- [ ] 运行目标 `unittest`、`compileall`、共享库一致性检查与 `git diff --check`；不做全局 ESLint，也不顺手修无关 TypeScript 错误。
- [ ] 在用户专用私有告警仓库和收件邮箱配置完成后，实测一次故障与恢复的真实推送邮件；未拿到邮件证据前只能宣称代码离线通过，不能宣称提醒端到端完成。

## 本计划不做 / 后续阶段

- B 站 DNS 采集故障作为需求 4 的独立问题继续诊断；原因是网络失败不能证明 Cookie 失效。需求 4 Verify 恢复时按 `bug-log.md` 处理。
- 整机或 AstrBot 进程停止的外部心跳监控：本机故障时无法主动上报；用户明确要监控宿主可用性时另做外部探测设计。
- 远端媒体上传和其他通知渠道：本轮只用专用私有 GitHub 仓库及其推送邮件；用户以后提出多端归档或冗余通知时另行对齐。
