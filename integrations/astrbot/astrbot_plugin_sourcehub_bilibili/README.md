# Metadata（元数据）

- 创建时间（Created At）：2026-09-21 13:04:29 +08:00
- 更新时间（Updated At）：2026-09-28 16:38:00 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：说明 B 站只读提及采集插件的安装、配置、数据位置、失败补取与验证边界。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联计划（Related Plan）：`.devflow/multi-source-hub/plans/2026-09-21-B站只读提及采集-plan.md`。
- 关联规格（Related Spec）：`.devflow/multi-source-hub/spec/bilibili-readonly/`。
- 当前状态（Status）：需求 7 实施中（In Progress）；真实扫码、迁移和邮件尚待验收。
- 文档边界（Scope / Boundary）：使用说明；需求 7 真相源见 `.devflow/multi-source-hub/spec/2026-09-28-需求7/`。不批准自动回复。

# SourceHub B 站只读采集（Read-only Mention Collection）

收到 B 站 @ 通知后，把触发评论、直接父评论、根评论和作品原文保存到本地，并按作品合并进统一资料目录（同一视频/专栏/动态多次 @ 只有一个 `item`、一篇 `content.md`）。插件复用 AstrBot 的配置与生命周期（Lifecycle），不注册发送评论、私信、点赞等写接口，也不会自动公开回复。

本机可以同时安装完整 BiliBot（`astrbot_plugin_bilibili_ai_bot`），二者职责不同：BiliBot 会互动；本插件只采集。不要用 BiliBot 的自动回复替代本插件。

通知入口与 BiliBot 相同：`/x/msgfeed/at`。本插件只读取，不调用 `/x/v2/reply/add` 等写接口。

## 启停

1. 在 AstrBot WebUI 打开本插件配置。
2. `enabled` 默认 `false`。保持停用时插件会加载并打日志「未启用采集」，不会轮询。
3. 可先填写本地 `sessdata`，也可运行下方扫码工具。把 `enabled` 设为 `true`，再重载插件（Reload Plugin）。
4. 停用：把 `enabled` 改回 `false` 并重载；退出 AstrBot 时会取消轮询任务并关闭会话。

没有登录配置时不会采集；若已知账号 UID 且配置了告警，则会记录登录失效事件。

## 登录配置

在 WebUI 本插件配置中填写，**不要把 Cookie 发到聊天或提交到 Git**。

| 字段 | 含义 | 默认 |
| --- | --- | --- |
| `enabled` | 是否启动只读采集（Read-only Collection） | `false` |
| `sessdata` | 账号登录凭证（SESSDATA） | 空 |
| `buvid3` | 浏览器设备标识（buvid3） | 空 |
| `bili_jct`、`refresh_token` | 已有登录态的刷新凭据；扫码后自动保存在本地凭据文件 | 空 |
| `account_id` | 告警去重所用数字 UID；成功登录后自动写入 | 空 |
| `poll_seconds` | 轮询间隔秒数（Polling Interval） | `120`，最小 `60` |
| `media_max_bytes` | 单媒体最大字节数（Media Limit） | `104857600`（100 MiB） |
| `vault_dir` | 统一资料目录（Vault），与 QQ 成条共用 | `data/sourcehub` |
| `publish_enabled` | 启用私有仓库安全自动发布；只发布 Markdown | `true` |
| `alert_enabled`、`alert_remote` | 启用独立私有 GitHub 告警仓库和其 SSH remote | `false`、空 |
| `network_proxy` | 可选本机 HTTP 代理（Local HTTP Proxy），用于 B 站接口与媒体访问 | 空 |

本插件使用自己的凭据文件，不读取 BiliBot 配置。扫码登录（QR Login）在本机终端运行：

```text
<AstrBot 使用的 Python 解释器> -m integrations.astrbot.astrbot_plugin_sourcehub_bilibili.login_cli --credentials <AstrBot 插件数据目录>/credentials.json
```

二维码只显示在本机终端；成功后凭据文件权限为 `0600`。插件轮询时检查登录态，并在平台确认需要刷新且本地有刷新令牌时更新 Cookie。网络错误只记为“未知”，不报登录失效。扫码工具依赖 `qrcode`，刷新依赖 `cryptography`，均已列入 `requirements.txt`。仓库的 `backend/.venv` 当前没有这两项依赖，需在 AstrBot 插件依赖安装后使用其解释器运行扫码工具。若本机直连解析失败，可在插件配置和扫码命令 `--proxy` 中填同一本机代理地址。

专用提醒仓库与资料仓库必须分开。创建私有 GitHub 仓库、设置 SSH 访问，并在 GitHub 的仓库推送邮件设置中启用通知后，填写两插件相同的 `alert_remote`，再打开 `alert_enabled`。首次确认故障和恢复各推送一次，持续故障不重复；仓库仅包含脱敏状态事件，不含 Cookie、二维码、资料正文或媒体。

## 数据位置

运行数据在 AstrBot 用户目录，不写进仓库：

