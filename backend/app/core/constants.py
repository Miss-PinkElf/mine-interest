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
