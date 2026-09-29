# Metadata（元数据）

- 创建时间（Created At）：2026-09-21 18:38:00 +08:00
- 更新时间（Updated At）：2026-09-29 10:55:00 +08:00。
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
8. GitHub 匿名接口容易被限流并返回 403。页面上的私有性要用已登录的 `gh` 判断。真正发布资料的闸门如果仍调用匿名检查，日志里的 `remote_private_unverified` 不会因为页面变绿而消失。
9. B 站播放地址的主链接经常是 PCDN。`mountaintoys.cn` 是 2025 年的调度域名，非 443 端口和 `os=mcdn` 都是信号。先用备用地址里的 `.bilivideo.com`；没有时只改写 `/upgcxcode` 的主机，按 `og` 选官方镜像。`/v1/resource` 不要改写。专栏 `link_type` 1 是视频 `av`，15 是专栏 `cv`。自带 `link` 的卡片直接用原文链接。
