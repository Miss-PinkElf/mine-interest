# Metadata（元数据）

- 更新时间（Updated At）：2026-10-23 16:36:00 +08:00。
- 作者（Author）：rin（Claude 协助）。
- 目的（Purpose）：恢复插件诊断上下文。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/多种信息源整合.md`。
- 当前状态（Status）：交接中（Handoff）。
- 文档边界（Scope / Boundary）：本任务记录；诊断插件不代表完整信息中心已获准实施。

# 问题清单（Bug Log）

## 2026-10-23：B 站插件的正常处理流程没有日志

| 问题现象 | 问题原因 | 解决方案与状态 |
| --- | --- | --- |
| 在 AstrBot 平台日志里看不到 B 站插件的运行日志；B 站 @ 之后也无法判断是否收到通知、是否开始采集、是否保存成功。只有发布器/登录状态异常时才会出现 WARNING | `Poller.scan` 收到通知后不记录数量；`Poller.process` 在采集与保存成功后完全不写日志；GitHub 动作日志虽然调用 `self.logger`，但没有统一前缀，也不易筛选 | **已修复（2026-10-23）**。`scan` 记录「收到 N 条 B 站通知」；`process` 记录「开始采集 B 站通知：业务｜发送者｜标题」「采集未完成（原因）」「已保存 B 站条目」；GitHub 动作日志统一加 `[SourceHub Bilibili]` 前缀；自动化关闭但检测到链接时记录跳过原因。B 站插件升 `0.3.6`，新增日志测试，全量离线 **168 项通过**。**待重载后观察真实日志** |

## 2026-10-23：`/fork` 因 `--remote` 参数被 `gh repo fork` 拒绝

| 问题现象 | 问题原因 | 解决方案与状态 |
| --- | --- | --- |
| 打开 `github_enabled` 后，QQ 发送 `https://github.com/Blinue/Magpie /fork`，回复 `[失败] Blinue/Magpie：gh 执行失败：the \`--remote\` flag is unsupported when a repository argument is provided`；同一条消息里的 star 已成功（状态文件记录 `已 star`） | `gh repo fork` 在传入仓库参数时不允许出现 `--remote`，即使写成 `--remote=false` 也算该 flag 被设置。代码同时传了 `--clone=false` 与 `--remote=false` | **已修复（2026-10-23）**。fork 命令改为 `gh repo fork <repo> --clone=false --default-branch-only`，去掉 `--remote=false`；三份 `sourcehub` 副本同步；回归测试由「断言包含 `--remote=false`」改为「断言不包含」；inspector 升 `0.6.4`、B 站插件升 `0.3.5` 并覆盖现场；全量离线 **161 项通过**。**待重载后重发 `/fork` 验证真实 fork** |

补充证据：

- `github_actions.json` 记录：16:19:13 `star` 成功；16:19:57 `fork` 失败，报文即上述 `--remote` 错误。
- 该失败发生在 `gh` 参数校验阶段，尚未创建 fork，因此重试不会产生重复仓库。

## 2026-10-23：QQ 消息处理入口 `TypeError: 'bool' object is not callable`

| 问题现象 | 问题原因 | 解决方案与状态 |
| --- | --- | --- |
| 重载检查插件 `0.6.2` 后，QQ 任意消息都会在 `main.py:250` 抛 `TypeError: 'bool' object is not callable`。异常发生在 `inspect_message` 第一行，后续消息快照、成条入库、回复全部被跳过，**QQ 采集链路整体失效**；与 `github_enabled` 开关无关 | `__init__` 第 142 行把配置 `github_reply_enabled` 存成实例属性 `self._github_reply`（布尔），第 222 行又定义了同名方法 `_github_reply`。Python 中实例属性优先于类方法，调用 `await self._github_reply(event)` 实际变成 `await True(event)` | **已修复（2026-10-23）**。属性改名为 `self._github_reply_enabled`，同步更新 3 处引用；新增 `tests/test_sourcehub_plugin_names.py` 静态守卫，禁止实例属性遮蔽同名方法（已用旧部署副本验证能检出该缺陷）；inspector 升 `0.6.3` 并覆盖现场目录，`diff -rq` 一致；全量离线 **161 项通过**。**待重载后发普通 QQ 消息复验** |

