# 视频情感化转写工作流 Learnings

## Metadata（元数据）

- 创建时间（Created At）：2026-07-13 14:28:23 +08:00
- 更新时间（Updated At）：2026-07-13 14:28:23 +08:00
- 作者（Author）：Codex
- 目的（Purpose）：沉淀本 mission 踩坑与可复用经验。
- 关联仓库或项目（Related Repository / Project）：`mine-interest`
- 关联 mission（Related Mission）：`.devflow/video-emotion-transcript-workflow/`
- 当前状态（Status）：进行中（Active）
- 文档边界（Scope / Boundary）：经验记录，不是任务清单。

## 经验条目

### 2026-07-13 14:28:23 +08:00 - 清华 npm 镜像元数据 404

- 现象：前端依赖安装失败。
- 原因：镜像对包元数据返回 HTTP 404。
- 方案：经用户授权改用默认 npm / 可用 PyPI 源。

### 2026-07-13 14:28:23 +08:00 - tasks.md 与 implementation-plan 编号不一致

- 现象：plan 中 Task 4 是预处理，tasks.md 第 4 项是本地 API。
- 原因：两套编号并存。
- 方案：**以 `spec/tasks.md` 为实施勾选真相源**；plan 作步骤细节参考。

### 2026-07-13 14:28:23 +08:00 - Vitest 误收集 Playwright 规格

- 现象：`npm run test` 因 `@playwright/test` 无法解析失败。
- 原因：e2e 目录被 vitest include。
- 方案：`vitest.config.ts` 仅 include `src/**/*.test.{ts,tsx}`，exclude `e2e/**`。

### 2026-07-13 14:28:23 +08:00 - Ant Design 在 jsdom 需要 matchMedia

- 现象：组件测试 `window.matchMedia is not a function`。
- 方案：在 `frontend/src/test/setup.ts` 注入 matchMedia / ResizeObserver 桩。
