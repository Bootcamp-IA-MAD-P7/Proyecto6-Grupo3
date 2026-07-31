"""Translation layer: Spanish -> English before classification.

WHY IT EXISTS
The model is trained on OPP-115, which is English only, over a frozen English
TF-IDF vocabulary. A Spanish policy therefore has almost no words the model
knows: measured on Spotify's Spanish policy, scores collapsed to ~0.10-0.29 (the
value the model returns when nothing matches its vocabulary) and headings like
"6. Retencion de datos" were classified as third_party. The same policy in
English scored up to 0.93 and classified correctly. So translation is not a
nicety: without it, Spanish output is noise.

ENGINE: Google Cloud Translation API (v2, REST over httpx)
Previously a local Opus-MT model (transformers + torch). That pipeline needed
~300MB just to load into memory on first use, which reliably OOM-crashed the
Render free-tier instance (512MB total) on the first Spanish request — the
whole API went unresponsive, not just translation. A REST call has no local
memory footprint and no multi-hundred-MB dependency to install. The trade-off,
accepted deliberately: text is sent to Google instead of staying on-box.

Auth: GOOGLE_TRANSLATE_API_KEY (backend/.env locally, an env var on Render).
Not set -> translation degrades to unavailable, same as any other failure
(see GRACEFUL DEGRADATION below); the API keeps working in English-only mode.

WHAT IS TRANSLATED AND WHAT IS RETURNED
Translation is INTERNAL AND DISPOSABLE. It is fed to the classifier; the user
always gets their ORIGINAL text back, with the original character offsets. That is
why translation happens FRAGMENT BY FRAGMENT after chunking, never on the whole
document: translating the whole thing would shift every offset and break the
`start`/`end` contract the browser extension needs for highlighting.

GRACEFUL DEGRADATION (floor requirement)
Any failure — missing API key, network error, API error, malformed response —
sets available=False (or leaves affected fragments untranslated) and the
pipeline continues in the original language. It NEVER raises. A user who gets
a warning plus a worse result is better served than one who gets a 500.

CACHE
Keyed by text hash, in memory. A demo that analyses the same policy twice
translates only once, and identical boilerplate paragraphs across a document
are only sent to the API once each.
"""

import hashlib
from dataclasses import dataclass
from functools import lru_cache

import httpx

from .config import load_settings

TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"
TIMEOUT_SECONDS = 10.0

# Google's v2 API accepts up to 128 `q` values per request; batching keeps
# every request comfortably under that regardless of how long the policy is.
BATCH_SIZE = 100

_SPANISH_CHARS = set("áéíóúñ¿¡")
_SPANISH_STOPWORDS = {
    "de", "la", "el", "que", "y", "los", "las", "para",
    "con", "su", "sus", "una", "uno", "por", "se", "del",
}

# text hash -> translation. Module level, so it survives across requests.
_CACHE: dict[str, str] = {}


def detect_language(text: str) -> str:
    """Trivial heuristic (Spanish diacritics/punctuation or common stopwords).

    Good enough to decide whether to translate; not a real language detector.
    A false negative costs accuracy, a false positive costs an API call —
    neither breaks anything, which is why a heuristic is acceptable here.
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


@dataclass
class FragmentTranslation:
    """Per-fragment result. `texts` feeds the classifier; the ORIGINAL fragments
    are what the response returns, so offsets stay valid."""

    texts: list[str]
    translated: bool
    available: bool
    note: str = ""


@lru_cache(maxsize=1)
def _api_key() -> str | None:
    # Routed through config.py, not os.environ directly, because a local
    # backend/.env is parsed by pydantic-settings for its own Settings
    # fields and never copied into the real process environment.
    return load_settings().google_translate_api_key


def translate_fragments(fragment_texts: list[str], source_lang: str) -> FragmentTranslation:
    """Translate a list of fragments es->en, preserving order and count.

    Order and count are part of the contract: analyze.py zips these texts against
    the ORIGINAL fragments to build the response, so index i must still be
    fragment i. Anything that cannot be translated comes back unchanged.
    """
    if source_lang != "es" or not fragment_texts:
        return FragmentTranslation(texts=fragment_texts, translated=False, available=True)

    api_key = _api_key()
    if not api_key:
        return FragmentTranslation(
            texts=fragment_texts,
            translated=False,
            available=False,
            note="GOOGLE_TRANSLATE_API_KEY is not configured; classified in the original language.",
        )

    out: list[str] = list(fragment_texts)
    pending: list[str] = []
    pending_index: list[int] = []
    from_cache = 0

    for i, text in enumerate(fragment_texts):
        if not text.strip():
            continue
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if key in _CACHE:
            out[i] = _CACHE[key]
            from_cache += 1
        else:
            pending.append(text)
            pending_index.append(i)

    translated_now = 0
    note = ""

    if pending:
        try:
            with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
                for start in range(0, len(pending), BATCH_SIZE):
                    batch = pending[start : start + BATCH_SIZE]
                    batch_index = pending_index[start : start + BATCH_SIZE]

                    response = client.post(
                        TRANSLATE_URL,
                        params={"key": api_key},
                        json={"q": batch, "source": "es", "target": "en", "format": "text"},
                    )
                    response.raise_for_status()
                    translations = response.json()["data"]["translations"]

                    for i, original, item in zip(batch_index, batch, translations):
                        translated_text = item["translatedText"]
                        out[i] = translated_text
                        _CACHE[hashlib.sha256(original.encode("utf-8")).hexdigest()] = translated_text
                        translated_now += 1
        except Exception as exc:  # noqa: BLE001 - degrade, never raise; batches already
            # translated before the failure are kept, the rest stay in the original language.
            print(f"[translation] Google Translate call failed, continuing untranslated: {exc}")
            note = (
                "Translation was interrupted by a service error; some fragments are "
                "classified in the original language."
            )

    return FragmentTranslation(
        texts=out,
        translated=translated_now > 0 or from_cache > 0,
        available=True,
        note=note,
    )


def translate(text: str, source_lang: str) -> TranslationResult:
    """Kept for compatibility: the whole-document entry point is no longer used.

    analyze.py now calls translate_fragments AFTER chunking, so that `start`/`end`
    keep pointing at the original document (2_spec.md section 5, rule 1).
    """
    return TranslationResult(text=text, translated=False, available=True)
