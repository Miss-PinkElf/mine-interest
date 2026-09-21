# Metadata（元数据）

- 更新时间（Updated At）：2026-09-21 18:38:00 +08:00
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：恢复插件诊断上下文。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 当前状态（Status）：交接中（Handoff）。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 问题清单（Bug Log）

## 成条入库（2026-09-21 18:38）

| 问题现象 | 原因 | 解决方案与状态 |
| --- | --- | --- |
| 两插件重载失败 `No module named 'sourcehub'` | AstrBot 以包加载插件，顶层 `from sourcehub` 找不到插件内目录 | 改为 `from .sourcehub...`。已解决 |
| 表情包会话收口后约 10 分钟无后续成条，B 站 `TimeoutError` | `collect_event` 同步 urllib 下 159 张图卡住事件循环 | 先 upsert，下载放到 `asyncio.to_thread`。已解决 |
| B 站专栏/动态/多次 @ 不进 Vault | complete 档案 `save()` 直接 return；轮询被卡住 | `export_existing` 回填；complete 仍导出。已解决 |
| `, , ,` / `。 。 。` 不成会话 | 整句必须等于中文 `，，，`/`。。。` | 去空白并归一化中英文逗号/句号。已解决 |
| 不嵌套转发条目几乎无正文 | NapCat `get_forward_msg` 对该 id 返回空列表 | **未解决**（平台空包）。可再转一次 |
| 会话 `content.md` 像一堆散图 | 阅读层平铺内层图片，无转发分组标题 | **未解决**。首版延期，见 deferred |

## B 站只读采集审查修复（2026-09-21）

| 问题现象 | 原因 | 解决方案与状态 |
| --- | --- | --- |
| 部分归档重试覆盖已拿到的原文和 `objects` | `store.save()` 只保护 Complete，Partial 直接整文件覆盖 | 按字段合并：失败/空结果保留旧正文和对象；合并后仍有缺口保持 Partial。已用回归覆盖 |
| 单条 `AttributeError` 卡住后续通知 | `process()` 未捕获，失败项不写 `attempted_at` | 隔离普通异常并落盘；`CancelledError` 传播；`desc is None` 等链式空值改为 `as_map`。已用回归覆盖 |
| 空 delta / 空节点 / 空 HTML 被标 Complete | 只检查字段存在，不看渲染结果 | 内容层无文本且无图片记 `empty_body` |
| 标题/通知/链接把空正文冲成 Complete | 落盘时用组装后 Markdown 是否非空来清除 `empty_body` | 空正文缺口只在本轮内容层不再报告、且非采集失败时才清除。聚焦复审发现并补回归 |
| 缺失或 null 的 parent/root 当成没有父评论 | `.get(...) or ''` 把缺失和明确 `0` 混在一起 | 缺失/null 记 `parent_missing`/`root_missing`；明确零值才表示顶层。已用回归覆盖 |
| 图文动态有图无正文，`body_missing` 重复多次 | Opus 详情每个模块都带空的 `module_content`（protobuf 风格），空段落被当成缺正文 | 只解析有段落/图片的模块；回退 `major.opus.summary`；合并时清掉已补上的 `body_missing`。33 项测试通过，两条真实动态已完整 |

## 已解决

| 问题现象 | 原因 | 解决方案与状态 |
| --- | --- | --- |
| 安装 ZIP 提示同名目录存在 | 此前已手动复制插件目录 | 用户授权删除旧目录，2026-09-09 18:32 安装成功；此后统一源码覆盖并重载。已解决 |
| 无前缀日志但 JSON 已生成 | 独立 logging 记录器未接 AstrBot 日志通道 | 三处改 `self.logger`，前缀 `[SourceHub Inspector]`。已解决 |
| **多层转发内层内容缺失**（原 T07 卡点） | 推送事件里的转发段只有 `{"type":"forward","data":{"id":"<res_id>"}}`，正文要二次调 OneBot `get_forward_msg`；插件从不调用。**不是平台限制** | 新增 `forward_expander.py`，调 `get_forward_msg` 递归展开。2026-09-20 18:50 用户实测通过：3 层 / 35 条 / 157 图 / 19 文本。已解决 |
| 嵌套转发按内层 id 递归取不到 | 实测 NapCat 对嵌套层内联 `content`，按内层 id 再请求会 `retcode 1200` | 递归**优先使用内联 `content`**，缺失才按 id 补取。已解决 |
| 插件对所有群生效，快照噪音大 | 没有来源范围控制 | 新增 `_conf_schema.json` 的 `enabled_group_ids` 白名单；留空=全部群。已解决 |
| `.txt` 里图片 URL 被截断，打开报 `invalid rkey` | 渲染器有 200 字符截断上限，把 237 字符的 URL 砍成 211 字符 | URL 改为**完整输出、单独一行、禁止截断**。已解决（这是本轮引入又修掉的自身缺陷） |
| 展开出的图存成 `.jpg` 但内容是 GIF | `file` 字段扩展名不可信 | 媒体落盘按**内容魔数**判断扩展名。本轮手动抢救时已按此改名；插件侧待实现 |

## 未解决

| 问题现象 | 原因 | 解决方案与状态 |
| --- | --- | --- |
| 图片/表情包未持久保存 | 插件只记录 `file` + `url`（腾讯 CDN，含 `rkey` 鉴权），不下载。AstrBot 的 `data/temp/media_image_*` 临时文件一分钟内即被清理 | **成条 Vault 已下载**到 `~/.astrbot/data/sourcehub/media/`。检查插件快照仍只存 URL。自动清理仍延期 |
| `rkey` 会过期，URL 不可长期依赖 | 腾讯 CDN 鉴权参数有有效期 | **未解决**。实测同一批 157 个 URL 中已有个别失效；越晚抢救能救回的越少 |
| 机器人自己发的消息从未进入 AstrBot | 定位到 NapCat `handleMsg`：`if (isSelf && !adapter.config.reportSelfMessage) continue`。配置里 `reportSelfMessage=true`，但运行实例疑似未应用（配置写入时间晚于进程启动） | **未解决**。需重启 NapCat 后复测；若仍失败，考虑换 NapCat 版本或插件侧 `get_group_msg_history` 回填（回填需先做去重） |
| 快照可能携带临时鉴权信息 | 递归整个 `event`（含 `bot`/`platform`），raw CQ 码含 `rkey=` | **未解决**。待限定消息字段并脱敏；不上传、不提交现有快照 |
| 事件身份回退时间，重复检测未实现 | 错读 `event.message_id`，真实字段在 `message_obj` | **未解决**。诊断快照不等于正式幂等收藏；回填方案依赖它 |
| 展开深度硬上限 5 层 | 防异常数据无限递归 | 保留。超限写 `_sourcehub_truncated`；实测样例最深 3 层，暂不构成阻塞 |
| 个别转发 `get_forward_msg` 返回空 | 直连 NapCat 复核同一 id 仍返回 `status=ok, retcode=0, messages=[]`；**不是插件问题** | 无插件侧解法。日志已降级为 WARNING，可读文本标注「未展开」 |

详细证据见 `handoffs/2026-09-20-003-个人号转发展开跑通与媒体待落盘.md`。
