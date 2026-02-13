# l4_core/ai/router.py

from typing import Optional, List, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import AIEngine
from ..utils.logging import log_engine_event, generate_trace_id

# Provider dispatch imports
from .providers import (
    call_openai,
    call_deepseek,
    call_anthropic,
    call_gemini,
    call_internal_model,
)


class AIRequest:
    """Generic AI request object for text (and future multimodal)."""

    def __init__(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.prompt = prompt
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.metadata = metadata or {}


class AIResponse:
    """Generic AI response wrapper."""

    def __init__(
        self,
        content: str,
        provider: str,
        model: str,
        trace_id: str,
        raw: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.provider = provider
        self.model = model
        self.trace_id = trace_id
        self.raw = raw or {}


class AIRouter:
    """
    Central AI router.
    - Chooses engine based on DB config (AIEngine)
    - Respects enabled/priority/fallback
    - Dispatches to OpenAI, DeepSeek, Claude, Gemini, or your own models.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_available_engines(self) -> List[AIEngine]:
        stmt = (
            select(AIEngine)
            .where(AIEngine.enabled == True)  # noqa: E712
            .order_by(AIEngine.priority.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _choose_engine(self) -> Optional[AIEngine]:
        engines = await self._get_available_engines()
        return engines[0] if engines else None

    async def generate_text(self, request: AIRequest) -> AIResponse:
        """
        Main text generation entrypoint.
        - Picks engine
        - Calls provider-specific implementation
        - Logs events with trace_id
        """
        trace_id = generate_trace_id()
        engine = await self._choose_engine()

        if not engine:
            log_engine_event(
                engine="none",
                message="No AI engines available",
                trace_id=trace_id,
                extra={"request_meta": request.metadata},
            )
            raise RuntimeError("No AI engines are enabled in the system.")

        engine_key = f"{engine.provider}:{engine.model}"

        log_engine_event(
            engine=engine_key,
            message="AI text generation started",
            trace_id=trace_id,
            extra={"request_meta": request.metadata},
        )

        # Provider dispatch
        if engine.provider == "openai":
            content, raw = await call_openai(request, engine.model)
        elif engine.provider == "deepseek":
            content, raw = await call_deepseek(request, engine.model)
        elif engine.provider == "anthropic":
            content, raw = await call_anthropic(request, engine.model)
        elif engine.provider == "gemini":
            content, raw = await call_gemini(request, engine.model)
        elif engine.provider == "internal":
            content, raw = await call_internal_model(request, engine.model)
        else:
            raise RuntimeError(f"Unknown AI provider: {engine.provider}")

        log_engine_event(
            engine=engine_key,
            message="AI text generation completed",
            trace_id=trace_id,
            extra={"response_preview": content[:120]},
        )

        return AIResponse(
            content=content,
            provider=engine.provider,
            model=engine.model,
            trace_id=trace_id,
            raw=raw,
        )

    async def generate_image(self, request: AIRequest) -> AIResponse:
        """
        Placeholder for image generation.
        Will route to internal-only engines for AAA asset pipelines.
        """
        trace_id = generate_trace_id()
        log_engine_event(
            engine="image-router",
            message="Image generation requested (not yet implemented)",
            trace_id=trace_id,
            extra={"request_meta": request.metadata},
        )
        raise NotImplementedError("Image generation not implemented yet.")

    async def generate_audio(self, request: AIRequest) -> AIResponse:
        """
        Placeholder for voice line generation for AAA titles.
        """
        trace_id = generate_trace_id()
        log_engine_event(
            engine="audio-router",
            message="Audio generation requested (not yet implemented)",
            trace_id=trace_id,
            extra={"request_meta": request.metadata},
        )
        raise NotImplementedError("Audio generation not implemented yet.")

    async def generate_video(self, request: AIRequest) -> AIResponse:
        """
        Placeholder for video/cinematic generation orchestration.
        """
        trace_id = generate_trace_id()
        log_engine_event(
            engine="video-router",
            message="Video generation requested (not yet implemented)",
            trace_id=trace_id,
            extra={"request_meta": request.metadata},
        )
        raise NotImplementedError("Video generation not implemented yet.")
