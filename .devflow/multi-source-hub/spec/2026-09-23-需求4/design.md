# Metadata（元数据）

- 创建时间（Created At）：2026-09-23 15:33:49 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：说明需求 4 的模块边界和数据流。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38 行。
- 关联计划（Related Plans）：`../../plans/2026-09-23-QQ标题分层目录迁移-plan.md`、`../../plans/2026-09-23-直连下载重试与历史补救-plan.md`、`../../plans/2026-09-23-Vault安全自动发布-plan.md`。
- 当前状态（Status）：首版已实现，真实运行验收待完成（Implemented; Runtime Verification Pending）。
- 文档边界（Scope / Boundary）：本子变更的设计真相源（Source of Truth）。

# 需求 4 设计（Design）

## 总体思路

三个子变更按 QQ 路径、媒体下载、安全发布的顺序交付。路径和下载先稳定本地资料；发布只读取最终资料投影。

## 结构与边界

- `sourcehub.paths` 只计算相对存储路径（Storage Path），QQ 标题从已有内容节点提取，不调用外部模型；逻辑身份保持原值。
- `sourcehub.migration` 先产生预演清单，确认零冲突后移动目录、更新 catalog 并重建每日索引。已有迁移器承担事务外的文件移动；异常时保留可再次预演的状态。
- `sourcehub.download` 与 B 站客户端（Bilibili Client）分别处理同步和异步直连下载，使用同一上限和错误分类；不读取系统代理。
- B 站补救入口（Repair Entry Point）在插件启动时处理原始记录中未成功的媒体，复用哈希媒体落盘与 Vault 回填，不复制整条通知。播放流首版写入 MP4；Markdown 媒体链接按实际存储路径计算相对层级。
- 发布器（Publisher）从 Vault 读取允许文件，先移除外链查询参数及已知凭据片段，再同步到独立工作目录，独立初始化 Git；单工作器串行提交、普通快进推送。未能安全脱敏时停止该轮发布，原始 Vault 内容不变；下一轮继续扫描待发布更新。

## 数据流与接口

`采集 -> Envelope -> 路径投影 -> Vault 写入 -> 定期重新扫描 -> 允许清单投影 -> 独立 Git commit/push`。失败时不修改源资料，下一轮或重启后重新扫描；首版未单设持久待发布表。

媒体下载走 `URL -> 主机/大小校验 -> 直连请求 -> 可恢复错误重试 -> 哈希存储 -> 回填 Vault`。补救与新采集共享后半段。

## 复用点

复用 `safe_title`、`plan_migration`、`execute_migration`、`Vault.upsert`、现有媒体哈希和每日索引。内嵌到两插件的 `sourcehub` 文件与后端真相源同步。

## 风险与权衡

QQ 标题变动会改变物理路径，因此历史迁移必须在部署新插件前完成；远端发布不能使用现有 Vault Git 历史。Markdown 本身可能含鉴权链接，发布投影会移除 URL 查询参数和已知凭据，残留可识别凭据时拒绝推送。远端私有性和 SSH 读取已核验；未执行首次真实推送，不能声称远端已有资料。
