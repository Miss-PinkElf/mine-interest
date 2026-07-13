# 片段未提供开始时间时使用的时间轴起点。
DEFAULT_SEGMENT_START_SECONDS = 0.0
# 片段未提供结束时间时使用的默认结束位置。
DEFAULT_SEGMENT_END_SECONDS = 0.0
# 证据尚无模型评分时使用的保守置信度。
DEFAULT_ENTITY_CONFIDENCE = 0.0
# 个人本地模式下审核操作的默认操作者标识。
DEFAULT_LOCAL_USER_ID = "local_user"

# 新建任务等待进入处理管线时的状态键。
JOB_STATUS_PENDING = "pending"
# 任务正在执行媒体或模型处理时的状态键。
JOB_STATUS_PROCESSING = "processing"
# 任务已生成结果并等待人工审核时的状态键。
JOB_STATUS_REVIEW = "review"
# 任务全部片段经人工确认后的状态键。
JOB_STATUS_CONFIRMED = "confirmed"
# 任务已生成最终导出文件后的状态键。
JOB_STATUS_EXPORTED = "exported"
# 任务在某个阶段无法继续时的状态键。
JOB_STATUS_FAILED = "failed"

# 片段尚未由人工确认时的审核状态键。
SEGMENT_REVIEW_STATUS_PENDING = "pending"
# 片段已由人工确认时的审核状态键。
SEGMENT_REVIEW_STATUS_CONFIRMED = "confirmed"

# 片段尚未完成分析时的分析状态键。
ANALYSIS_STATUS_PENDING = "pending"
# 片段分析结果仍与当前内容一致时的状态键。
ANALYSIS_STATUS_CURRENT = "current"
# 片段编辑后需要重新分析时的状态键。
ANALYSIS_STATUS_STALE = "stale"
# 片段分析过程失败时的状态键。
ANALYSIS_STATUS_FAILED = "failed"

# 由本地专用模型生成的客观事实证据来源键。
EVIDENCE_SOURCE_SPECIALIZED_MODEL = "specialized_model"
# 由音频特征分析生成的证据来源键。
EVIDENCE_SOURCE_AUDIO_ANALYSIS = "audio_analysis"
# 由画面文字识别生成的证据来源键。
EVIDENCE_SOURCE_OCR = "ocr"
# 由云端 LLM 生成的语义解释证据来源键。
EVIDENCE_SOURCE_LLM = "llm"
# 由人工审核产生的补充证据来源键。
EVIDENCE_SOURCE_HUMAN_REVIEW = "human_review"

# 证据已成功生成并可被审核使用时的可用性状态键。
EVIDENCE_AVAILABILITY_AVAILABLE = "available"
# 因输入条件不满足而无法生成证据时的状态键。
EVIDENCE_AVAILABILITY_UNAVAILABLE = "unavailable"
# 因工具或模型出错而未生成证据时的状态键。
EVIDENCE_AVAILABILITY_FAILED = "failed"

# 人工修改片段文本时的审核操作类型。
REVIEW_OPERATION_TEXT_EDIT = "text_edit"
# 人工修改片段说话人时的审核操作类型。
REVIEW_OPERATION_SPEAKER_EDIT = "speaker_edit"
# 人工将一个片段拆分为多个片段时的审核操作类型。
REVIEW_OPERATION_SPLIT = "split"
# 人工合并相邻片段时的审核操作类型。
REVIEW_OPERATION_MERGE = "merge"
# 人工删除无效片段时的审核操作类型。
REVIEW_OPERATION_DELETE = "delete"
# 人工确认片段最终内容时的审核操作类型。
REVIEW_OPERATION_CONFIRM = "confirm"

# 面向机器消费的结构化导出格式键。
EXPORT_FORMAT_JSON = "json"
# 面向人工阅读的时间轴报告导出格式键。
EXPORT_FORMAT_MARKDOWN = "markdown"

