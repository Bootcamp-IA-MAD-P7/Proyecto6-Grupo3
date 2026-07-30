"""Orchestrates one /api/analyze call: chunk -> translate -> predict -> contract.

This is the seam described in specs/5_backend_contract.md: the stub has been
replaced by the real multiclass model in `predictor.predict_proba`. The response
contract (§9) did not change — see `_build_fragment` for how a single-class
prediction is expressed in the multi-label shape the frontend already consumes.
"""

import numpy as np

from . import exposure, gdpr, predictor, translation
from .categories import CATEGORIES
from .chunker import split_into_fragments
from .schemas import AnalyzeResponse, Category, Document, Fragment, Label

MODEL_VERSION = "1.0.0"


def analyze_text(text: str) -> AnalyzeResponse:
    source_language = translation.detect_language(text)
    translation_result = translation.translate(text, source_language)

    raw_fragments = split_into_fragments(text)
    fragment_texts = [fragment.text for fragment in raw_fragments]
    probabilities = predictor.predict_proba(fragment_texts, translation_result.text)

    fragments = [
        _build_fragment(index, raw_fragments[index], probabilities[index])
        for index in range(len(raw_fragments))
    ]
    categories = [
        _build_category(category_index, category_id, probabilities)
        for category_index, category_id in enumerate(CATEGORIES)
    ]

    document = Document(
        source_language=source_language,
        translated=translation_result.translated,
        translation_available=translation_result.available,
        exposure=exposure.compute_exposure(categories),
        categories=categories,
        fragment_count=len(fragments),
    )
    return AnalyzeResponse(
        model_version=MODEL_VERSION, stub=False, document=document, fragments=fragments
    )


def _build_fragment(index: int, raw_fragment, scores: np.ndarray) -> Fragment:
    """Build one fragment of the §9 contract from its class probabilities.

    Multiclass: exactly one class wins (argmax), there is no threshold — the ten
    classes compete and the highest takes it, be it 0.9 or 0.4. The LIST shape of
    `labels` is kept so the frontend contract does not change; it simply always
    carries a single item. Note that every fragment now gets a label: the `Other`
    class absorbs paragraphs that describe no data practice.
    """
    winner = int(np.argmax(scores))
    labels = [Label(id=CATEGORIES[winner], score=round(float(scores[winner]), 4))]
    return Fragment(
        id=index,
        text=raw_fragment.text,
        start=raw_fragment.start,
        end=raw_fragment.end,
        labels=labels,
    )


def _build_category(
    category_index: int, category_id: str, probabilities: np.ndarray
) -> Category:
    """Build one document-level category entry: how many fragments this class won.

    `fragment_count` is the count of fragments whose winning class is this one, so
    dividing it by document.fragment_count gives the share of the policy devoted to
    this practice. That share is what the exposure layer will consume.
    `confidence` is the mean probability across the fragments this class won.
    """
    if probabilities.size:
        winners = probabilities.argmax(axis=1)
        mask = winners == category_index
        fragment_count = int(mask.sum())
        confidence = (
            float(probabilities[mask, category_index].mean()) if fragment_count else 0.0
        )
    else:
        fragment_count, confidence = 0, 0.0

    return Category(
        id=category_id,
        present=fragment_count > 0,
        confidence=round(confidence, 4),
        fragment_count=fragment_count,
        gdpr_reference=gdpr.gdpr_reference_for(category_id),
    )