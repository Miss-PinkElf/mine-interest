"""插件标识、配置键与默认值（Plugin Constants）。"""

PLUGIN_NAME = "astrbot_plugin_cc_qq"
PLUGIN_VERSION = "0.1.13"
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
DEFAULT_CLAUDE_MODEL_KEY = "default_claude_model"
DEFAULT_CODEX_MODEL_KEY = "default_codex_model"
DEFAULT_MODEL_KEY_BY_AGENT = {
    "claude": DEFAULT_CLAUDE_MODEL_KEY,
    "codex": DEFAULT_CODEX_MODEL_KEY,
}

DATABASE_NAME = "cc_qq.sqlite3"
MAX_QQ_TEXT_CHARS = 1500
DEFAULT_AGENT_TIMEOUT_SECONDS = 1800
PROCESS_TERMINATE_GRACE_SECONDS = 5
STDERR_TAIL_LINES = 20

CLAUDE_COMMAND = "claude"
CODEX_COMMAND = "codex"
CLAUDE_COMMAND_KEY = "claude_command"
CODEX_COMMAND_KEY = "codex_command"
CLAUDE_DEFAULT_PERMISSION_MODE = "bypassPermissions"
CODEX_DEFAULT_ACCESS_FLAG = "--dangerously-bypass-approvals-and-sandbox"

REASON_OUT_OF_SCOPE = "out_of_scope"
REASON_NOT_ALLOWED = "not_allowed"
REASON_CONFIGURATION_INVALID = "configuration_invalid"
REASON_WORK_DIR_MISSING = "work_dir_missing"

NOT_ALLOWED_REPLY = "当前 QQ 账号未获此会话授权，请联系插件管理员。"
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
SESSION_ENDED_REPLY = "当前会话已结束。"
NO_SESSION_TO_END_REPLY = "当前没有活跃会话。"
NO_SESSION_TO_RESUME_REPLY = "当前范围没有可恢复的历史会话。"
CC_USAGE_REPLY = "用法：/cc <代理消息>"
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
