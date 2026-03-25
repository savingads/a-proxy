import json
import logging
from typing import Any, Dict, List, Optional

from config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    LLM_MAX_OUTPUT_TOKENS,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_COMPATIBLE_URL,
    OPENAI_COMPATIBLE_MODEL,
    OPENAI_COMPATIBLE_API_KEY,
)


logger = logging.getLogger(__name__)


class ProviderNotConfiguredError(RuntimeError):
    """Raised when a requested LLM provider is not configured."""


class BaseAdapter:
    provider_name: str = "base"
    default_model: str = ""

    def __init__(self, max_output_tokens: int):
        self.max_output_tokens = max_output_tokens

    def chat(self, messages: List[Dict[str, str]], model_hint: Optional[str] = None) -> str:
        raise NotImplementedError

    def generate_structured(
        self, prompt: str, schema: Dict[str, Any], model_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def _validate_tokens(self, requested_tokens: Optional[int]) -> int:
        if requested_tokens is None:
            return self.max_output_tokens
        if requested_tokens <= 0:
            raise ValueError("Requested tokens must be positive")
        if requested_tokens > self.max_output_tokens:
            raise ValueError(
                f"Requested tokens {requested_tokens} exceed limit {self.max_output_tokens}"
            )
        return requested_tokens


class OpenAICompatibleAdapter(BaseAdapter):
    """Adapter for OpenAI-compatible APIs (vLLM, Ollama, text-generation-webui, LiteLLM, etc.)."""

    provider_name = "openai_compatible"
    default_model = OPENAI_COMPATIBLE_MODEL

    def __init__(self, max_output_tokens: int):
        super().__init__(max_output_tokens)
        if not OPENAI_COMPATIBLE_URL:
            raise ProviderNotConfiguredError("OPENAI_COMPATIBLE_URL is not set")
        from openai import OpenAI

        logger.info("Initializing OpenAI-compatible client at %s", OPENAI_COMPATIBLE_URL)
        self.client = OpenAI(
            base_url=OPENAI_COMPATIBLE_URL,
            api_key=OPENAI_COMPATIBLE_API_KEY,
        )

    def chat(self, messages: List[Dict[str, str]], model_hint: Optional[str] = None) -> str:
        model = model_hint or self.default_model
        logger.debug(
            "Sending chat to OpenAI-compatible endpoint",
            extra={"model": model, "message_count": len(messages)},
        )
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=self._validate_tokens(None),
        )
        return completion.choices[0].message.content or ""

    def generate_structured(
        self, prompt: str, schema: Dict[str, Any], model_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        model = model_hint or self.default_model
        augmented_prompt = (
            f"{prompt}\n\nRespond ONLY with valid JSON that matches this schema: {json.dumps(schema)}"
        )
        logger.debug("Generating structured response via OpenAI-compatible endpoint", extra={"model": model})
        completion = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": augmented_prompt}],
            max_tokens=self._validate_tokens(None),
        )
        content = completion.choices[0].message.content or "{}"
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse JSON from OpenAI-compatible response", exc_info=True)
            raise ValueError("Structured response could not be parsed as JSON") from exc


