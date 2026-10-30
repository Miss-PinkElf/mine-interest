# Checkpoints

## Metadata（元数据）

- 创建时间（Created At）：2026-10-27 17:10:00 CST。
- 更新时间（Updated At）：2026-10-31 02:31:26 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：记录当前 mission 的阶段检查点，只保留最近 3 条。
- 关联项目（Related Repository / Project）：当前仓库 `.`。
- 关联任务（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：Docker 双容器 E2E 启动脚本完成并验证；测试资产待修。
- 文档边界（Scope / Boundary）：恢复热路径的一部分；不替代 `state.md` 或 `handoff`。

## 2026-10-31 02:31:26 CST — Docker 双容器 E2E 启动脚本完成

- 新增 `tools/napcat_e2e/`：两个 NapCat 容器（`napcat-e2e-bot` 17号 / `napcat-e2e-sender` C#）+ 测试 AstrBot；`start-all` 打开 iTerm 三标签，另有分开启动、停止、状态脚本。
- 关键修复：`start-astrbot` 先等待 6200/6201，并用 `wait_onebot.py` 调 `get_login_info` 确认账号就绪；`start-instance` 失败重试 3 次；支持 `--detach`、`--restart`、`--force-tabs`；iTerm AppleScript 应用名改为 `iTerm`。
- 验证：`doctor OK`；`/pwd` PASSED；`/info` 实际回复「当前会话 #5，代理：claude，状态：active。」，用例仍期望 `/new`（断言过期）；`probe_echo` 被 cc-qq 回执拦截。
- 收尾：旧原生 e2e 数据归档到 `~/.qq-e2e/archive-20261031/`；生产容器 `napcat` 当前停止，恢复用 `stop-all.sh`。
- 下一步：新会话更新 `/info` 断言、隔离 probe/cc-qq、决定专用测试 bot 账号与 Docker 镜像升级。

## 2026-10-30 15:55:00 CST — 需求 2 真机验收与收尾完成

- 阶段：`Verify/Close`（需求 2）。
- 完成：
  - `doctor OK`：bot `3254276668`、sender `1961618848`。
  - 多轮 `/pwd` → `/info` PASSED：`reports/20261030-154828-636210-cc-qq`。
  - 文本 suite 2/2 PASSED：`reports/20261030-154847-882152-astrbot_plugin_cc_qq-suite`；报告脱敏无泄漏。
  - 自愈：未知端口占用只报错不误杀；残留实例自动停止/重启（`reports/20261030-155012-908540-astrbot_plugin_cc_qq-suite`）。
  - 发现并固化：cc-qq `/help` 返回图片卡片，标记 `testability=rich_media`，不自动生成文本用例。
- 当前边界：Task 0–13 完成；引擎 127/127，skill 12/12；未提交。
- 下一步：向用户申请提交许可；未批准前不 commit。
- 已知风险：Q11 富媒体断言；Q12 QQ/NapCat 签名与 App 管理权限；生产 bot 兼任测试机器人。

## 2026-10-30 15:40:00 CST — Apply 暂停（Task 12 阻塞）

- 阶段：`Apply`（需求 2）；Task 0–11 完成，Task 12 未完成。
- 完成：
  - 引擎：多轮 `steps`、`execute_case`、`run-suite`、插件源解析、报告脱敏、doctor 增强、`--no-redact`；全量 **127/127**。
  - skill：探测、功能清单、用例生成、文档/模板、vendor、仓库副本、catalog 登记；脚本测试全部通过。
  - 复核修复：`reverse_ws_token` 脱敏；`/cc <参数>` 识别；系统路径误报；`/cd`、`/resume` 高风险；目录不存在静默空清单。
- 阻塞：本机 QQ 7.0.2 签名/quarantine 问题；`codesign --force --deep --sign -` 破坏 nested Helper 签名，Worker 被 `SIGKILL (Code Signature Invalid)`。用户决定自行还原 QQ/NapCat 环境。
- 当前边界：未提交任何改动；容器 11G 未删除；QQ 应用备份在 `~/Applications-backup/`。
- 下一步：环境恢复后执行 Task 12（doctor、多轮、suite、脱敏、自愈演练），再 Task 13 收尾。
- 已知风险：不要对 NapCat 注入后的 QQ 使用 `--deep` 重签；App 管理权限会阻止 xattr/codesign。


