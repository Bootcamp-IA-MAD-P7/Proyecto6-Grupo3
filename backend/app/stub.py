"""Fake probability generator (stub model).

See specs/5_backend_contract.md, STUB. The day the real model exists, only
`predict_proba` is replaced (by model.predict_proba over the TF-IDF vectors,
see specs/4_data_contract.md) — callers and the response contract don't change.

Seeded by the full input text, so the same input always produces the same
output (required so the frontend can develop against a stable response).
"""

import hashlib

import numpy as np

from .categories import CATEGORIES


def predict_proba(fragment_texts: list[str], full_text: str) -> np.ndarray:
    """Return an (n_fragments, 9) matrix of fake per-category probabilities."""
    if not fragment_texts:
        return np.empty((0, len(CATEGORIES)))
    seed = int(hashlib.sha256(full_text.encode("utf-8")).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)
    return rng.random((len(fragment_texts), len(CATEGORIES)))
