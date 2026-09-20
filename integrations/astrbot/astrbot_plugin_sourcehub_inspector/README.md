# Metadata（元数据）

- 更新时间（Updated At）：2026-09-20 19:05:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：说明诊断插件的安装、配置、测试方式、展开能力与已知限制。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联计划（Related Plan）：`.devflow/multi-source-hub/plans/2026-09-20-检查插件嵌套转发展开-plan.md`、`.devflow/multi-source-hub/plans/2026-09-20-检查插件群级启用范围-plan.md`。
- 当前状态（Status）：诊断原型（Diagnostic Prototype），不用于正式收藏。
- 文档边界（Scope / Boundary）：使用说明；问题真相源为 `.devflow/multi-source-hub/bug-log.md`。

# SourceHub 消息检查器（Message Inspector）

在 AstrBot Desktop v4.27.5 + QQ 个人号（NapCat / aiocqhttp，OneBot v11）上生成真实消息快照，并展开合并转发的完整内层聊天记录。仅保存 JSON，不自动回复，不接完整信息中心。

## 它做两件事

1. **事件快照**：把整条消息事件存成 JSON，落到 `data/sourcehub-inspector/snapshots/`。
2. **转发展开**：消息里含合并转发（`Forward`）时，调用 OneBot v11 的 `get_forward_msg` 取回内层消息树，落到 `data/sourcehub-inspector/forwards/`。

为什么要二次调用：推送事件里的转发段只有 `{"type": "forward", "data": {"id": "<res_id>"}}`，正文不在事件中。官方 QQ 机器人没有这个二次获取入口，个人号（NapCat）有。

内层树包含：每条消息的发送者 QQ 号 / 昵称 / 群名片、时间、消息 ID、群 ID，以及 `text`、`image` 等消息段。

嵌套转发以**内联 `content` 优先**递归，缺失时才按 `id` 补取（实测按内层 id 再请求会 `retcode 1200`）。深度上限 5 层，超限写 `_sourcehub_truncated` 标记；取数失败写 `_sourcehub_error` 标记，不抛异常。

## 输出文件

每收到一条合并转发，会同时输出两份文件到 `data/sourcehub-inspector/forwards/`：

| 文件 | 内容 |
| --- | --- |
| `<时间>_<事件ID>_<forward_id>.json` | 结构化原始数据（`messages` 数组，内嵌层在 `message[].data.content`） |
| `<时间>_<事件ID>_<forward_id>.txt` | **可读转录**，按层缩进，直接打开就能看 |

可读文本长这样：

```text
转发展开结果  forward_id=7687568200398538184
共 3 层 / 35 条 / 段类型 {'forward': 6, 'image': 157, 'text': 19}

[第1层 第1条] 昵称(QQ号)  2026-04-30 12:54:54
  [文本] …
  [图片] file=xxx.jpg size=12345 url=…
  └─ 内嵌转发 id=…
    [第2层 第1条] …
```

NapCat 对个别转发会返回 `status=ok` 但内容为空，这类会在文本里标 `（未展开：NapCat 返回为空，无内层内容）`，日志里降级为 WARNING，不与正常展开混淆。

## 群级启用范围（Enabled Group Scope）

插件只对配置的群生效。配置入口：AstrBot WebUI → 插件 → 本插件 → 配置，字段 `enabled_group_ids`（群号白名单，可填多个，纯数字）。

| 配置 | 行为 |
| --- | --- |
| 留空（默认） | **全部群**都保存快照并展开转发 |
| 填了群号 | 只处理列出的群；其他群的消息不落盘、不展开，只在 debug 级别记录跳过 |
| 填了群号时的私聊 | 不处理（白名单是群维度） |

插件加载时会把启用范围写进日志：

```
[SourceHub Inspector] 插件已加载，快照目录：…，启用范围：全部群（白名单留空）
[SourceHub Inspector] 插件已加载，快照目录：…，启用范围：836229427
```

每条处理日志都带 `群名(群号)`，便于确认消息来自哪个群。

## 安装与开发

首次通过 WebUI 插件管理上传仓库根的 `astrbot_plugin_sourcehub_inspector.zip`。同名目录已存在时不能重复安装。

用户偏好的开发方式：修改本仓库插件源码，覆盖 AstrBot 用户数据目录内 `data/plugins/astrbot_plugin_sourcehub_inspector/`，再在插件页选择“重载插件（Reload Plugin）”。不要同时在两份源码各自修改。

日志使用 AstrBot 基类 `self.logger`，前缀 `[SourceHub Inspector]`。重载后应看到“插件已加载”；收到消息后是“已保存消息快照”；消息含转发时多一行“已展开转发消息：层数=… 内层条数=… 段类型=…”。

## 测试方法

1. 在群里用带唯一内外层文字标记的样例转发：一层纯文本、一层带图、两层嵌套。
2. 看日志那行展开摘要，层数 / 条数应与实际相符。
3. 打开 `forwards/` 下最新 JSON，`messages` 就是内层每条消息；嵌套层在 `message[].data.content` 里。

## 已知限制（本轮未解决）

- **媒体未持久化**：内层图片只记录 `file` / `url`，图片临时文件会消失，不能算离线可读的收藏。上层 `Image` 段同理。
- **快照未脱敏**：仍递归保存整个 `event`（含 `bot` / `platform`），原始 CQ 码里的图片 URL 带 `rkey=` 鉴权参数。**不要公开或提交真实 JSON。**
- **事件身份不可靠**：`event_id` 仍读 `event.message_id`，可能回退成时间；没有重复检测。
- **深度上限 5 层**：超限内层只保留 id 不展开。
- 没有完整去重、异常隔离或正式服务。（群级来源白名单已在 0.3.0 补上，见上文）

来源：官方插件开发教程 https://docs.astrbot.app/dev/star/plugin-new.html 。
