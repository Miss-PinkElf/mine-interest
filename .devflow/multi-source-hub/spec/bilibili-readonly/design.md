# Metadata（元数据）

- 创建时间（Created At）：2026-09-21 11:00:00 +08:00
- 更新时间（Updated At）：2026-09-21 15:51:15 +08:00
- 作者（Author）：Codex。
- 目的（Purpose）：明确采集模块、状态和数据边界。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 关联计划（Related Plan）：`../../plans/2026-09-21-B站只读提及采集-plan.md`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md`。
- 当前状态（Status）：首版已验收（Completed First Version）。
- 文档边界（Scope / Boundary）：本子变更设计真相源（Source of Truth）。

# 设计（Design）

- `main.py` 创建客户端、存储与轮询任务；默认不开启；关闭时取消任务和释放连接。不监听 QQ 消息，不注册公开回复工具。
- `client.py` 只提供读取请求，固定 API 端点，独立匿名媒体会话。请求失败只记录错误类别/业务码，不打印 Cookie 或含鉴权查询的链接。
- `poller.py` 拉取通知、先持久化再移动游标；待处理队列从本地通知重建。每条失败不阻断其他通知；完整条目不重采。
- `collector.py` 定位评论和作品；直接父评论与根评论分别保存；缺失不是不存在。评论类型及对象编号使用平台字段；动态对象编号与动态页面编号不能混用，优先从通知 URI 解析动态标识。
- `content.py` 负责正文转换与附件发现；结构变化报为不完整；原始响应不截断保存。
- `store.py` 原子写入，使用通知编号和账号编号构建路径，禁止标题或外部路径控制落盘位置；完整项不覆盖。部分项重试按字段合并（Field Merge）：成功结果覆盖对应字段，失败或空结果保留已保存原文、原始对象和本地图片；合并后仍有缺口则保持部分状态（Partial）。

成功状态（Complete）要求作品正文、所需评论及媒体均成功。部分状态（Partial）保留已获取内容和缺失原因，后续轮询可补齐。不能把 Partial 直接视为 Complete。首次启动保存当前通知页面可见的历史通知；不承诺平台不再提供的历史。

不自动清理归档；单媒体下载上限作为可调资源保护，触顶记录不完整，不偷换成缩略图。原文含私人数据，运行数据位于 AstrBot 数据目录，不写进仓库。
