# Metadata（元数据）

- 创建时间（Created At）：2026-09-21 18:38:00 +08:00
- 更新时间（Updated At）：2026-10-23 12:00:00 +08:00。
- 作者（Author）：Grok
- 目的（Purpose）：沉淀本轮成条切片的踩坑。
- 关联仓库或项目（Related Repository / Project）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：有效（Active）。
- 文档边界（Scope / Boundary）：经验记录，不是需求真相源。

# 经验

1. AstrBot 把插件当包加载（`data.plugins.<plugin_name>`），插件目录里的 `sourcehub/` 必须用相对导入 `from .sourcehub...`，不能当顶层包。
2. 在 `async` 消息处理里用同步 `urllib` 下图会卡住整个事件循环（本轮约 10 分钟），B 站轮询和后续 QQ 消息一起停。应先 upsert 条目，下载放到 `asyncio.to_thread`。
3. 会话标记不要只做「整句等于中文标点」。手机输入常带空格，或打成英文 `, , ,` / `。 。 。`。匹配前去空白并归一化中英文逗号/句号。
4. 已 complete 的采集档案不会再走 `save()`，新 Vault 必须另做 `export_existing` 回填。
5. `media/` 是哈希库；给人看的是 `items/<id>/content.md`。会话里的嵌套转发按当时规则是子块，不是第二条。
6. 改 AstrBot 插件后要做三件事：提高 `metadata.yaml` 和 `PLUGIN_VERSION`，整份覆盖到 `~/.astrbot/data/plugins/<插件名>/`，再重载。只改仓库，运行中的进程不会变。
7. 插件页的业务脚本必须写在 `/api/plugin/page/bridge-sdk.js` 之后。写在前面时 `AstrBotPluginPage` 还不存在，页面会停在初始文案。登录状态和仓库校验要分开请求，一个挂起不能挡住另一个。
8. 交接写「还没重载」时，先看后端日志里的最后一次 `Plugin astrbot_plugin_sourcehub_bilibili (版本)`，再用插件列表接口核对。磁盘文件已经是新版本，不代表进程没加载；2026-09-29 10:52 已经加载 `0.3.2`，11:03 的交接仍写成未重载。
8. GitHub 匿名接口容易被限流并返回 403。页面上的私有性要用已登录的 `gh` 判断。真正发布资料的闸门如果仍调用匿名检查，日志里的 `remote_private_unverified` 不会因为页面变绿而消失。
9. B 站播放地址的主链接经常是 PCDN。`mountaintoys.cn` 是 2025 年的调度域名，非 443 端口和 `os=mcdn` 都是信号。先用备用地址里的 `.bilivideo.com`；没有时只改写 `/upgcxcode` 的主机，按 `og` 选官方镜像。`/v1/resource` 不要改写。专栏 `link_type` 1 是视频 `av`，15 是专栏 `cv`。自带 `link` 的卡片直接用原文链接。
10. **不要从「整篇渲染结果」里抠一行当摘要。** 2026-10-15 的日文档多行截断就是这么来的：`render_content_md(envelope).splitlines()[-1]` 在单行消息下偶然等于正文，多行消息下必然只剩最后一行。需要「正文」就问渲染层要正文（本轮加了 `render_message_body_md`），不要用 `[-1]`、固定行号、或「跳过以 `- ` 开头的行」这类启发式——后者会误伤以列表开头的消息，固定行号会在带缺口小节时错位。
11. **同一段代码被两种数据形态共用时，缺陷会只在一种形态下暴露。** 这个截断在 2026-09-22 到 09-30 一直没被发现，只因为那几天的群消息恰好都是单行（`hihi`/`泥嚎`）。写回归测试时要显式覆盖「多行」这一形态，别只测一行。
12. **改共享库时要连历史数据一起想。** 修好代码只解决「以后」；已经写坏的记录不会自己变好，而且 `_write_daily_index` 会原样保留摘要块。修历史要用**与修复后同一个函数**重投影（本轮一次性命令按日账本重建），不要手工敲一遍——那样格式会与代码漂移，且不可复现。改真实 Vault 前先备份。
13. **`unittest discover` 必须带 `-t .`。** `tests/__init__.py` 用相对导入做引导，`discover -s tests` 会把 `tests` 当顶层目录，导致 `test_sourcehub_vendoring` 报 `attempted relative import with no known parent package`。正确命令：`PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'`。
14. **验证「纯重构」要比对输出，不能只看测试绿。** 本轮把改动前的 `markdown.py` 从 `HEAD` 取出，对 8 类封套（QQ 单行/多行/带缺口/图片/转发树/未知节点/文件节点 + B 站作品）逐字比对 `render_content_md`。既有测试绿只能说明没测到差异，不能说明没有差异。
15. **在 fork 里装同步工作流，会天然让 fork 领先上游。** `gh repo sync` 默认只做快进，遇到工作流提交会失败；`--force` 会把工作流一起删掉，下一次定时任务就没了。正确做法是工作流内 `git fetch upstream` + `git merge` + `git push`，只同步默认分支。2026-10-23 需求 8 因此没有采用 `gh repo sync`。
16. **GitHub Actions 在 fork 里默认可能未启用。** 安装工作流后要尝试 `gh workflow enable <file> -R <fork>`；失败时必须在回复或页面里明确提示用户去 Actions 页手动启用，不能静默当作完成。
17. **AstrBot 插件运行时找不到 `gh` 是真实风险。** 桌面版进程的 PATH 未必包含 Homebrew；`GithubRunner` 必须按「配置路径 → `shutil.which` → `/opt/homebrew/bin/gh` → `/usr/local/bin/gh`」依次查找，不能只依赖 PATH。
18. **用 AstrBot 内置 Python 做现场导入验证，比只看仓库测试更接近真实加载。** 命令：`PYTHONPATH=$HOME/.astrbot/data/plugins:/Applications/AstrBot.app/Contents/Resources/backend/app /Applications/AstrBot.app/Contents/Resources/backend/python/bin/python -c "import astrbot_plugin_sourcehub_inspector.main, astrbot_plugin_sourcehub_bilibili.main"`。它不需要真的启动 AstrBot，也不会触发网络副作用。
