"""Translation layer: Spanish -> English before classification.

WHY IT EXISTS
The model is trained on OPP-115, which is English only, over a frozen English
TF-IDF vocabulary. A Spanish policy therefore has almost no words the model
knows: measured on Spotify's Spanish policy, scores collapsed to ~0.10-0.29 (the
value the model returns when nothing matches its vocabulary) and headings like
"6. Retencion de datos" were classified as third_party. The same policy in
English scored up to 0.93 and classified correctly. So translation is not a
nicety: without it, Spanish output is noise.

ENGINE: Opus-MT local (Helsinki-NLP/opus-mt-es-en, Apache-2.0)
Chosen over NLLB, which is better quality but CC-BY-NC (non-commercial), clashing
with the open-source nature of the project; and over cloud APIs, which need a key
and send the user's policy to a third party. Running locally means the text never
leaves the machine — for a privacy tool that is an argument, not just a detail.

WHAT IS TRANSLATED AND WHAT IS RETURNED
Translation is INTERNAL AND DISPOSABLE. It is fed to the classifier; the user
always gets their ORIGINAL text back, with the original character offsets. That is
why translation happens FRAGMENT BY FRAGMENT after chunking, never on the whole
document: translating the whole thing would shift every offset and break the
`start`/`end` contract the browser extension needs for highlighting.

GRACEFUL DEGRADATION (floor requirement)
Any failure — package missing, no network to download the model, out of memory,
time budget exceeded — sets available=False and the pipeline continues in the
original language. It NEVER raises. A user who gets a warning plus a worse result
is better served than one who gets a 500.

CACHE
Keyed by text hash, in memory. A demo that analyses the same policy twice
translates only once. Warming the cache before a live demo makes it instant.
"""

import hashlib
import time
from dataclasses import dataclass, field

MODEL_NAME = "Helsinki-NLP/opus-mt-es-en"

# Time budget for translating ONE document. Past this, whatever is already
# translated is used and the rest goes through untranslated. This is the guard
# against a live demo hanging: a partial result beats a spinner.
TIME_BUDGET_SECONDS = 0.0

# Fragments translated per forward pass. Bigger is faster but uses more memory;
# 16 runs comfortably on a laptop.
BATCH_SIZE = 16

# Opus-MT truncates beyond its own limit anyway; this keeps memory predictable.
MAX_TOKENS = 512

_SPANISH_CHARS = set("áéíóúñ¿¡")
_SPANISH_STOPWORDS = {
    "de", "la", "el", "que", "y", "los", "las", "para",
    "con", "su", "sus", "una", "uno", "por", "se", "del",
}

# text hash -> translation. Module level, so it survives across requests.
_CACHE: dict[str, str] = {}

# Loaded lazily and kept: (tokenizer, model), or False if loading failed.
_ENGINE = None


def detect_language(text: str) -> str:
    """Trivial heuristic (Spanish diacritics/punctuation or common stopwords).

    Good enough to decide whether to translate; not a real language detector.
    A false negative costs accuracy, a false positive costs time — neither breaks
    anything, which is why a heuristic is acceptable here.
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
    stats: dict = field(default_factory=dict)


def _load_engine():
    """Load tokenizer and model once, on first Spanish request.

    Deliberately NOT at import time: the model is ~300 MB and downloads on first
    use, so loading eagerly would make the API slow to boot even for English-only
    traffic. Returns False on any failure — the caller degrades, does not raise.
    """
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    try:
        from transformers import MarianMTModel, MarianTokenizer

        tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
        model = MarianMTModel.from_pretrained(MODEL_NAME)
        model.eval()  # inference only: no gradients, less memory
        _ENGINE = (tokenizer, model)
    except Exception as exc:  # noqa: BLE001 - any failure must degrade, not raise
        print(f"[translation] engine unavailable, continuing untranslated: {exc}")
        _ENGINE = False

    return _ENGINE


def translate_fragments(fragment_texts: list[str], source_lang: str) -> FragmentTranslation:
    """Translate a list of fragments es->en, preserving order and count.

    Order and count are part of the contract: analyze.py zips these texts against
    the ORIGINAL fragments to build the response, so index i must still be
    fragment i. Anything that cannot be translated comes back unchanged.
    """
    if source_lang != "es" or not fragment_texts:
        return FragmentTranslation(
            texts=fragment_texts, translated=False, available=True
        )

    engine = _load_engine()
    if engine is False:
        return FragmentTranslation(
            texts=fragment_texts,
            translated=False,
            available=False,
            note="Translation engine unavailable; classified in the original language.",
        )

    tokenizer, model = engine
    import torch

    started = time.monotonic()
    out: list[str] = []
    from_cache = 0
    translated_now = 0
    skipped_over_budget = 0

    for start in range(0, len(fragment_texts), BATCH_SIZE):
        batch = fragment_texts[start : start + BATCH_SIZE]

        # Time budget checked per batch, not per fragment: cheap, and granular
        # enough. Everything left goes through untranslated.
        if time.monotonic() - started > TIME_BUDGET_SECONDS:
            out.extend(batch)
            skipped_over_budget += len(batch)
            continue

        pending, pending_index = [], []
        batch_out = [None] * len(batch)

        for i, text in enumerate(batch):
            key = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if key in _CACHE:
                batch_out[i] = _CACHE[key]
                from_cache += 1
            elif not text.strip():
                batch_out[i] = text  # nothing to translate
            else:
                pending.append(text)
                pending_index.append(i)

        if pending:
            try:
                with torch.no_grad():  # inference only
                    encoded = tokenizer(
                        pending,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=MAX_TOKENS,
                    )
                    generated = model.generate(**encoded, max_length=MAX_TOKENS)
                decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)

                for i, text, translation in zip(pending_index, pending, decoded):
                    batch_out[i] = translation
                    _CACHE[hashlib.sha256(text.encode("utf-8")).hexdigest()] = translation
                    translated_now += 1
            except Exception as exc:  # noqa: BLE001 - degrade this batch, keep going
                print(f"[translation] batch failed, keeping original text: {exc}")
                for i, text in zip(pending_index, pending):
                    batch_out[i] = text

        out.extend(batch_out)

    elapsed = time.monotonic() - started
    note = ""
    if skipped_over_budget:
        note = (
            f"{skipped_over_budget} of {len(fragment_texts)} fragments were not "
            f"translated: the {TIME_BUDGET_SECONDS:.0f}s budget was exhausted. Those "
            f"fragments were classified in the original language."
        )

    print(
        f"[translation] {len(fragment_texts)} fragments in {elapsed:.1f}s "
        f"(translated {translated_now}, cached {from_cache}, "
        f"skipped {skipped_over_budget})"
    )

    return FragmentTranslation(
        texts=out,
        translated=translated_now > 0 or from_cache > 0,
        # Partial translation is still a working translation: available stays True
        # and the shortfall is reported in `note`.
        available=True,
        note=note,
        stats={
            "seconds": round(elapsed, 1),
            "translated": translated_now,
            "cached": from_cache,
            "skipped": skipped_over_budget,
        },
    )


def translate(text: str, source_lang: str) -> TranslationResult:
    """Kept for compatibility: the whole-document entry point is no longer used.

    analyze.py now calls translate_fragments AFTER chunking, so that `start`/`end`
    keep pointing at the original document (2_spec.md section 5, rule 1).
    """
    return TranslationResult(text=text, translated=False, available=True)