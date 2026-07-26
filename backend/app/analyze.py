"""Orchestrates one /api/analyze call: chunk -> translate -> predict -> contract.

This is the seam described in specs/5_backend_contract.md: swapping the stub
for the real model means changing `stub.predict_proba`, not this function.
"""

import numpy as np

from . import exposure, gdpr, stub, translation
from .categories import CATEGORIES
from .chunker import split_into_fragments
from .schemas import AnalyzeResponse, Category, Document, Fragment, Label

MODEL_VERSION = "0.1.0"

# Stub-only decision: score at/above this counts as "this category applies to
# this fragment". Not part of the frozen contract — the real model may pick
# its own operating point per category.
LABEL_THRESHOLD = 0.5


def analyze_text(text: str) -> AnalyzeResponse:
    source_language = translation.detect_language(text)
    translation_result = translation.translate(text, source_language)

    raw_fragments = split_into_fragments(text)
    fragment_texts = [fragment.text for fragment in raw_fragments]
    probabilities = stub.predict_proba(fragment_texts, translation_result.text)

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
        model_version=MODEL_VERSION, stub=True, document=document, fragments=fragments
    )


def _build_fragment(index: int, raw_fragment, scores: np.ndarray) -> Fragment:
    labels = [
        Label(id=CATEGORIES[i], score=round(float(scores[i]), 4))
        for i in range(len(CATEGORIES))
        if scores[i] >= LABEL_THRESHOLD
    ]
    labels.sort(key=lambda label: label.score, reverse=True)
    return Fragment(
        id=index, text=raw_fragment.text, start=raw_fragment.start,
        end=raw_fragment.end, labels=labels,
    )


def _build_category(
    category_index: int, category_id: str, probabilities: np.ndarray
) -> Category:
    column = probabilities[:, category_index] if probabilities.size else np.array([])
    present_mask = column >= LABEL_THRESHOLD
    fragment_count = int(present_mask.sum())
    present = fragment_count > 0
    relevant = column[present_mask] if fragment_count else column
    confidence = float(relevant.mean()) if relevant.size else 0.0
    return Category(
        id=category_id,
        present=present,
        confidence=round(confidence, 4),
        fragment_count=fragment_count,
        gdpr_reference=gdpr.gdpr_reference_for(category_id),
    )
