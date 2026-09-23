# Metadata（元数据）

- 创建时间（Created At）：2026-09-23 15:33:49 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：在资料更新后自动发布允许的 Vault 文本到独立私有仓库。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 37 行。
- 关联对齐（Related Align）：`plans/2026-09-23-QQ目录直连重试与安全自动推送-align.md`。
- 当前状态（Status）：首版已实施，真实推送待验证（Implemented; Push Pending Verification）。
- 文档边界（Scope / Boundary）：本文件是自动发布子变更的实施计划（Plan）；不将现有 Vault Git 历史视为可推送资料。

# Vault 安全自动发布 Implementation Plan

> 执行方式：本会话顺序实施（Inline Execution）；代码仓库提交须另行询问。用户已授权资料自动推送到指定远端。

**目标（Goal）：** Vault 文本更新后自动、可恢复地推送到 `git@github.com:Miss-PinkElf/data-hub.git`，仅包含允许内容。

**结构（Architecture）：** 使用独立发布目录及独立 Git 历史，从 Vault 按允许清单投影 Markdown 和安全元数据。更新事件唤醒单一发布工作器；启动时与失败后再次扫描。推送前验证远端私有性与内容边界，不执行强制推送。

**技术栈（Tech Stack）：** Python、Git CLI、SQLite/本地状态、unittest、AstrBot。

---

## 文件职责

- `backend/src/sourcehub/publish.py`：允许清单、敏感内容检查、独立目录同步和安全 Git 推送。
- `integrations/astrbot/astrbot_plugin_sourcehub_inspector/main.py` 与 `integrations/astrbot/astrbot_plugin_sourcehub_bilibili/main.py`：启动后每 30 秒扫描一次；失败后下一轮及重启后重新扫描。
- `integrations/astrbot/astrbot_plugin_sourcehub_inspector/` 与 `integrations/astrbot/astrbot_plugin_sourcehub_bilibili/`：接入同一发布目录，避免两个插件并发推送。
- `tests/test_sourcehub_publish.py`：允许清单、隔离历史、失败恢复、非强推和多来源并发回归。

## 任务 1：投影与安全边界

- [ ] 创建测试 Vault，放入 `content.md`、`envelope.json`、Cookie、SQLite、媒体和快照；断言仅 Markdown、每日索引及明确安全的元数据进入独立发布目录。测试旧 Vault Git 历史不被复用。
- [ ] 实现只读投影：遍历 `items/` 下允许的 Markdown；移除外链查询参数与已知凭据片段，残留可识别凭据时拒绝该次发布并报告文件相对路径。发布目录存放于 Vault 外部，不将其加入现有 Vault 的 Git 索引。
- [ ] 运行 `PYTHONPATH=backend/src backend/.venv/bin/python -m unittest tests.test_sourcehub_publish -v`，预期边界测试通过。

## 任务 2：事件、恢复与远端推送

- [ ] 加入新 Item、每日文档追加、两个插件同时写入、远端不可达、远端有新提交的测试；先观察失败。
- [ ] 使用文件锁（File Lock）串行同步与提交、普通快进 `git push`；源资料作为持久待发布状态，失败后定时或重启重新扫描，不另建状态表；发布异常不阻断本地入库。
- [ ] 配置远端为指定 SSH URL；在首推前验证仓库为私有且目标可访问。核验失败只保留本地待推送状态，不猜测远端可见性。
- [ ] 在可联网环境验证真实远端权限、私有性、首推和后续自动推送。检查远端文件列表中没有封套、Cookie、快照、数据库、日志或媒体。

## 验证与边界

- [ ] 运行发布合成回归、全量 `unittest` 与 `git diff --check`。
- [ ] 不提交代码仓库；不推送现有 Vault Git 历史；未完成远端私有性核验前不报告实际推送完成。

## 实施记录

2026-09-23：仅投影 `items/**/*.md`，删除外部 URL 查询参数及已知凭据；私有性检查（匿名 API 404 + SSH 可读）已通过。首次真实推送与新消息后自动推送均未验证；上方步骤清单保留计划原貌。本次代码仓库提交由用户在收尾请求中明确授权，不等于授权上传真实快照或媒体。
