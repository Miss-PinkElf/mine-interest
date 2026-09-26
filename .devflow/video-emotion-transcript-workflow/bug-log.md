# 视频情感化转写工作流问题日志

## Metadata（元数据）

- 创建时间（Created At）：2026-07-10 16:05:12 +08:00
- 更新时间（Updated At）：2026-09-27 00:47:18 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：记录 Apply（实施）阶段出现的可复现问题、根因与处理状态。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 关联计划（Related Plan）：`plans/2026-07-10-video-emotion-transcript-mvp-implementation-plan.md`
- 当前状态（Status）：已解除（Resolved）
- 文档边界（Scope / Boundary）：本文件是实施问题记录，不替代任务清单、规格或验证结果。

## 2026-07-10 - 清华 npm 镜像无法安装前端依赖

- 问题现象（Symptom）：在 `frontend/.npmrc` 配置 `https://mirrors.tuna.tsinghua.edu.cn/npm/` 后，`npm ping` 与 `npm view react version` 均返回 HTTP 404；直接请求镜像的 `npm/react` 路径同样返回 HTTP 404。
- 问题原因（Root Cause）：该清华镜像地址当前不提供 npm Registry（npm 注册表）所需的包元数据接口，无法解析 React 等依赖；并非本项目 package 配置或 `npm ping` 端点兼容性问题。
- 解决方案（Resolution）：用户已授权切换为 npm 默认源（default registry），`frontend/.npmrc` 已改为 `https://registry.npmjs.org/`；随后安装依赖并执行前端构建验证。
- 复现命令（Reproduction）：`cd frontend && npm view react version --registry=https://mirrors.tuna.tsinghua.edu.cn/npm/`
- 影响（Impact）：已改用默认 npm Registry（npm 注册表）完成前端 `npm install` 与生产构建；该问题不再阻塞后续实施。

## 2026-07-13 14:28:23 +08:00 - Vitest 误收集 Playwright 规格

- 问题现象：`npm run test` 报无法解析 `@playwright/test`。
- 问题原因：e2e 规格被 vitest 默认收集。
- 解决方案：`frontend/vitest.config.ts` 限制 `include` 为 `src/**/*.test.{ts,tsx}`，`exclude` `e2e/**`。

## 2026-09-27 00:28:28 +08:00 - 旧任务异步片段覆盖新任务

- 问题现象（Symptom）：任务 A 的片段查询延迟返回时，用户上传任务 B 后，A 的片段可能出现在 B 的审核页并错误解锁导出按钮。
- 问题原因（Root Cause）：只依赖 React effect 的清理标记；上传 B 到旧 effect 清理之间存在短暂窗口。
- 解决方案（Resolution）：写入任务状态或片段前，再比对当前会话任务 ID；新增延迟旧响应的竞态测试。
- 验证：`frontend/src/App.test.tsx` 中旧响应与新上传交错用例通过。

## 2026-09-27 00:28:28 +08:00 - 人工修订未持久化

- 问题现象（Symptom）：审核页修改文本后确认，刷新或导出仍使用原始转写。
- 问题原因（Root Cause）：编辑器仅修改本地 state，确认回调未调用既有文本修订 API。
- 解决方案（Resolution）：确认前顺序调用文本修订 API 与确认 API；修订保存失败时不确认，新增页面与后端 API 验证。
- 验证：前端用例检查调用顺序；后端 API 用例检查 `raw_text` 保留、`edited_text` 与两种导出使用修订文本。

## 2026-09-27 00:47:18 +08:00 - 首次并发请求重复初始化数据库

- 问题现象（Symptom）：浏览器首次同时请求任务接口时，后端偶发 `sqlite3.OperationalError: table jobs already exists`。
- 问题原因（Root Cause）：API 运行时（API Runtime）的懒加载单例在多个请求线程中并发构建，两个初始化过程同时建表。
- 解决方案（Resolution）：为运行时单例初始化增加线程锁（threading.Lock），并以并发请求测试固定该边界。
- 验证：并发初始化测试由失败转绿；完整后端测试 28 passed；本地浏览器上传成功。