```text
data/plugin_data/astrbot_plugin_sourcehub_bilibili/<账号 mid>/
  notifications/<通知编号>.json
  items/<通知编号>/record.json
  items/<通知编号>/content.md
  items/<通知编号>/media/
  cursor.json
```

本机绝对路径一般是 `~/.astrbot/data/plugin_data/astrbot_plugin_sourcehub_bilibili/<账号 mid>/`。每个登录账号一个子目录。落盘路径由通知编号和账号编号构成，不用标题或外部路径控制。

## 存量文档迁移（Existing Item Rerender）

新排版从 `record.json` 的作品、评论和媒体映射重新生成；不会解析旧 `content.md`，也不会在插件启动时自动批量改写旧资料。先运行只读预演：

```text
PYTHONPATH=.:backend/src backend/.venv/bin/python tools/preview_bilibili_rerender.py --archive-root <B站插件数据目录> --vault <SourceHub资料目录>
```

预演会列出记录、作品、源图片与本地媒体缺口、待补封面及现有断链。网络恢复并确认 AstrBot 已停止采集后，增加 `--apply` 执行；如需本机代理，再加 `--proxy http://127.0.0.1:7897`。工具先备份整个 B 站条目树、catalog 与原始记录，再补媒体并逐作品重渲染。补取失败的作品保持原样。备份目录默认位于 Vault 同级。

如需回滚（Rollback），保持 AstrBot 停止，使用相同的 `--archive-root`、`--vault`，并加 `--rollback <备份目录>`。若迁移后出现新 B 站条目或原始记录变化，工具会拒绝整树回滚，避免删掉新采集内容；此时需按备份内容逐条恢复。

## 状态含义与失败补取

| 状态 | 含义 |
| --- | --- |
| 完整（Complete） | 所需评论、作品正文和媒体都成功。按作品重渲染时会从原始记录生成 `content.md`。 |
| 部分（Partial） | 已保存能拿到的内容，并在 `record.json` 的 `gaps` 与 `content.md` 的「未完成项」里写明缺口。后续轮询会按字段合并（Field Merge）补齐。 |

字段合并规则：新一轮成功的对象、评论、来源链接、已下载图片覆盖对应字段；新一轮失败或空结果保留上一轮原文和原始对象。不能把 Partial 直接当成 Complete。标题、通知摘要、来源链接不能证明全文存在。

图片按内容魔数保存，不信任 URL 后缀。超过 `media_max_bytes` 记为未完成，不改成缩略图。**没有自动清理**归档。

`cursor.json` 只表示通知扫描进度，不表示内容已经采全。

## 不公开回复

插件没有发送评论、私信、点赞或动态的入口。日志只记录错误类别或业务码，不打印 Cookie，也不把登录凭证带到图片下载会话。

## 安装

推荐开发方式（与检查插件相同）：把仓库源码覆盖到 AstrBot 插件目录后重载。

```text
integrations/astrbot/astrbot_plugin_sourcehub_bilibili/
→ ~/.astrbot/data/plugins/astrbot_plugin_sourcehub_bilibili/
```

也可在 WebUI 上传仓库根目录的 `astrbot_plugin_sourcehub_bilibili.zip`。安装包只含源码、配置、依赖列表和本说明，不含虚拟环境、缓存、私人数据和凭证。同名目录已存在时改为覆盖源码，不要卸掉 QQ 检查插件。

依赖：`aiohttp`、`beautifulsoup4`、`markdownify`、`cryptography`、`qrcode`。AstrBot 会按 `requirements.txt` 安装到用户 `site-packages`。

重载后应看到：

```text
[SourceHub Bilibili] 未启用采集
```

在填写登录并启用之前，这是预期日志。

## 样本验收

离线测试：

```text
backend/.venv/bin/python -m unittest discover -s tests -p 'test_bilibili*.py' -v
```

离线通过只证明内部逻辑。真实验收需要能接收 @ 的本地登录态，并由用户发出测试 @，助手不得擅自公开发消息。五类样本：

1. 视频顶层 @
2. 回复根评论 @
3. 回复子评论 @
4. 动态评论 @
5. 专栏评论 @

核对：触发/父/根评论、完整简介或图文全文、来源页面链接、图片离线可读、重复轮询与失败补取。

## 当前限制

- 工程默认值（停用、120 秒、50 MiB、不清理）尚未作为长期产品策略单独确认。
- 当前扫描接口可见的 @ 通知；不承诺平台不再提供的历史。
- 未做发送者白名单；真实扫码和刷新需在网络恢复后验收。
- 当前首版会尝试下载接口返回的单段 MP4，并保存到 Vault 媒体目录；不保证最高画质、多分段、断点续传或任意视频可下载。远端自动发布仅包含 Markdown，不上传 MP4。
- 未知正文节点会保留原始 JSON 并标 Partial。

## 来源依据

- 通知接口与 BiliBot 的 `/x/msgfeed/at` 契约一致，仅借鉴读取，不复制自动互动实现。
- 图文/专栏结构参考 BBDownNext Opus 提取器的公开说明，不复制其代码。
