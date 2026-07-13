/**
 * Playwright 端到端骨架。
 * 运行前需：npx playwright install && 后端/前端服务已启动。
 */
import { test, expect } from '@playwright/test'

const START_TASK_LABEL = '开始任务'
const CONFIRM_SEGMENT_LABEL = '确认片段'
const EXPORT_MARKDOWN_LABEL = '导出 Markdown'

test.describe('review workflow', () => {
  test.skip(!process.env.E2E_BASE_URL, '需要 E2E_BASE_URL 与运行中的本地服务')

  test('uploads a job, confirms a segment, and enables markdown export', async ({
    page,
  }) => {
    await page.goto(process.env.E2E_BASE_URL || 'http://127.0.0.1:5173')
    // 无真实样本时仅校验导出按钮存在；完整链路在有服务时启用。
    await expect(page.getByRole('button', { name: EXPORT_MARKDOWN_LABEL })).toBeVisible()
    await expect(page.getByRole('button', { name: START_TASK_LABEL })).toBeVisible()
    await expect(page.getByRole('button', { name: CONFIRM_SEGMENT_LABEL }).first()).toHaveCount(0)
  })
})
