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

    def ask(self, prompt: str, system: str = "You are a precise analytical system. Always respond in valid JSON.", model_override: str | None = None) -> str:
        response = self.client.chat.completions.create(
            model=model_override or self.model,
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
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
        if match:
            raw = match.group(1).strip()
        return json.loads(raw)

    def ask_code(self, prompt: str, model_override: str | None = None) -> str:
        """Generate code — uses model_override for stronger models on evolution."""
        raw = self.ask(
            prompt,
            system="You are an expert Python 3.11+ developer. Return a COMPLETE, valid Python file inside ```python``` code fences. Include ALL imports, ALL functions, ALL code. No placeholders, no ellipsis, no truncation. The file must be syntactically valid.",
            model_override=model_override,
        )
        match = re.search(r"```(?:python)?\s*([\s\S]*?)```", raw)
        if match:
            code = match.group(1).strip()
            try:
                compile(code, "<evolution>", "exec")
                return code
            except SyntaxError:
                pass
        try:
            compile(raw.strip(), "<evolution>", "exec")
            return raw.strip()
        except SyntaxError:
            return ""

    def get_usage(self) -> dict:
        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens_used,
            "estimated_cost_usd": self.total_tokens_used * 0.00000015,
        }


def create_provider(provider_string: str) -> LLMProvider:
    """
    Parse provider string like:
      "openai:gpt-4o-mini"
      "ollama:llama3"
      "http://localhost:11434/v1:llama3"
    """
    if "://" in provider_string:
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
        return LLMProvider(model=model or "llama3", base_url="http://localhost:11434/v1", api_key="ollama")
    elif provider_name == "groq":
        return LLMProvider(model=model or "llama-3.1-70b-versatile", base_url="https://api.groq.com/openai/v1")
    elif provider_name == "together":
        return LLMProvider(model=model or "meta-llama/Llama-3-70b-chat-hf", base_url="https://api.together.xyz/v1")
    else:
        return LLMProvider(model=provider_string)
