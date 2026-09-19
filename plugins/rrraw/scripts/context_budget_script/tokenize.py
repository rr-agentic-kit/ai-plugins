"""tiktoken counting — budget unit via cl100k_base (not model-exact)."""

from __future__ import annotations

from functools import lru_cache

from . import ENCODING_NAME


@lru_cache(maxsize=1)
def _encoding():  # type: ignore[no-untyped-def]
    import tiktoken

    return tiktoken.get_encoding(ENCODING_NAME)


def count_tokens(text: str) -> int:
    return len(_encoding().encode(text))
