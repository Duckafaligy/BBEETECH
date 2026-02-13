# l4_core/ai/providers/openai_provider.py

from typing import Tuple, Dict, Any
from ..router import AIRequest
from ...config import settings


async def call_openai(request: AIRequest, model: str) -> Tuple[str, Dict[str, Any]]:
    # TODO: wire real OpenAI client here
    content = f"[openai:{model}] {request.prompt}"
    raw = {"provider": "openai", "model": model, "placeholder": True}
    return content, raw
