"""Exposure ("semaforo") layer: interface wired, scoring not implemented yet.

See 2_spec.md §7: the weights per category and the low/medium/high thresholds
are an open TODO in the spec. Returning a fixed placeholder here is a team
decision (specs/5_backend_contract.md) — do NOT simulate the real scoring.
"""

from .schemas import Exposure

_PLACEHOLDER = Exposure(
    level="medium",
    score=0.5,
    disclaimer=(
        "Estimacion basada en los temas detectados, no en una lectura "
        "clausula por clausula."
    ),
)


def compute_exposure(categories: list) -> Exposure:
    return _PLACEHOLDER
