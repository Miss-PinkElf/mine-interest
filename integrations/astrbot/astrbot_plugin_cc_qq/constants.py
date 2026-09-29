"""插件标识、配置键与默认值（Plugin Constants）。"""

PLUGIN_NAME = "astrbot_plugin_cc_qq"
PLUGIN_VERSION = "0.1.2"
PLUGIN_DESCRIPTION = "通过 QQ 使用本机 Claude Code 与 Codex"
LOG_PREFIX = "[cc-qq]"

QQ_PLATFORM_NAME = "aiocqhttp"
DEFAULT_AGENT = "claude"
SUPPORTED_AGENTS = ("claude", "codex")
DEFAULT_MODEL = ""
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
DEFAULT_MODEL_KEY = "default_model"

DATABASE_NAME = "cc_qq.sqlite3"
MAX_QQ_TEXT_CHARS = 1500
DEFAULT_AGENT_TIMEOUT_SECONDS = 1800
PROCESS_TERMINATE_GRACE_SECONDS = 5
STDERR_TAIL_LINES = 20

CLAUDE_COMMAND = "claude"
CODEX_COMMAND = "codex"
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
AGENT_NOT_READY_REPLY = "QQ 消息接入已就绪，Claude Code／Codex 会话功能正在接入。"
