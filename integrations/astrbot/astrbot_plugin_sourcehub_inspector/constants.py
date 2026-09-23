"""检查插件共享常量（真相源）。

集中管理日志前缀、落盘目录名与转发接口相关常量，避免散落在各个模块里。
"""

LOG_PREFIX = "[SourceHub Inspector]"

# 快照与转发展开结果的落盘目录（相对 AstrBot 运行工作目录）
SNAPSHOT_DIR_NAME = "sourcehub-inspector/snapshots"
FORWARD_DIR_NAME = "sourcehub-inspector/forwards"

# OneBot v11 获取合并转发的接口名
GET_FORWARD_MSG_ACTION = "get_forward_msg"

# 消息段类型：合并转发
FORWARD_SEGMENT_TYPE = "forward"

# get_forward_msg 的参数名兼容列表。
# 不同 OneBot 实现分别使用 message_id / id，按顺序尝试。
FORWARD_ID_PARAM_KEYS = ("message_id", "id")

# 嵌套展开深度硬上限，防止异常数据造成无限递归。
# 实测样例最深 3 层；超过上限的内层保留原样并标记截断。
MAX_FORWARD_DEPTH = 5

# 超过深度上限时写入的标记字段
FORWARD_TRUNCATED_KEY = "_sourcehub_truncated"

# 获取失败时写入的标记字段
FORWARD_ERROR_KEY = "_sourcehub_error"

# 插件配置项：启用检查的群号白名单（留空表示全部群启用）
ENABLED_GROUP_IDS_KEY = "enabled_group_ids"
COLLECT_ENABLED_KEY = "collect_enabled"
PUBLISH_ENABLED_KEY = "publish_enabled"
VAULT_DIR_KEY = "vault_dir"
SESSION_START_KEY = "session_start"
SESSION_END_KEY = "session_end"
MEDIA_MAX_BYTES_KEY = "media_max_bytes"
TIMEZONE_KEY = "timezone"
ORGANIZE_COMMAND_KEY = "organize_command"
DEFAULT_TIMEZONE = "Asia/Shanghai"
DEFAULT_ORGANIZE_COMMAND = "整理"
DEFAULT_VAULT_DIR = "data/sourcehub"

# 白名单留空时日志里的说明文案
ALL_GROUPS_SCOPE_LABEL = "全部群"
