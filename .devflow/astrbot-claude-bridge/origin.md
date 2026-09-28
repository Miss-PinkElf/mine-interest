# QQ 多代理 AstrBot 接入原始输入索引（Raw Input Source Index）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-28 21:43:08 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：索引本 mission 的原始需求与参考实现。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：已吸收至计划与设计回退记录（Indexed）
- 文档边界（Scope / Boundary）：原始输入索引真相源（source of truth）；不解释为已批准方案，不触发实施。

## 输入

- `zzz-prompt-debug/接入agent/prompt-01.md`：AstrBot 接入、QQ 对话、多编码代理（Coding Agent）、白名单及工作目录只读权限需求。
- `cc-ding/`：本地参考实现，包含钉钉接入、Claude Code 与 Codex 代理适配。
- 本次会话：用户明确要求使用 devflow 重型路径（Heavy Route）。
- 本次会话后续澄清：工具调用单独配置；白名单外用户只能访问当前工作目录下的文件，且不能编辑。
- 本次会话再次确认：白名单用户也限制在指定工作目录内，但允许读写。
- 本次会话确认：每个启用的 QQ 群配置一个固定工作目录。
- 本次会话提出：优先考虑把 `cc-ding` 的架构和成熟功能迁移到 AstrBot 插件，而非另起一套运行服务。
- 本次会话确认：采用迁移 `cc-ding` 通用核心、由 AstrBot 插件承接平台消息的设计方向。
- 本次会话确认：本轮只处理 Claude Code 与 Codex；群内共享会话，私聊另设权限，群级可设置只读与工具调用权限；OpenCode、Pi 后续再扩展，并要求模块化、低耦合、高内聚。
- 本次会话确认：白名单与群级策略取更严格者；共享会话下也逐条消息重新计算文件及工具权限；私聊单独配置。
- 本次会话确认：“完整迁移”包含 `cc-ding` 的 Web Console 管理能力与代理间通信（A2A）。
- 本次会话补充：插件最终在 Windows／macOS 原生运行，不以 Ubuntu／WSL 为前置条件；CLI 原生只读可作为候选，但工作目录外拒读仍是硬要求。
- 本次会话补充：允许测试 Codex elevated Windows 沙箱；测试结果已写入 `spec/permission-matrix.md`，授权不等于同意放宽文件权限。
- 本次会话收尾指令：根目录 `devflow-handoff.md` 只读作为指导；只提交本 mission 相关文件，默认不提交 `.gitignore`、`config.ts`、`tsconfig.json`；下一对话继续未解决的设计与实施。
