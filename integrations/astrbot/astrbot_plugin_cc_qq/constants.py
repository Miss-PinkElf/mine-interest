"""插件标识、配置键与默认值（Plugin Constants）。"""

PLUGIN_NAME = "astrbot_plugin_cc_qq"
PLUGIN_VERSION = "0.2.5"
PLUGIN_DESCRIPTION = "通过 QQ 使用本机 Claude Code 与 Codex"
LOG_PREFIX = "[cc-qq]"

QQ_PLATFORM_NAME = "aiocqhttp"
DEFAULT_AGENT = "claude"
SUPPORTED_AGENTS = ("claude", "codex")
DEFAULT_PRIVATE_ENABLED = False
DEFAULT_GROUP_RULES_JSON = "{}"

PLATFORM_ID_KEY = "qq_platform_id"
ENABLED_GROUP_IDS_KEY = "enabled_group_ids"
GROUP_RULES_JSON_KEY = "group_rules_json"
PRIVATE_ENABLED_KEY = "private_enabled"
PRIVATE_USER_IDS_KEY = "private_user_ids"
PRIVATE_WORK_DIR_KEY = "private_work_dir"
OWNER_QQ_ID_KEY = "owner_qq_id"
ADMIN_QQ_IDS_KEY = "admin_qq_ids"
GLOBAL_ALLOWED_USER_IDS_KEY = "global_allowed_user_ids"
DEFAULT_AGENT_KEY = "default_agent"
GUEST_PERMISSION_PROFILE_KEY = "guest_permission_profile"
MEMBER_PERMISSION_PROFILE_KEY = "member_permission_profile"
OWNER_PERMISSION_PROFILE_KEY = "owner_permission_profile"
DANGER_APPROVAL_ENABLED_KEY = "danger_approval_enabled"
DANGER_APPROVAL_TIMEOUT_SECONDS_KEY = "danger_approval_timeout_seconds"
ALLOWED_WORK_DIRS_KEY = "allowed_work_dirs"
CLAUDE_SETTING_SOURCES_KEY = "claude_setting_sources"
READONLY_MCP_ENABLED_KEY = "readonly_mcp_enabled"
DEFAULT_CLAUDE_MODEL_KEY = "default_claude_model"
DEFAULT_CODEX_MODEL_KEY = "default_codex_model"
DEFAULT_MODEL_KEY_BY_AGENT = {
    "claude": DEFAULT_CLAUDE_MODEL_KEY,
    "codex": DEFAULT_CODEX_MODEL_KEY,
}

