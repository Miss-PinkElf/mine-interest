# 0.3.3 真机用例：跳过与未自动生成项

> 生成时间：2026-11-01 02:30 +08:00
> 被测插件：`astrbot_plugin_cc_qq` 0.3.3
> 说明：本文件只记录未执行项与原因，不静默丢弃。

## 高风险命令（按约定 SKIPPED）

| 功能 | 原因 |
| --- | --- |
| `/cd` | 高风险：会切换工作目录并结束会话；用户未要求本轮验证 |
| `/goon` | 高风险：会中断当前执行并继续会话 |
| `/approve`、`/deny` | 高风险：危险操作审批，需先构造待审批动作 |
| `/initbase` | 高风险：会向工作目录补模板文件 |
| `/resume` | 高风险：会恢复历史会话，状态不可控 |
| `/cc` | 高风险：代理透传；本轮回复媒体用普通文本触发即可 |
| `/img` | 中风险但会改变会话长图开关；本轮未要求，避免污染后续用例 |

## 误报项

| 功能 | 原因 |
| --- | --- |
| `/new` | discover 从 README 版本历史中误识别；`commands/registry.py` 已无 `/new`，实际命令是 `/start`。群内发送 `/new` 会命中 AstrBot 内置命令并提示权限不足，不属于本插件能力。 |

## 不可自动断言项

| 功能 | 原因 |
| --- | --- |
| 事件 `filter.EventMessageType.ALL` | testability=manual，无独立可观测输出 |
| 30 项配置 | testability=config，需改配置并重载插件；本轮只读测试，不修改测试实例配置 |
| `auto_send_media=false` 回退 | 需修改测试实例配置并重载插件；`--attach` 模式不重启实例 |
| 视频自动发送 | 执行引擎只有 `images` 断言，没有视频断言；且本机无 ffmpeg，无法生成有效 mp4。插件侧代码路径与图片共用 `send_parts()`，本轮以单测覆盖，真机标 SKIPPED |
| 长文本转长图 | 非本次改动；且 `allow_long_image` 只对会启动代理的输入生效，`/help` 等同步命令仍为文本 |

## 用例与功能映射

| 用例文件 | 覆盖 |
| --- | --- |
| `00-help.json` | `/help` 文本命令列表（含 `/start`、`/info`、`/pwd`） |
| `01-pwd.json` | `/pwd` |
| `02-info.json` | `/info`（活跃/无会话两种状态） |
| `03-start-multiturn.json` | `/start` → 普通文本 → `/info` → `/end` |
| `04-media-local.json` | 回复中可信本地图片路径自动发送 |
| `05-media-url.json` | 回复中公网图片 URL 自动发送 |
| `06-media-untrusted.json` | 工作目录外路径与私网 URL 不发送 |
| `07-explicit-marker.json` | `[[image:<path>]]` 显式标记回归 |
| `08-draw-skill.json` | 代理（python3）生成图片后自动发送 |
| `../ccqq-v033-manual/12-draw-skill-explicit.json` | 显式调用 `rc-draw-generate`（run.sh）生成图片后自动发送；单独执行 |
| `09-receipt.json` | 执行回执 |
| `10-spacer.json` | 回执 10 秒去重窗口间隔垫片 |
| `11-interrupt.json` | 执行中 `/!` 中断（用户明确要求的 high risk 例外） |
