"""LLM Provider — works with any OpenAI-compatible API."""

import json
import re
from openai import OpenAI


class LLMProvider:
    def __init__(self, model: str = "gpt-4o-mini", base_url: str | None = None, api_key: str | None = None):
        self.model = model
        kwargs = {}
        if base_url:
            kwargs["base_url"] = base_url
        if api_key:
            kwargs["api_key"] = api_key
        self.client = OpenAI(**kwargs)
        self.total_tokens_used = 0
        self.total_calls = 0

    def ask(self, prompt: str, system: str = "You are a precise analytical system. Always respond in valid JSON.") -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        self.total_calls += 1
        if response.usage:
            self.total_tokens_used += response.usage.total_tokens
        return response.choices[0].message.content or ""

    def ask_json(self, prompt: str) -> dict | list:
        raw = self.ask(prompt)
        # Extract JSON from markdown code blocks if present
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
        if match:
            raw = match.group(1).strip()
        return json.loads(raw)

    def ask_code(self, prompt: str) -> str:
        raw = self.ask(
            prompt,
            system="You are an expert Python developer. Return ONLY the complete Python file content. No explanations.",
        )
        match = re.search(r"```(?:python)?\s*([\s\S]*?)```", raw)
        if match:
            return match.group(1).strip()
        return raw.strip()

    def get_usage(self) -> dict:
        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens_used,
            "estimated_cost_usd": self.total_tokens_used * 0.00000015,  # gpt-4o-mini input rate approx
        }


def create_provider(provider_string: str) -> LLMProvider:
    """
    Parse provider string like:
      "openai:gpt-4o-mini"
      "ollama:llama3"
      "groq:llama-3.1-70b"
      "http://localhost:11434/v1:llama3"
    """
    if "://" in provider_string:
        # Custom URL: "http://localhost:11434/v1:model"
        parts = provider_string.rsplit(":", 1)
        base_url = parts[0]
        model = parts[1] if len(parts) > 1 else "default"
        return LLMProvider(model=model, base_url=base_url, api_key="not-needed")

    parts = provider_string.split(":", 1)
    provider_name = parts[0].lower()
    model = parts[1] if len(parts) > 1 else None

    if provider_name == "openai":
        return LLMProvider(model=model or "gpt-4o-mini")

    elif provider_name == "ollama":
        return LLMProvider(
            model=model or "llama3",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )

    elif provider_name == "groq":
        return LLMProvider(
            model=model or "llama-3.1-70b-versatile",
            base_url="https://api.groq.com/openai/v1",
        )

    elif provider_name == "together":
        return LLMProvider(
            model=model or "meta-llama/Llama-3-70b-chat-hf",
            base_url="https://api.together.xyz/v1",
        )

    elif provider_name == "anthropic":
        # Anthropic doesn't use OpenAI-compatible API, but some proxies do
        return LLMProvider(model=model or "claude-sonnet-4-20250514")

    else:
        # Assume it's a model name for OpenAI
        return LLMProvider(model=provider_string)
