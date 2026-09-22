"""成条与落盘常量（Capture Constants）。"""

SCHEMA_VERSION = "1"

PLATFORM_QQ = "qq"
PLATFORM_BILIBILI = "bilibili"

GROUPING_SINGLE = "single"
GROUPING_MERGED_FORWARD = "merged_forward"
GROUPING_SESSION_MARKERS = "session_markers"
GROUPING_DAILY = "daily"
GROUPING_WORK_OBJECT = "work_object"

DEFAULT_SESSION_START = "，，，"
DEFAULT_SESSION_END = "。。。"
DEFAULT_SESSION_IDLE_SECONDS = 30 * 60
DEFAULT_MEDIA_MAX_BYTES = 100 * 1024 * 1024

GAP_SESSION_END_MISSING = "session_end_missing"
GAP_FORWARD_UNEXPANDED = "forward_unexpanded"
GAP_MEDIA_FAILED = "media_failed"
GAP_MEDIA_TOO_LARGE = "media_too_large"
GAP_EVENT_ID_MISSING = "event_id_missing"

NODE_TEXT = "text"
NODE_IMAGE = "image"
NODE_FILE = "file"
NODE_QUOTE = "quote"
NODE_FORWARD = "forward"
NODE_UNKNOWN = "unknown"

ITEM_DIR = "items"
MEDIA_DIR = "media"
SPOOL_DIR = "spool"
PRIVATE_EVENTS_DIR = "private/events"
CATALOG_FILE = "catalog.sqlite3"
ENVELOPE_FILE = "envelope.json"
CONTENT_FILE = "content.md"

WORK_VIDEO = "video"
WORK_ARTICLE = "article"
WORK_OPUS = "opus"
