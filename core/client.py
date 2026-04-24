import anthropic
from functools import lru_cache


@lru_cache(maxsize=1)
def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def build_cached_system(static_text: str, dynamic_text: str = "") -> list[dict]:
    """
    Returns system prompt with cache_control on the static prefix.
    Dynamic content (live state, timestamps) goes after — never cached.
    """
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
