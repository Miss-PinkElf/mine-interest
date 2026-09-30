# cc-qq 本次踩坑（Learnings）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-30 15:38:00 +08:00
- 作者（Author）：Grok
- 目的（Purpose）：留下这次排查里下次还会用到的判断，避免再走错证据。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`
- 当前状态（Status）：已记录（Recorded）
- 文档边界（Scope / Boundary）：经验记录，不是验收结论，也不代替 `bug-log.md`。

- 判断消息是不是过期，只读 OneBot 原始 `time`（`message_obj.raw_message["time"]`）。AstrBot 会把 `message_obj.timestamp` 改成收到时刻。
- 用户和 NapCat 同时登录的是同一个机器人号 `1961618848`。空白私聊的发送者仍是对方 `1968401530`，不是第二个机器人号在线。插件只丢弃 `sender_id == self_id`。
- CPython 3.12 的 `StreamWriter.drain()` 在对端已关掉管道时抛 `ConnectionResetError('Connection lost')`。`0.1.14` 之前这段不在 `AgentProcessError` 里，子进程 stderr 会被丢掉。
- 上传 ZIP 必须在插件目录内部打包，让 `metadata.yaml` 位于压缩包根层。在工作区根目录执行 `zip -r ../... .` 会把整个仓库打进工作区的上一级目录。
- 插件单测要用 `backend/.venv/bin/python -m unittest discover -s integrations/astrbot/astrbot_plugin_cc_qq/tests -t integrations/astrbot -p 'test_*.py'`。这个虚拟环境是 Python 3.9.6，AstrBot 运行时是 3.12。直接 `python -m unittest integrations.astrbot...` 会找不到包。
- 不要在整个 `$HOME` 里做宽搜索，macOS 隐私权限会拦住。插件配置 JSON 带 UTF-8 BOM，读取时用 `utf-8-sig`。
- 空白事件是双端登录机器人号时多推进来的空包，日志为 `1968401530/1968401530:`，发送者仍是对方。回执按 `message_id` 去重，拦不住这种连发空包。
- 在 AstrBot 插件设置页保存新 schema 字段时，可能把 `private_enabled` 和 `private_user_ids` 写回默认值。15:44 那次保存清掉了 `1968401530`。
- 未授权判断若排在空文本静默之前，空白私聊会刷「未获授权」。私聊未在名单应走范围外静默。