# SQLite 任务库文件名，默认放在产物根目录下便于本地恢复。
JOB_SQLITE_FILENAME = "jobs.sqlite"
# SQLite 连接 URL 前缀，使用本地文件路径。
SQLITE_URL_PREFIX = "sqlite:///"
# 任务产物根目录下用于隔离每个 Job 的子目录名前缀。
JOB_ARTIFACT_DIR_PREFIX = "jobs"
# 质量报告等相对产物路径示例中的目录名（仅作路径片段语义说明，不硬编码业务内容）。
QUALITY_REPORT_RELATIVE_DIR = "quality"
# 应用重启时将中断任务标记为失败的错误码。
JOB_ERROR_CODE_INTERRUPTED = "JOB_INTERRUPTED"
# 应用重启恢复时标记的失败阶段名。
JOB_FAILED_STAGE_INTERRUPTED = "runtime"
# 默认失败可重试标记：业务失败默认不可自动重试，中断恢复可重试。
DEFAULT_FAILURE_RETRYABLE = False
# 中断恢复后的任务可重试，便于重新进入处理管线。
INTERRUPTED_FAILURE_RETRYABLE = True

# 本地数据根目录默认名，相对进程工作目录存放 SQLite 与产物。
DEFAULT_DATA_ROOT_DIRNAME = "data"
# 任务输入媒体在产物目录中的相对子目录名。
SOURCE_MEDIA_RELATIVE_DIR = "input"
# 导出文件在产物目录中的相对子目录名。
EXPORT_RELATIVE_DIR = "exports"
# Markdown 导出文件名。
EXPORT_MARKDOWN_FILENAME = "transcript.md"
# JSON 导出文件名。
EXPORT_JSON_FILENAME = "transcript.json"
# 上传接口使用的 multipart 表单字段名。
UPLOAD_FILE_FORM_FIELD = "file"
# 任务集合 API 路径前缀。
API_JOBS_PATH = "/api/jobs"
# 片段集合 API 路径前缀。
API_SEGMENTS_PATH = "/api/segments"
# 确认片段的路径后缀。
API_SEGMENT_CONFIRM_SUFFIX = "confirm"
# 导出集合相对任务的路径后缀。
API_JOB_EXPORTS_SUFFIX = "exports"
# 片段列表相对任务的路径后缀。
API_JOB_SEGMENTS_SUFFIX = "segments"
# HTTP 创建成功状态码（上传、导出）。
HTTP_STATUS_CREATED = 201
# HTTP 成功状态码（查询）。
HTTP_STATUS_OK = 200
# HTTP 资源不存在状态码。
HTTP_STATUS_NOT_FOUND = 404
# HTTP 请求不合法状态码。
HTTP_STATUS_BAD_REQUEST = 400
# 导出前任务尚无片段时的错误码。
EXPORT_ERROR_NO_SEGMENTS = "NO_SEGMENTS"
# 上传空文件时的错误码。
UPLOAD_ERROR_EMPTY_FILE = "EMPTY_FILE"
# 上传缺少文件名时的默认媒体文件名。
DEFAULT_UPLOAD_FILENAME = "upload.bin"



# Provider 设置 API 路径。
API_SETTINGS_PROVIDER_PATH = "/api/settings/provider"
# 默认 Provider Base URL 占位，避免空值。
DEFAULT_PROVIDER_BASE_URL = ""
# 默认模型名占位。
DEFAULT_PROVIDER_MODEL_NAME = ""


# 原始抽取音轨文件名，永不覆盖。
AUDIO_RAW_FILENAME = "audio_raw.wav"
# 轻度处理后的音轨文件名。
AUDIO_LIGHT_FILENAME = "audio_light.wav"
# STT 就绪音轨文件名。
AUDIO_STT_READY_FILENAME = "audio_stt_ready.wav"
# 媒体产物子目录。
MEDIA_ARTIFACT_DIR = "media"
# 干净音频仅做响度标准化的处理原因。
PREPROCESS_REASON_CLEAN_NORMALIZE = "CLEAN_AUDIO_NORMALIZE_ONLY"
# BGM 重时启用分离的原因。
PREPROCESS_REASON_STRONG_BGM = "STRONG_BGM_SEPARATE_VOCALS"
# 无脸帧跳过人脸工具的原因。
TOOL_SKIP_REASON_NO_FACE_FRAME = "NO_FACE_FRAME"
# 默认云端融合失败可重试次数。
DEFAULT_FUSION_MAX_RETRIES = 2
# 局部重分析队列默认状态。
REANALYSIS_STATUS_QUEUED = "queued"
REANALYSIS_STATUS_DONE = "done"
