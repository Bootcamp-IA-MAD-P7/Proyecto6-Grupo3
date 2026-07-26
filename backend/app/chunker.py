"""Split raw policy text into fragments, by paragraph (MVP rule).

Reusable across the stub and the future real model: this is the single place
that turns raw text into (text, start, end), where start/end are real
character positions in the ORIGINAL text (see specs/5_backend_contract.md,
TROCEADOR DE FRAGMENTOS).
"""

import re
from dataclasses import dataclass

_PARAGRAPH_BREAK = re.compile(r"\n\s*\n+")


@dataclass
class ParagraphFragment:
    text: str
    start: int
    end: int


def split_into_fragments(text: str) -> list[ParagraphFragment]:
    fragments: list[ParagraphFragment] = []
    cursor = 0
    for match in _PARAGRAPH_BREAK.finditer(text):
        _append_fragment(fragments, text, cursor, match.start())
        cursor = match.end()
    _append_fragment(fragments, text, cursor, len(text))
    return fragments


def _append_fragment(
    fragments: list[ParagraphFragment], text: str, raw_start: int, raw_end: int
) -> None:
    raw_chunk = text[raw_start:raw_end]
    left_stripped = raw_chunk.lstrip()
    left_trim = len(raw_chunk) - len(left_stripped)
    stripped = left_stripped.rstrip()
    if not stripped:
        return
    start = raw_start + left_trim
    end = start + len(stripped)
    fragments.append(ParagraphFragment(text=stripped, start=start, end=end))