DATABASE_NAME = "cc_qq.sqlite3"
MAX_QQ_TEXT_CHARS = 1500
DEFAULT_AGENT_TIMEOUT_SECONDS = 1800
DEFAULT_GUEST_PERMISSION_PROFILE = "readonly"
DEFAULT_MEMBER_PERMISSION_PROFILE = "workspace"
DEFAULT_OWNER_PERMISSION_PROFILE = "full"
DEFAULT_DANGER_APPROVAL_ENABLED = True
DEFAULT_DANGER_APPROVAL_TIMEOUT_SECONDS = 300
MIN_DANGER_APPROVAL_TIMEOUT_SECONDS = 30
MAX_DANGER_APPROVAL_TIMEOUT_SECONDS = 3600
DEFAULT_CLAUDE_SETTING_SOURCES = ""
DEFAULT_READONLY_MCP_ENABLED = True
# deepseek-web 在服务端抓网页，碰不到本机与内网；本机 fetch 直连 URL，存在内网访问风险。
MCP_DEEPSEEK_SERVER_RULE = "mcp__deepseek-web"
MCP_LOCAL_FETCH_SERVER_RULE = "mcp__fetch"
DENIED_NATIVE_WEB_TOOL_RULES = ("WebSearch", "WebFetch")
APPROVAL_BROKER_HOST = "127.0.0.1"
APPROVAL_HOOK_TIMEOUT_MARGIN_SECONDS = 30
APPROVAL_ENV_HOST = "CC_QQ_APPROVAL_HOST"
APPROVAL_ENV_PORT = "CC_QQ_APPROVAL_PORT"
APPROVAL_ENV_TOKEN = "CC_QQ_APPROVAL_TOKEN"
APPROVAL_ENV_TIMEOUT = "CC_QQ_APPROVAL_TIMEOUT"
AGENT_ENV_PROFILE = "CC_QQ_PERMISSION_PROFILE"
AGENT_ENV_ROLE = "CC_QQ_ROLE"
AGENT_ENV_WORK_DIR = "CC_QQ_WORK_DIR"
AGENT_ENV_CONVERSATION_KEY = "CC_QQ_CONVERSATION_KEY"
AGENT_ENV_SENDER_ID = "CC_QQ_SENDER_ID"
AGENT_ENV_ORIGIN = "CC_QQ_ORIGIN"
AGENT_POLICY_DIR_NAME = "agent_policy"
APPROVAL_HOOK_SCRIPT_NAME = "approval_hook.py"
GUARD_HOOK_SCRIPT_NAME = "guard_hook.py"
READONLY_HOOK_SCRIPT_NAME = "readonly_hook.py"
APPROVAL_HOOK_DIR_NAME = "hooks"
GUARD_HOOK_TIMEOUT_SECONDS = 30
APPROVAL_SUMMARY_MAX_CHARS = 300
APPROVAL_PENDING_STATUS = "pending"
APPROVAL_APPROVED_STATUS = "approved"
APPROVAL_DENIED_STATUS = "denied"
APPROVAL_TIMEOUT_STATUS = "timeout"
BASE_TEMPLATE_DIR_NAME = "templates"
BASE_TEMPLATE_ROOT_NAME = "base"
STALE_MESSAGE_MAX_AGE_SECONDS_KEY = "stale_message_max_age_seconds"
DEFAULT_STALE_MESSAGE_MAX_AGE_SECONDS = 180
PRIVATE_DUPLICATE_WINDOW_SECONDS = 10
ONEBOT_MILLISECOND_TIMESTAMP_THRESHOLD = 10_000_000_000
STDERR_LOG_LINE_COUNT = 5
STDERR_LOG_LINE_CHARS = 200
PROCESS_TERMINATE_GRACE_SECONDS = 5
STDERR_TAIL_LINES = 20

CLAUDE_COMMAND = "claude"
CODEX_COMMAND = "codex"
CLAUDE_COMMAND_KEY = "claude_command"
CODEX_COMMAND_KEY = "codex_command"

REASON_OUT_OF_SCOPE = "out_of_scope"
REASON_CONFIGURATION_INVALID = "configuration_invalid"
REASON_WORK_DIR_MISSING = "work_dir_missing"

