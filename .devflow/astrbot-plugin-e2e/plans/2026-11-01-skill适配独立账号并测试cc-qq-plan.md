# Skill 适配独立测试账号并验证 cc-qq 改动计划

## Metadata（元数据）

- 创建时间（Created At）：2026-11-01 02:10:00 CST。
- 更新时间（Updated At）：2026-11-01 02:10:00 CST。
- 作者（Author）：Claude。
- 目的（Purpose）：让 `astrbot-plugin-e2e` skill 与当前 Docker 双容器、独立测试 bot 账号的环境一致，并修正过期用例断言，用于验证刚修改的 cc-qq 插件。
- 关联仓库或项目（Related Repository / Project）：当前仓库 `.`、`person-config`（skill 真源）。
- 关联 mission（Related Mission）：`.devflow/astrbot-plugin-e2e/`。
- 当前状态（Status）：已完成（Completed）；Skill 与用例修复、媒体功能 E2E 验证均通过。
- 文档边界（Scope / Boundary）：本文件是实施计划；不替代 `state.md` / `decision-log.md`。

## 一、问题

1. Skill 仍按旧环境描述：要求执行 `~/.qq-e2e/start-e2e.sh`，并把「暂停生产」当作默认动作。
2. 当前环境已改为 Docker 双容器 + 独立测试 bot `3299987672`，生产 `3254276668` 可同时运行。
3. `tools/astrbot_e2e/cases/cc_qq_multi_turn.json` 的 `/info` 断言仍期望 `/new`，与实际回复「当前会话…状态」不一致，会导致必现失败。
4. 插件已把 `/new` 改名为 `/start`，skill 的多轮示例需要同步。

## 二、改动清单

### 2.1 Skill 文档（真源 + 仓库副本）

真源：`person-config/skills/custom/astrbot-plugin-e2e`。
副本：`.claude/skills/astrbot-plugin-e2e`。

- `SKILL.md`
  - S1 安全闸：生产暂停改为「仅当测试 bot 与生产同号时需要」，独立账号可并行。
  - S2 起服务：优先 `tools/napcat_e2e/start-all.sh`；`~/.qq-e2e/start-e2e.sh` 仅作回退；已运行时跳过启动，只做 `doctor`。
  - S4 生成用例：多轮示例 `/new` 改为 `/start`。
  - S7 收尾：仅当本次暂停过生产时才需要恢复。
- `references/safety-rules.md`
  - 用户确认清单中，「暂停/恢复生产 AstrBot」标注为「仅当测试 bot 与生产同号」。
  - 生产/测试隔离一节补充「独立测试账号可并行」的前提。

### 2.2 用例断言

- `tools/astrbot_e2e/cases/cc_qq_multi_turn.json`：`/info` 断言由 `contains ["/new"]` 改为正则 `当前会话.*状态`。

### 2.3 一致性

- 运行 `sync_vendor.py` 更新仓库副本与真源的 `vendor/astrbot_e2e`，确保用例与 README 同步。
- 更新 `person-config/skills/catalog.json` 中 `astrbot-plugin-e2e` 的 `sha256`。

### 2.4 补充修复：异步回复采集（2026-11-01 02:20，用户批准）

现象：`/start` 等异步代理命令的 E2E 用例在 2.6 秒内结束，只抓到「正在处理」回执；实际图片回复约 12 秒后才到，造成假失败。

根因：bot 观察端 `onebot11_<bot_qq>.json` 的 `websocketServers[0].reportSelfMessage` 为 `false`，观察端收不到 bot 自己发送的消息，执行引擎回退历史查询时只拿到回执。

改动：

- `tools/napcat_e2e/common.sh`：观察端 `e2e-observer` 的 `reportSelfMessage` 改为 `true`；反向 WS 客户端保持 `false`。
- 现有本地配置 `~/.qq-e2e-docker/bot/config/onebot11_3299987672.json` 同步改为 `true`，重启 `napcat-e2e-bot`。
- `tools/napcat_e2e/README.md` 补充说明。
- 媒体用例断言改为 `images: {min: 1}`（路径文本会被插件消费，不再断言文本）。

## 三、验证

1. Skill 测试：`python3 -m unittest discover -s tests -t .`，期望 14/14。
2. 引擎测试：`backend/.venv/bin/python -m unittest discover -s tools/astrbot_e2e/tests -t tools`，期望 127/127。
3. 运行时：`doctor` 通过后运行修正后的 `cc_qq_multi_turn`，期望 `/pwd`、`/info` 均 PASSED。
4. 用 `discover_plugin.py` 生成 cc-qq 功能清单，向用户确认后再决定是否扩展用例。

## 四、实施结果（2026-11-01 02:20）

- Skill 文档真源、仓库副本与 `catalog.json` 哈希已同步。
- 引擎 127/127、skill 14/14。
- `cc_qq_multi_turn` PASSED：`reports/20261101-021832-550174-cc-qq`。
- 媒体功能 E2E PASSED：`reports/20261101-021808-341659-cc-qq`（14.7 秒，图片数 1）。
- 追加修复：`e2e-observer` 的 `reportSelfMessage=true`（`tools/napcat_e2e/common.sh`、本地配置、README）；原因见 `bug-log.md` B13。

## 四、边界

- 不修改 cc-qq 插件源码。
- 不停止生产 AstrBot/NapCat。
- 不改动测试实例账号与登录态。
- 不提交代码，提交前先询问用户。
