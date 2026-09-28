# Metadata（元数据）

- 更新时间（Updated At）：2026-09-28 15:00:53 +08:00。
- 作者（Author）：Codex。
- 目的（Purpose）：为下一次对话提供短恢复入口和明确的未完成边界。
- 关联仓库（Related Repository）：`.`。
- 关联任务（Related Mission）：`.devflow/multi-source-hub/`。
- 最新交接（Latest Handoff）：`handoffs/2026-09-28-009-运行核查与上传延期.md`。
- 当前状态（Status）：需求 4 运行验收待续，远端媒体上传延期（Runtime Verification Pending / Media Upload Deferred）。
- 文档边界（Scope / Boundary）：恢复入口；不自动授权实施（Apply）。

# 下一次对话提示词

请恢复 `.devflow/multi-source-hub/`。默认先读 `state.md` 与 `checkpoints.md`，再读 `handoffs/2026-09-28-009-运行核查与上传延期.md`。需求 4 首版代码提交为 `2fae5a6`，当前仍在 Verify；不要重做已批准的 Align / Plan / Spec。优先处理 `bug-log.md` 2026-09-28 条目，实时核对 AstrBot 日志和 Vault，因为交接数字会随采集变化。

## 已完成且无需重做

- QQ 当天总文档与整理去重、按采集日归档的前序能力继续有效。
- 需求 4：QQ 新目录为 `日期/message|forward|session/标题-ID`，真实 Vault 17 项补迁完成；QQ/B 站最多 5 次直连下载；历史 B 站专栏媒体链接核查无断链，本机有 2 个 MP4。
- 检查器 0.5.5、B 站 0.2.5 已同步本机；2026-09-28 AstrBot 正在运行，已有新 B 站条目。
- 独立私有发布目录仅跟踪 Markdown；9 月 28 日 14:57 的 `origin/main` reflog 显示真实 `update by push`，先前“首次推送未证实”的交接判断已过时。2026-09-23 的 86 项离线测试、编译和差异检查通过。

## 未完成 / 下一步

1. 先诊断 B 站反复出现的 `ClientConnectorDNSError`：记录失败请求域名与网络环节，再用新的 B 站 `@` 验证。9 月 28 日新条目只证明间歇成功，不能视作稳定。
2. 旧 QQ 条目有 184 个本地媒体相对链接少一层 `../`，对应文件均存在。先做预演和修复计划，再修复真实 Vault，验证所有本地链接。
3. 用新 QQ 文字/转发与 B 站样本核对成条、目录、媒体和日志；`spec/2026-09-23-需求4/tasks.md` T7 仍未完成。
4. 现有 Markdown 发布间歇报 `remote_private_unverified`，需要区分匿名 API、SSH 与推送失败环节；2026-09-28 15:00 发布目录跟踪 47 份 Markdown、零个其他文件。远端媒体上传与 Git LFS 用户明确暂缓，触发条件见 `deferred/需求4首版未做与运行验收.md`。
5. 需求 5（B 站 Cookie 有效性检查/刷新）尚未对齐；如用户选择，单独 Align / Plan，不因 DNS 故障自动启动。多分段/高画质/持久队列、链接筛选与外层 14 项也未自动开工。

## 注意

- 不要提交 Cookie、真实快照、媒体或 `sourcehub-image-urls.json`；工作区存在其他会话可能暂存的候选计划、会话记录、ZIP 及 `zzz-prompt-debug/prompt-1.md` 改动，先辨别归属，不批量提交或清理。
- 不要把真实推送证据误写成发布稳定，也不要把远端媒体上传延期误写成永久放弃。
- 改动插件运行文件时同步递增 `metadata.yaml` 与注册版本，覆盖本机插件后重载。
- 需要完整演进时再读 `development-overview.md`；旧状态、原始输入和其他延期项仅按需读 `state-history.md`、`origin.md`、`backlog.md`、`deferred/`。
