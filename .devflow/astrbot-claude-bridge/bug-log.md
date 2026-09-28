# 代理目录权限问题清单（Bug Log）

## Metadata（元数据）

- 创建时间（Created At）：2026-09-29 00:21:05 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录 T02 的可复现失败、原因和后续解决动作。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/astrbot-claude-bridge/`
- 原始需求（Raw Requirement）：`zzz-prompt-debug/接入agent/prompt-01.md`
- 实施计划（Implementation Plan）：`.devflow/astrbot-claude-bridge/plans/2026-09-28-cc-ding完整迁移astrbot插件计划.md`
- 当前状态（Status）：待解决（Open）
- 文档边界（Scope / Boundary）：本文件记录已观察的问题，不将候选解法视为批准方案；以 `spec/permission-matrix.md` 为测试证据。

## T02-01｜Codex 内置只读可读取目录外文件

- 问题现象：原生 Windows 使用 `codex sandbox -P ':read-only'`，工作目录外的同级哨兵文件仍可读取；工作目录内写入则被拒。
- 问题原因：内置只读约束写入，不提供本需求要求的工作目录外拒读。
- 解决方案：该组合保持关闭；重新设计具有目录外拒读能力的执行边界，并用真实 CLI、子进程、联接目录、恢复会话样本验证。尚未解决。

## T02-02｜Codex 根目录拒读配置无法在 Windows 沙箱启动

- 问题现象：`:root = deny` 自定义配置在普通 Windows 沙箱要求 elevated；加 `windows.sandbox="elevated"` 后返回 `requires effective ':root' read access`。测试命令未执行。
- 问题原因：当前 Codex CLI 0.158.0 的两个本机 Windows 后端均未接受这组根目录拒读配置；elevated 启动前明确校验根目录可读。
- 解决方案：回退开放规格（OpenSpec）设计，调查原生 Windows 可运行的进程级隔离方案；保持 Codex 代理执行关闭，直到目录内读写及目录外拒读样本全部通过。尚未解决。

## T02-03｜elevated 在临时测试目录启动错误

- 问题现象：`:root = read` 的 elevated 配置在仓库目录可执行，在系统临时测试目录返回 `CreateProcessWithLogonW failed: 267`。
- 问题原因：尚未查明；可能与测试目录对沙箱用户的可见性有关，不能据此断言。
- 解决方案：下一轮先隔离复现并核对有效工作目录及权限；该配置本身允许根目录读取，不能作为需求的安全方案。尚未解决。
