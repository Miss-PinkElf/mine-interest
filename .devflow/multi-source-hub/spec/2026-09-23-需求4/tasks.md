# Metadata（元数据）

- 创建时间（Created At）：2026-09-23 15:33:49 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：按依赖顺序追踪需求 4 的实施与验收。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 原始需求（Original Requirement）：`zzz-prompt-debug/prompt-1.md` 第 34–38 行。
- 关联计划（Related Plans）：`../../plans/2026-09-23-QQ标题分层目录迁移-plan.md`、`../../plans/2026-09-23-直连下载重试与历史补救-plan.md`、`../../plans/2026-09-23-Vault安全自动发布-plan.md`。
- 当前状态（Status）：首版已实现，真实运行验收待完成（Implemented; Runtime Verification Pending）。
- 文档边界（Scope / Boundary）：本子变更的任务真相源（Source of Truth）；复选框需验证证据支撑。

# 需求 4 任务（Tasks）

- [x] T1：QQ 标题路径投影与合成测试；新路径为 `日期/类型/标题-ID`，稳定 ID 不变。
- [x] T2：历史 QQ 迁移、catalog 与每日索引回归；真实 Vault 预演零冲突后迁移 17 项，复验零剩余。
- [x] T3：QQ 和 B 站下载最多 5 次直连尝试；临时失败重试、确定性失败即停，测试验证系统代理不生效。
- [x] T4：B 站历史失败媒体启动补救；指定专栏 11 个媒体链接已核对无断链，重复回填不损坏原文。
- [x] T5：独立发布目录仅投影 `items/**/*.md`，脱除外链查询参数与已知凭据；合成测试确认排除原始封套、媒体及 Vault Git 历史。
- [x] T6：两插件启动后定期扫描并尝试普通推送；失败保留本地资料，下一轮与重启后重试。以重新扫描代替单独的持久待发布表，真实推送尚未验收。
- [ ] T7：离线回归、插件版本与本机同步、真实 Vault 迁移和远端私有性已核对；AstrBot 新消息运行及首次真实远端推送仍待用户启动后验收。
- [x] T8：B 站播放流 MP4 首版落盘与 Vault 链接；本机确认 2 个视频文件，媒体链接指向实际存储路径。

## 验证

使用 `backend/.venv/bin/python` 运行目标 `unittest` 与全量回归，执行 `git diff --check`；真实资料只用于本机验收，不加入代码仓库。无法完成远端真实验证时保留 T7 未完成，并说明具体阻塞。
