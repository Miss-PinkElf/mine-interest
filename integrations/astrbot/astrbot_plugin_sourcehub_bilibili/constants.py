"""接口契约和业务常量（Protocol and Business Constants）。"""

PLUGIN_NAME = "astrbot_plugin_sourcehub_bilibili"
PLUGIN_VERSION = "0.2.4"
LOG_PREFIX = "[SourceHub Bilibili]"
API_BASE = "https://api.bilibili.com"
SITE_BASE = "https://www.bilibili.com"
ENDPOINTS = {
    "identity": "/x/web-interface/nav",
    "mentions": "/x/msgfeed/at",
    "comment": "/x/v2/reply/detail",
    "replies": "/x/v2/reply/reply",
    "video": "/x/web-interface/view",
    "playurl": "/x/player/playurl",
    "dynamic": "/x/polymer/web-dynamic/v1/detail",
    "opus": "/x/polymer/web-dynamic/v1/opus/detail",
    "article": "/x/article/view",
}
VIDEO_COMMENT = 1
ARTICLE_COMMENT = 12
DYNAMIC_COMMENTS = {11, 17}
COMPLETE = "complete"
PARTIAL = "partial"
PENDING = "pending"
EMPTY_BODY_GAP = "empty_body"
PARENT_MISSING_GAP = "parent_missing"
ROOT_MISSING_GAP = "root_missing"
NO_PARENT_ID = "0"
PARENT_ID_KEYS = ("parent_str", "parent")
ROOT_ID_KEYS = ("root_str", "root")
COLLECTION_GAP_PREFIX = "collection:"
OBJECT_GAP_PREFIX = "object:"
IMAGE_GAP_PREFIX = "image:"
TRIGGER_GAP_PREFIX = "trigger:"
PARENT_GAP_PREFIX = "parent:"
ROOT_GAP_PREFIX = "root:"
CONTENT_STATUS_PREFIX = "采集状态（Collection Status）："
CONTENT_GAPS_HEADING = "## 未完成项"
DEFAULT_POLL_SECONDS = 120
MIN_POLL_SECONDS = 60
REQUEST_TIMEOUT_SECONDS = 30
PAGE_SIZE = 20
MAX_SCAN_PAGES = 50
MAX_COMMENT_PAGES = 50
MAX_ITEMS_PER_CYCLE = 20
MAX_FORWARD_DEPTH = 8
MEDIA_MAX_BYTES = 100 * 1024 * 1024
MEDIA_CHUNK_BYTES = 64 * 1024
MEDIA_HOST_SUFFIX = ".hdslb.com"
USER_AGENT = "Mozilla/5.0 SourceHub-Bilibili/0.1"
OPUS_FEATURES = "itemOpusStyle,opusBigCover,htmlNewStyle"
NOTIFICATION_DIR = "notifications"
ITEM_DIR = "items"
RECORD_FILE = "record.json"
CONTENT_FILE = "content.md"
CURSOR_FILE = "cursor.json"
MEDIA_DIR = "media"
