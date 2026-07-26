"""Translation layer: interface wired, engine not implemented yet.

See specs/5_backend_contract.md, TRADUCCION. `translate()` is a no-op stub —
it returns the input unchanged. The real engine (Opus-MT es->en,
Helsinki-NLP/opus-mt-es-en) replaces its body later without changing this
signature, the caller, or the response contract. Because a no-op cannot fail,
`available` is always True here; a real engine would set it to False on
failure instead of raising (graceful degradation, per 2_spec.md §11.1).
"""

from dataclasses import dataclass

_SPANISH_CHARS = set("áéíóúñ¿¡")
_SPANISH_STOPWORDS = {
    "de", "la", "el", "que", "y", "los", "las", "para",
    "con", "su", "sus", "una", "uno", "por", "se", "del",
}


def detect_language(text: str) -> str:
    """Trivial heuristic (Spanish diacritics/punctuation or common stopwords).

    Good enough to route the stub; not a real language detector.
    """
    lowered = text.lower()
    if any(char in lowered for char in _SPANISH_CHARS):
        return "es"
    words = set(lowered.split())
    if len(words & _SPANISH_STOPWORDS) >= 3:
        return "es"
    return "en"


@dataclass
class TranslationResult:
    text: str
    translated: bool
    available: bool


def translate(text: str, source_lang: str) -> TranslationResult:
    """No-op stub. Always returns the original text with translated=False."""
    return TranslationResult(text=text, translated=False, available=True)
