from functools import lru_cache


def is_mock_mode() -> bool:
    return True


@lru_cache(maxsize=1)
def get_client():
    return None


def build_cached_system(static_text: str, dynamic_text: str = "") -> list[dict]:
    blocks = [{"type": "text", "text": static_text}]
    if dynamic_text:
        blocks.append({"type": "text", "text": dynamic_text})
    return blocks
