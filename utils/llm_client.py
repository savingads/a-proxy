import json
import logging
from typing import Any, Dict, List, Optional

import anthropic
import google.generativeai as genai
from openai import OpenAI

from config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    GOOGLE_API_KEY,
    GOOGLE_MODEL,
    LLM_MAX_OUTPUT_TOKENS,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
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


class AnthropicAdapter(BaseAdapter):
    provider_name = "anthropic"
    default_model = ANTHROPIC_MODEL

    def __init__(self, max_output_tokens: int):
        super().__init__(max_output_tokens)
        if not ANTHROPIC_API_KEY:
            raise ProviderNotConfiguredError("ANTHROPIC_API_KEY is not set")
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


class GoogleAdapter(BaseAdapter):
    provider_name = "google"
    default_model = GOOGLE_MODEL

    def __init__(self, max_output_tokens: int):
        super().__init__(max_output_tokens)
        if not GOOGLE_API_KEY:
            raise ProviderNotConfiguredError("GOOGLE_API_KEY is not set")
        logger.info("Initializing Google Generative AI client")
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(self.default_model)

    def chat(self, messages: List[Dict[str, str]], model_hint: Optional[str] = None) -> str:
        model_name = model_hint or self.default_model
        if model_name != self.model.model_name:
            self.model = genai.GenerativeModel(model_name)
        prompt = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
        logger.debug(
            "Sending chat to Google", extra={"model": model_name, "message_count": len(messages)}
        )
        result = self.model.generate_content(
            prompt,
            generation_config={"max_output_tokens": self._validate_tokens(None)},
        )
        return result.text or ""

    def generate_structured(
        self, prompt: str, schema: Dict[str, Any], model_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        model_name = model_hint or self.default_model
        if model_name != self.model.model_name:
            self.model = genai.GenerativeModel(model_name)

        augmented_prompt = (
            f"{prompt}\n\nReturn JSON only that fits this schema: {json.dumps(schema)}"
        )
        logger.debug("Generating structured response with Google", extra={"model": model_name})
        result = self.model.generate_content(
            augmented_prompt,
            generation_config={"max_output_tokens": self._validate_tokens(None)},
        )
        try:
            return json.loads(result.text or "{}")
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse JSON from Google response", exc_info=True)
            raise ValueError("Structured response could not be parsed as JSON") from exc


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
        if provider == "anthropic":
            return AnthropicAdapter(self.max_output_tokens)
        if provider == "openai":
            return OpenAIAdapter(self.max_output_tokens)
        if provider == "google":
            return GoogleAdapter(self.max_output_tokens)
        raise ProviderNotConfiguredError("No supported LLM provider is configured")

    def _auto_detect_provider(self) -> str:
        if ANTHROPIC_API_KEY:
            return "anthropic"
        if OPENAI_API_KEY:
            return "openai"
        if GOOGLE_API_KEY:
            return "google"
        raise ProviderNotConfiguredError("No API key found for any LLM provider")

