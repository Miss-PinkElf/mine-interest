# Metadata（元数据）

- 更新时间（Updated At）：2026-09-09 18:55:33 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：说明诊断插件安装、测试及已知限制。
- 关联仓库（Related Repository）：mine-interest-source-hub（`.`）。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 当前状态（Status）：诊断原型（Diagnostic Prototype），不用于正式收藏。
- 文档边界（Scope / Boundary）：使用说明；问题真相源为 `.devflow/multi-source-hub/bug-log.md`。

# SourceHub 消息检查器（Message Inspector）

已在 AstrBot Desktop v4.27.5 的 QQ 官方适配器上生成真实消息快照。仅保存 JSON，不自动回复，不接完整信息中心。

## 安装与开发

首次通过 WebUI 插件管理上传仓库根的 `astrbot_plugin_sourcehub_inspector.zip`。同名目录已存在时不能重复安装。

用户偏好的开发方式：修改本仓库插件源码，覆盖 AstrBot 用户数据目录内 `data/plugins/astrbot_plugin_sourcehub_inspector/main.py`，再在插件页选择“重载插件（Reload Plugin）”。不要同时在两份源码各自修改。

使用 AstrBot 基类 `self.logger` 输出，前缀 `[SourceHub Inspector]`。在平台日志勾选 INFO；重载后检查“插件已加载”，发送消息后检查“已保存消息快照”。

## 保存与实测边界

快照相对运行工作目录保存到 `data/sourcehub-inspector/snapshots/`，文件名使用 UTC 时间。源码没有复制图片或下载转发附件：图片路径可能指向随后被清理的临时文件，不能算持久收藏。

本轮测试：普通文本保存；表情包和图片留下临时路径；一层转发有展示文本和附件 URL；多层转发内部内容未完整取得。不要将缺失直接归因于 QQ 平台，需进一步调查原始字段和获取接口。

当前递归整个事件、深度截断及字符串兜底有局限；可能保存临时鉴权字段。不要公开或提交真实 JSON。后续需限定消息字段、脱敏、媒体持久化、正确身份提取和错误处理。当前没有来源白名单、重复标记或完整去重。

来源：官方插件开发教程 https://docs.astrbot.app/dev/star/plugin-new.html 。