补充证据：

- 现场与仓库两份 `main.py` 逐行一致，排除部署版本错位。
- 守卫只扫描 `integrations/astrbot/*/main.py`；当前只发现这一处冲突，B 站插件无同类问题。
- 离线测试原先只覆盖 `github_gate` 纯函数，未实例化插件主类，因此未捕获该运行时错误。

## 2026-10-15：QQ 日文档摘要多行截断

| 问题现象 | 问题原因 | 解决方案与状态 |
| --- | --- | --- |
| 群里发一条多行普通消息后，`items/qq/<日期>/content.md` 的「实时消息（Live Messages）」区只出现正文的**最后一行**，前面几行全部丢失。样本：2026-10-15 群 `836229427` 的消息 `1441885612`（204 字，7 行），日文档只留下了第二段 | `sourcehub/vault.py` 的 `append_daily_message` 用 `render_content_md(envelope).splitlines()[-1]` 取摘要。`render_content_md` 返回的是「封套头部元信息 + 正文」整篇 Markdown，取最后一行在**单行消息**下偶然等于正文，**多行消息**下必然只剩最后一行 | **已修复（2026-10-15）**。渲染层拆出 `markdown.py` 的 `_envelope_header_lines` / `_envelope_body_lines`，新增 `render_message_body_md`（`render_content_md` 输出保持字节级不变）；`vault.py` 新增 `format_daily_message_entry` 与 `DAILY_MESSAGE_CONTINUATION_INDENT`，多行正文按续行 2 空格缩进。已加回归测试（单行输出逐字不变 + 多行全保留）。历史条目已按日账本重投影。插件升版 inspector `0.6.1` / B 站 `0.3.3` 并覆盖插件目录，**待重载后真实消息复现验收**。计划见 `plans/2026-10-15-QQ日文档摘要多行截断修复与链路说明-plan.md` |
| 排查时误以为「日文档只有 1 条消息 = 采集漏了」 | 普通消息走日账本分支时不 `upsert`，当日目录下没有 `message/` 子目录。这是 2026-09-22 的既定设计（延迟成条），不是缺陷 | **不是 Bug**。`@机器人 整理` 或午夜调度成条后即出现 `message/` 目录。已记入链路说明文档 |

补充证据：

- 日志侧无异常。`backend.log` 22:10:15 有 `[Core] [Test-01(aiocqhttp)] C#/1961618848:` 原样消息与 `[SourceHub Inspector] 已保存消息快照`，没有 `成条入库失败`。
- 完整原文没有丢：日账本 `spool/qq_daily/836229427/2026-10-15.json` 存有 204 字全文；成条后 Item 的 `content.md` 也是全文。
- 在 Vault 副本上用真实代码复现 `render_content_md(env).splitlines()[-1]`，输出与日文档中那一行逐字一致，根因坐实。
- 影响面复扫「日文档摘要行 vs 日账本原文」全部日期：**仅 2026-10-15 这 1 条**。此前的日子恰好都是单行消息（`hihi`/`泥嚎`），缺陷被掩盖。
- 注：日文档是索引加摘要，不是真相源，因此本缺陷不构成数据丢失，但它会长期留在日文档里且不会被 `_write_daily_index` 自动覆盖（该函数会原样保留「实时消息」块）。

## 2026-09-29：播放地址与专栏链接卡片

| 问题现象 | 问题原因 | 解决方案与状态 |
| --- | --- | --- |
| 视频正文出现 `image:media_host_not_allowed`，封面已保存 | 播放地址主链接落在 PCDN（如 `mountaintoys.cn:4483`，`os=mcdn`）。采集器只取 `durl[0].url`，允许名单只有 `.hdslb.com` 和 `.bilivideo.com` | 代码已改：先用主地址或备用地址里已允许的链接；都不是时，仅对 `/upgcxcode` 的 PCDN 按 `og` 换成官方镜像。已成功的官方地址不改。插件 `0.3.2`。旧文档要重新采集才会变 |
| 专栏正文出现 `unknown_paragraph` 和一段 `link_card` JSON | 段落只有文字、图片、代码、分隔线四种；视频卡（`link_type` 1）和专栏卡（`link_type` 15）被原样留下 | 代码已改：视频卡写成 `av` 链接，专栏卡写成 `cv` 链接，自带 `link` 的卡片用原文链接。不认识的卡片仍保留 JSON 和缺口。旧文档要重新采集才会变 |