CONFIGURATION_INVALID_REPLY = "当前会话的插件配置无效，请联系插件管理员检查群配置。"
WORK_DIR_MISSING_REPLY = "当前会话尚未配置工作目录，请联系插件管理员。"
UNSUPPORTED_SEGMENT_REPLY = "当前阶段只支持文本消息；图片、文件和引用将在后续阶段接入。"
EMPTY_MESSAGE_REPLY = "请在 @ 机器人后输入文本或命令。"
SERVICE_ERROR_REPLY = "处理消息时发生错误，请联系插件管理员查看日志。"
AGENT_NO_TEXT_REPLY = "代理没有返回文本，请检查代理登录状态和插件日志。"
INTERRUPTED_ON_RESTART_REPLY = (
    "上一条请求在插件重启时中断，结果未确认；"
    "可发送 /goon 继续当前代理会话，或重发请求。"
)
NO_RUNNING_AGENT_REPLY = "当前没有正在执行的代理。"
AGENT_INTERRUPTED_REPLY = "已中断当前代理执行。"
GOON_INTERRUPTED_PREFIX = "已中断上一条执行。\n"
EXECUTION_STARTED_REPLY = "已收到，正在处理，完成后会回复。期间可发送 /! 中断。"
SESSION_ENDED_REPLY = "当前会话已结束。"
NO_SESSION_TO_END_REPLY = "当前没有活跃会话。"
NO_SESSION_TO_RESUME_REPLY = "当前范围没有可恢复的历史会话。"
CC_USAGE_REPLY = "用法：/cc <代理消息>"
NO_COMMAND_PERMISSION_REPLY = "当前角色无权使用该命令。"
CD_USAGE_REPLY = "用法：/cd list 查看可切换目录；/cd <序号> 切换；/cd <工作目录> 切换。"
CD_NOT_CONFIGURED_REPLY = "插件尚未配置 allowed_work_dirs，无法切换工作目录。"
CD_OUTSIDE_ROOTS_REPLY = "目标目录不在允许范围内，请联系插件管理员更新 allowed_work_dirs。"
CD_NOT_DIRECTORY_REPLY = "目标路径不存在或不是目录。"
CD_RUNNING_REPLY = "当前有代理正在执行，请先发送 /! 中断后再切换工作目录。"
CD_SUCCESS_TEMPLATE = "已切换工作目录：{work_dir}\n当前会话已结束，下一条消息将在新目录开始。"
CD_LIST_HEADER = "可切换的工作目录（按 allowed_work_dirs 配置顺序）："
CD_LIST_ITEM_TEMPLATE = "{index}. {work_dir}"
CD_LIST_CURRENT_MARKER = "  ← 当前"
CD_LIST_CURRENT_TEMPLATE = "当前工作目录：{work_dir}"
CD_LIST_HINT = "发送 /cd <序号> 切换。"
CD_LIST_EMPTY_REPLY = "当前没有可切换的工作目录。"
CD_INDEX_OUT_OF_RANGE_TEMPLATE = "序号超出范围：可用范围为 1-{max_index}，发送 /cd list 查看。"
CD_LIST_KEYWORD = "list"
PWD_TEMPLATE = "工作目录：{work_dir}\n角色：{role}\n权限档：{profile}\n代理：{agent_type}"
INITBASE_SUCCESS_TEMPLATE = "基础模板初始化完成：新建 {created} 个，跳过 {skipped} 个已存在文件。"
INITBASE_FAILED_REPLY = "基础模板初始化失败，请检查工作目录与插件日志。"
INITBASE_NOTHING_TEMPLATE = "基础模板已存在，未新建文件（跳过 {skipped} 个）。"
APPROVAL_USAGE_REPLY = "用法：/approve <审批号> 或 /deny <审批号>"
APPROVAL_NOT_FOUND_REPLY = "审批号不存在、已处理或已过期。"
APPROVAL_APPROVED_REPLY = "已批准审批 #{approval_id}。"
APPROVAL_DENIED_REPLY = "已拒绝审批 #{approval_id}。"
APPROVAL_REQUEST_TEMPLATE = (
    "🔐 危险操作审批 #{approval_id}\n"
    "发起人：{sender_id}\n"
    "工具：{tool_name}\n"
    "操作：{summary}\n"
    "回复 /approve {approval_id} 批准，或 /deny {approval_id} 拒绝（群聊请先 @ 机器人）；{timeout} 秒后自动拒绝。"
)
APPROVAL_TIMEOUT_REPLY = "审批 #{approval_id} 超时，已默认拒绝。"
APPROVAL_DISABLED_REPLY = "危险操作审批未启用，已拒绝该操作。"
APPROVAL_BROKER_ERROR_REPLY = "审批服务不可用，已拒绝该操作。"
NO_COMMANDS_REPLY = "当前角色没有可用命令。"
NEW_SESSION_REPLY_TEMPLATE = "已新建会话 #{session_id}，代理：{agent_type}。"
RESUMED_SESSION_REPLY_TEMPLATE = "已恢复会话 #{session_id}，代理：{agent_type}。"
NO_WORK_DIR_REPLY = "工作目录不存在"
MAX_AGENT_OUTPUT_LINE_BYTES = 1_048_576
NO_ACTIVE_SESSION_REPLY = "当前没有活跃会话，请发送消息或使用 /new 开始。"
CONTINUE_PROMPT = "继续"
SESSION_ACTIVE = "active"
SESSION_ENDED = "ended"
RECEIPT_PROCESSING = "processing"
RECEIPT_QUEUED = "queued"
RECEIPT_DONE = "done"
RECEIPT_CANCELLED = "cancelled"
RECEIPT_ERROR = "error"
RECEIPT_INTERRUPTED = "interrupted"
RECEIPT_DELIVERY_FAILED = "delivery_failed"