class AnthropicAdapter(BaseAdapter):
    provider_name = "anthropic"
    default_model = ANTHROPIC_MODEL

    def __init__(self, max_output_tokens: int):
        super().__init__(max_output_tokens)
        if not ANTHROPIC_API_KEY:
            raise ProviderNotConfiguredError("ANTHROPIC_API_KEY is not set")
        import anthropic

        logger.info("Initializing Anthropic client")
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def chat(self, messages: List[Dict[str, str]], model_hint: Optional[str] = None) -> str:
        model = model_hint or self.default_model
        system_messages = [m["content"] for m in messages if m.get("role") == "system"]
        system_prompt = "\n".join(system_messages) if system_messages else None
        convo = [m for m in messages if m.get("role") != "system"]

        logger.debug(
            "Sending chat to Anthropic", extra={"model": model, "message_count": len(convo)}
        )

        response = self.client.messages.create(
            model=model,
            system=system_prompt,
            messages=[
                {
                    "role": m.get("role", "user"),
                    "content": m.get("content", ""),
                }
                for m in convo
            ],
            max_tokens=self._validate_tokens(None),
        )

        return response.content[0].text

    def generate_structured(
        self, prompt: str, schema: Dict[str, Any], model_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        model = model_hint or self.default_model
        augmented_prompt = (
            f"{prompt}\n\nRespond ONLY with valid JSON that matches this schema: {json.dumps(schema)}"
        )
        logger.debug("Generating structured response with Anthropic", extra={"model": model})

        response = self.client.messages.create(
            model=model,
            messages=[{"role": "user", "content": augmented_prompt}],
            max_tokens=self._validate_tokens(None),
        )
        return self._parse_json_response(response.content[0].text)

    @staticmethod
    def _parse_json_response(text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse JSON from Anthropic response", exc_info=True)
            raise ValueError("Structured response could not be parsed as JSON") from exc


class OpenAIAdapter(BaseAdapter):
    provider_name = "openai"
    default_model = OPENAI_MODEL

    def __init__(self, max_output_tokens: int):
        super().__init__(max_output_tokens)
        if not OPENAI_API_KEY:
            raise ProviderNotConfiguredError("OPENAI_API_KEY is not set")
        from openai import OpenAI

        logger.info("Initializing OpenAI client")
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def chat(self, messages: List[Dict[str, str]], model_hint: Optional[str] = None) -> str:
        model = model_hint or self.default_model
        logger.debug(
            "Sending chat to OpenAI", extra={"model": model, "message_count": len(messages)}
        )
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=self._validate_tokens(None),
        )
        return completion.choices[0].message.content or ""

    def generate_structured(
        self, prompt: str, schema: Dict[str, Any], model_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        model = model_hint or self.default_model
        logger.debug("Generating structured response with OpenAI", extra={"model": model})
        completion = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "response", "schema": schema, "strict": True},
            },
            max_tokens=self._validate_tokens(None),
        )
        content = completion.choices[0].message.content or "{}"
        return json.loads(content)


class LLMClient:
    """Provider-aware client for chat and structured generation."""

    def __init__(self, provider: Optional[str] = None, max_output_tokens: Optional[int] = None):
        self.provider_name = (provider or LLM_PROVIDER or "").lower()
        self.max_output_tokens = max_output_tokens or LLM_MAX_OUTPUT_TOKENS
        self.adapter = self._initialize_adapter()
        logger.info(
            "Initialized LLMClient",
            extra={
                "provider": self.adapter.provider_name,
                "model": self.adapter.default_model,
                "max_output_tokens": self.max_output_tokens,
            },
        )

    def chat(self, messages: List[Dict[str, str]], model_hint: Optional[str] = None) -> str:
        try:
            return self.adapter.chat(messages, model_hint)
        except Exception as exc:
            logger.error("LLM chat request failed", exc_info=True)
            raise RuntimeError("Chat completion failed") from exc

    def generate_structured(
        self, prompt: str, schema: Dict[str, Any], model_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            return self.adapter.generate_structured(prompt, schema, model_hint)
        except Exception as exc:
            logger.error("Structured generation failed", exc_info=True)
            raise RuntimeError("Structured generation failed") from exc

    def _initialize_adapter(self) -> BaseAdapter:
        provider = self.provider_name or self._auto_detect_provider()
        if provider == "openai_compatible":
            return OpenAICompatibleAdapter(self.max_output_tokens)
        if provider == "anthropic":
            return AnthropicAdapter(self.max_output_tokens)
        if provider == "openai":
            return OpenAIAdapter(self.max_output_tokens)
        raise ProviderNotConfiguredError(f"Unknown LLM provider: {provider!r}")

    def _auto_detect_provider(self) -> str:
        if OPENAI_COMPATIBLE_URL:
            return "openai_compatible"
        if ANTHROPIC_API_KEY:
            return "anthropic"
        if OPENAI_API_KEY:
            return "openai"
        raise ProviderNotConfiguredError("No LLM provider is configured")
