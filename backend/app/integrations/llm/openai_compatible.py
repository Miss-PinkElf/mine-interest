"""OpenAI-compatible Provider 适配器。"""

from __future__ import annotations

from app.integrations.llm.base import FusionRequest, FusionResponse, LlmProvider


# 融合提示词真相源：要求输出结论、证据引用、不确定性、冲突与人工审核标记。
FUSION_SYSTEM_PROMPT = (
    "你是证据融合助手。只能基于给定证据解释语义，"
    "输出结论、置信度、不确定性、evidence_ids、冲突说明和 requires_human_review。"
    "不得编造未提供的媒体内容。"
)


class OpenAICompatibleProvider:
    """可注入 HTTP 客户端的 Provider；默认提供可测试的本地回退。"""

    def __init__(
        self,
        *,
        base_url: str,
        model_name: str,
        api_key: str,
        http_post=None,
    ) -> None:
        self.base_url = base_url
        self.model_name = model_name
        self.api_key = api_key
        self._http_post = http_post

    def fuse(self, request: FusionRequest) -> FusionResponse:
        """调用云端或本地回退生成结构化解释。"""
        if self._http_post is not None:
            payload = self._http_post(request)
            return FusionResponse(**payload)

        evidence_ids = [str(item.get("id", "")) for item in request.evidence_summaries]
        conflicts: list[str] = []
        requires_review = False
        # 简单冲突检测：专用模型与文本暗示不一致时进入人工审核。
        for item in request.evidence_summaries:
            if item.get("kind") == "audio_emotion" and "反讽" in request.text:
                conflicts.append("专用情感与文本暗示可能冲突")
                requires_review = True
        return FusionResponse(
            conclusion="基于证据的初步语义解释",
            confidence=0.55 if requires_review else 0.75,
            uncertainty="中等" if requires_review else "较低",
            evidence_ids=[item for item in evidence_ids if item],
            conflicts=conflicts,
            requires_human_review=requires_review,
        )