## 2026-09-28：运行核查新发现

| 问题现象 | 问题原因 | 解决方案与状态 |
| --- | --- | --- |
| 9 月 21、22 日 QQ 条目有 184 个本地媒体链接无法解析 | 这些条目迁移到 `日期/类型/标题-ID` 后，旧链接仍指向少一层 `../` 的相对路径；对应媒体文件均存在 | 已修复（2026-09-28 17:51）：按计划只给这 184 个链接补一层 `../`，7 个正文、资料目录与发布目录都已改。复核后本地相对链接 221 个全部可打开，B 站断链 0。未重新下载。备份：`sourcehub-qq-link-backup-20260928-175127` |
| B 站轮询反复报告 `ClientConnectorDNSError`，采集间歇失败 | 直连的域名解析或连接阶段失败；具体系统网络原因尚未定位，不能直接归因于 Cookie；本机无凭据 HTTP 代理已成功下载一张真实封面 | 用户于 2026-09-28 晚明确本轮暂缓。后续要求继续查采集网络时，再记录失败域名和环节。不是永久放弃 |
| 发布器间歇报告 `remote_private_unverified`，偶有 `git_push_failed` | 发布闸门仍要求匿名 GitHub API 返回 404。2026-09-28 晚该接口对本机返回 403 频率限制。已登录的 `gh` 能确认仓库私有且演练可推，页面变绿不会让这条发布日志消失 | 用户于 2026-09-28 晚明确本轮暂缓。后续要求修发布稳定性时，把发布闸门改成与插件页同一套已登录检查，并保留 SSH 演练 |

## 需求 4（2026-09-23）

| 问题现象 | 问题原因 | 解决方案与状态 |
| --- | --- | --- |
| B 站媒体直链可打开，但专栏图片下载失败 | B 站实际媒体域名含 `bilivideo.com`，原允许主机集合未覆盖；历史失败条目没有启动补救 | 扩展受控主机、最多 5 次直连重试、启动补救并回填；指定专栏 11 个媒体链接断链数为零，已解决 |
| 文章回填后 Vault `content.md` 中媒体链接仍失效 | Markdown 渲染器按逻辑 ID 而非实际日期/标题存储路径计算 `../` 层级 | 按实际存储路径计算相对媒体链接，目标测试与真实文章复验通过，已解决 |
| 目标仓库一度被误判为公开 | 已登录环境的 HTTPS 可访问性不能证明匿名可读 | 改用匿名 GitHub API 404 与 SSH 可读双重核验；真实检查通过，已纠正 |
| 首次自动推送暂无运行证据 | 2026-09-23 交接时 AstrBot 未运行，发布循环尚未在真实消息后触发 | 2026-09-28 复核发布目录远端跟踪分支 reflog，已有 `update by push`，最近为 14:57；已解决首次推送证据缺口。后续稳定性另见本日问题 |

## 按天归档（2026-09-22）

| 问题现象 | 原因 | 解决方案与状态 |
| --- | --- | --- |
| `qq:forward:1319423280` 的目录未进入 `2026-09-22` | 该转发在 18:05 由旧插件进程写入；按日期路径的检查器 0.5.4 于 18:16 才重载 | 对真实 Vault 重新预演，发现 2 条同类遗漏；原子补迁移、更新 catalog 与每日索引。预演剩余项为 0，已解决 |
| 日总文档在普通消息到来时不能即时阅读 | 仅有日账本，原先只在整理后产生 Item | 普通消息同时追加当天 `content.md` 的“实时消息（Live Messages）”区，已解决 |

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
