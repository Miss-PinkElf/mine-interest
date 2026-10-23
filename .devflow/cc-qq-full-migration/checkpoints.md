# cc-qq 完整迁移最近检查点（Checkpoints）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 10:23:07 +08:00
- 更新时间（Updated At）：2026-10-23 00:00:00 +08:00
- 作者（Author）：Grok / Claude（Fable 5）
- 目的（Purpose）：记录本 mission 最近的阶段切换与继续位置。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/cc-qq-full-migration/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/完整迁移cc-ding/prompt-01.md`、`zzz-prompt-debug/接入agent/prompt-01.md`
- 当前状态（Status）：权限分级待真机验收（Permission Runtime Verification Pending）
- 文档边界（Scope / Boundary）：最近检查点真相源（source of truth）；仅保留最近三条，不代替对齐文档或计划。

## 2026-09-30 15:38:00 +08:00 — 已覆盖、已提交，验收留到下一对话

- 已完成：用户要求覆盖安装目录。代码提交为 `7a714ac`。用户声明已经重载 `0.1.14`。交接当时是 `handoffs/2026-09-30-003-三项修复待真实验收.md`。
- 当前阶段：当时本轮暂停。第一阶段运行验收未完成。
- 下一步：当时写成核对 `0.1.14` 再验三条。
- 注意：随后 15:44 保存配置清掉了私聊名单；本会话继续修到 `0.1.16`。

## 2026-09-30 16:08:00 +08:00 — 0.1.16 已提交，待重载

- 已完成：非白名单私聊静默、10 秒同一句去重。22 个单元测试通过。代码提交 `107409f`，安装目录已覆盖。交接是 `handoffs/2026-09-30-004-私聊静默与去重待重载.md`。
- 当前阶段：本轮暂停。AstrBot 尚未重载，运行中仍是 `0.1.14`。
- 下一步：用户重载后确认 `已加载 v0.1.16`，再验空白与非白名单私聊不回复。
- 注意：现场配置仍是私聊关闭、名单为空。`prompt-01.md` 的聚合需求仍未提交、未对齐。

## 2026-10-23 00:00:00 +08:00 — 权限分级 0.2.0 已实施，待提交与真机验收

- 已完成：权限档位、Claude 只读/审批/守护 hook、Codex 权限档案、`/cd`、`/pwd`、`/initbase`、审计表与基础模板。83 个单元测试通过。
- 本机验证：Claude 2.1.202 的 hook→broker→allow/deny 链路可用；只读 hook 阻止工作目录外读取；完全权限守护 hook 阻止 `/etc` 与 `~/.ssh` 写入；Codex 0.162.1 的 `ccqq-readonly`/`ccqq-workspace` 能限制工作区外读写。
- 当前阶段：代码已提交为 `0ad479e`，未推送；未生成 `v0.2.0` ZIP，未覆盖安装目录，AstrBot 尚未重载。
- 下一步：下次对话生成 ZIP、重载后按 T05.10 验收 guest 只读、member 工作区、目录外审批、`/cd`、`/initbase`。
- 注意：Codex 本轮没有逐次审批；审批卡片只在来源会话可见。
