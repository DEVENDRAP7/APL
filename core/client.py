import os
import anthropic
from functools import lru_cache

_MOCK_KEYS = {"", "mock", "dummy", "placeholder"}


def is_mock_mode() -> bool:
    return os.getenv("ANTHROPIC_API_KEY", "").lower() in _MOCK_KEYS


@lru_cache(maxsize=1)
def get_client() -> anthropic.Anthropic:
    if is_mock_mode():
        return anthropic.Anthropic(api_key="mock-key-not-used")
    return anthropic.Anthropic()


def build_cached_system(static_text: str, dynamic_text: str = "") -> list[dict]:
    blocks = [
        {
            "type": "text",
            "text": static_text,
            "cache_control": {"type": "ephemeral"},
        }
    ]
    if dynamic_text:
        blocks.append({"type": "text", "text": dynamic_text})
    return blocks
