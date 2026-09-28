# Metadata（元数据）

- 创建时间（Created At）：2026-09-28 16:21:00 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：规定需求 7 的数据流、接口与失败边界。
- 关联仓库（Related Repository / Project）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 50–58 行。
- 计划（Plans）：`plans/2026-09-28-需求7-B站原文排版与封面迁移-plan.md`、`plans/2026-09-28-需求7-登录检查与GitHub告警-plan.md`。
- 当前状态（Status）：已批准实施（Approved for Apply）。
- 文档边界（Scope / Boundary）：技术设计（Design）真相源；接口细节可随已验证的 API 事实更新，不自动扩大范围。

# Design（技术设计）

## 总体思路

采集记录（Raw Record）保存完整作品和评论 JSON；投影器（Projector）仅从该记录与本地媒体映射生成封套（Envelope）。B 站专用渲染器输出已认可的作品顺序。身份探针（Identity Probe）输出 `healthy`、`login_required` 或 `unknown`；QQ 探针额外输出持续断线。告警状态机（Alert State Machine）处理去重、恢复与待送队列，独立 Git 发布器只发布脱敏事件。

## 结构与边界

- `content.py`：只转换原始富文本标记；不处理告警，也不从视觉语气推断标题。
- `collector.py` / `store.py`：下载封面、正文与评论媒体并保留 URL 到本地文件的映射；不回读旧 Markdown 当源内容。
- `bili_ingest.py` / `bili_merge.py`：按作品与评论 ID 合并；不同触发事件共享一份作品与同 ID 上级评论。
- `markdown.py`：按平台分派；B 站输出 H1、链接与时间、封面、正文、真实附件、评论，QQ 维持原模板。
- `auth.py` / `qq_status.py`：把平台 API 的证据分类；只有明确信号才产生需重登事件。
- `alerts.py` / `alert_publish.py`：前者原子保存最小状态和待送事件，后者核验私有 remote 并推送独立目录；不访问资料发布树。

## 数据流与接口

1. 原始 `record.json` → 格式转换 → 作品/评论片段 → 按作品 ID 合并的 `envelope.json` → 可再生成的 `content.md`。
2. 媒体 URL → 校验域名/大小/类型 → SHA-256 文件名 → Vault `media/` → 相对链接。封面只在标题下，正文图片留原位置，视频文件只在附件列一次。
3. 平台状态 → `observe(platform, account, status, observed_at)` → 原子状态文件与待送事件 → 私有仓库单次提交/推送 → `mark_delivered(event_id)`。未知状态不推进登录故障或恢复。
4. 迁移工具默认只读预演；显式 `--apply` 时先备份，再按作品顺序重建；记录缺失或断链则跳过该条。

## 复用点

- 媒体下载沿用现有白名单、上限和重试；Vault 沿用原子写入、catalog 和每日索引。
- 私有 remote 核验复用 `sourcehub/publish.py` 的现有函数；告警 Git 工作目录与资料 Git 目录分离。
- B 站扫码与刷新以已有本机参考插件和实测接口为依据；不读取参考插件凭据。

## 风险与权衡

- 旧记录可能缺少完整原文或媒体，迁移逐条验证后保留旧条目与缺口；不能用现有渲染文本冒充原文。
- QQ 连接状态 API 可能只暴露连接中断；文案必须反映证据级别。
- GitHub 推送成功与电子邮件投递是两个环节；真实邮件需单独验收。
- 资料目录与现有 Git 可能有并发写入，迁移需停采或使用明确互斥与备份；未经验证不批量覆盖。
