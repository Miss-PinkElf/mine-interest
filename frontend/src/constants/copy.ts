/** 工作台界面文案常量（中文 + 英文术语）。 */

// 产品主标题。
export const APPLICATION_TITLE = '视频情感化转写'
// 主导航：任务页标签。
export const NAV_JOBS_LABEL = '任务'
// 主导航：设置页标签。
export const NAV_SETTINGS_LABEL = '设置'
// 上传媒体字段标签，供无障碍与测试定位。
export const UPLOAD_MEDIA_LABEL = '选择本地媒体'
// 开始处理任务按钮文案。
export const START_TASK_LABEL = '开始任务'
// 当前任务状态区域标题。
export const TASK_STATUS_TITLE = '任务状态'
// 导出区域标题。
export const EXPORT_PANEL_TITLE = '导出'
// Markdown 导出按钮。
export const EXPORT_MARKDOWN_LABEL = '导出 Markdown'
// JSON 导出按钮。
export const EXPORT_JSON_LABEL = '导出 JSON'
// Provider 设置标题。
export const PROVIDER_SETTINGS_TITLE = '云端 Provider 设置'
// API Key 输入标签。
export const PROVIDER_API_KEY_LABEL = 'API Key'
// Base URL 输入标签。
export const PROVIDER_BASE_URL_LABEL = 'Base URL'
// 模型名输入标签。
export const PROVIDER_MODEL_LABEL = '模型名'
// 保存设置按钮。
export const SAVE_SETTINGS_LABEL = '保存设置'
// 保存成功提示。
export const SETTINGS_SAVED_MESSAGE = '设置已保存到本机服务'
// 上传成功提示。
export const UPLOAD_SUCCESS_MESSAGE = '任务已创建'
// 显式选择假转写模式的复选框标签。
export const DEMO_MODE_LABEL = '使用演示转写（Fake STT）'
// 任务和审核页共用的演示来源声明。
export const DEMO_MODE_NOTICE = '演示数据：内容由假转写引擎生成，并非上传媒体的真实转写。'
// 人工修订或确认请求失败时的默认提示。
export const SEGMENT_CONFIRM_FAILED_MESSAGE = '保存修订或确认片段失败'
// 确认片段按钮。
export const CONFIRM_SEGMENT_LABEL = '确认片段'
// 已确认且内容未改变时的按钮文案。
export const SEGMENT_ALREADY_CONFIRMED_LABEL = '已确认'
// 片段确认成功后的操作反馈。
export const SEGMENT_CONFIRMED_MESSAGE = '片段已确认'
// 导出成功但任务状态查询失败时的提示。
export const TASK_STATUS_REFRESH_FAILED_MESSAGE = '文件已导出，但任务状态刷新失败，请刷新页面'
// 切分片段按钮。
export const SPLIT_SEGMENT_LABEL = '切分片段'
// 合并片段按钮。
export const MERGE_SEGMENT_LABEL = '合并片段'
// 删除片段按钮。
export const DELETE_SEGMENT_LABEL = '删除片段'
// 证据冲突提示文案。
export const CONFLICT_REVIEW_COPY = '证据存在冲突，请人工复核'
// 审核工作台标题。
export const REVIEW_WORKSPACE_TITLE = '片段审核工作台'
// 证据面板标题。
export const EVIDENCE_PANEL_TITLE = '证据面板'
// 原始文本标签。
export const RAW_TEXT_LABEL = '原始转写'
// 修订文本标签。
export const EDITED_TEXT_LABEL = '人工修订'
// API Key 不会写入浏览器 localStorage 的说明。
export const API_KEY_STORAGE_HINT = 'API Key 仅提交到本机 FastAPI，不会写入浏览器 localStorage'
