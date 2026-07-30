"""Exposure ("semaforo") layer: turns the per-category fragment counts into a
low/medium/high exposure level for the user.

THE QUESTION IT ANSWERS
How many hands do my data pass through, how long do they stay, and am I left any
control. It measures privacy EXPOSURE, not legal compliance: a site can comply
perfectly and still expose you a lot (2_spec.md 7.1).

HOW IT SCORES
score = sum(weight * share of fragments of that category)

Shares, not raw counts, so a long policy is not penalised for being long. The
share is computed over the TOTAL number of fragments, `Other` included: if 60% of
a policy is contact details and boilerplate, that should dilute the score,
because it genuinely is what the document is made of.

WHY THE WEIGHTS ARE ASYMMETRIC (+3 max, -1 min)
The model detects WHAT a paragraph is about, not whether it is done well. That a
policy mentions data security does not mean the measures are adequate; that it
declares sharing data with third parties IS a verifiable fact. So what raises
exposure is more reliable than what lowers it, and is weighted accordingly. For a
privacy tool, the error we cannot afford is painting a site green because it said
the word "security" three times.

WHY do_not_track IS EXCLUDED
The category is blind to polarity: it fires the same for "we honour DNT signals"
and for "we do not respond to DNT signals" (2_spec.md 13.2). No fixed weight is
correct — a negative one would reward a site for declaring that it ignores the
signal. It is surfaced as information, it does not score.

LIMITATION, STATED TO THE USER
This is an estimate by topic presence, not a clause-by-clause reading. The
disclaimer travels with every response and the frontend must show it.
"""

from .schemas import Exposure

# Weight per category. Positive raises exposure, negative lowers it.
# See the module docstring for why they are asymmetric.
WEIGHTS: dict[str, float] = {
    # Data leaves the organisation: the single most consequential fact.
    "third_party_sharing_collection": 3.0,
    # What is kept stays exposed: to breaches, to new owners, to new uses.
    "data_retention": 2.0,
    # Collection raises it, but mildly: it is the expected starting point of any
    # service, not an anomaly.
    "first_party_collection_use": 1.0,
    # Includes international transfers, which do expose (other jurisdictions,
    # other guarantees). Low weight because the category also bundles minors and
    # region-specific rules.
    "international_specific_audiences": 1.0,
    # Tells you how a change is communicated, not what is done with the data.
    "policy_change": 0.0,
    # These three lower exposure: they protect, or hand control back.
    "data_security": -1.0,
    "user_choice_control": -1.0,
    "user_access_edit_deletion": -1.0,
    # Blind to polarity — see docstring. Shown as information, does not score.
    "do_not_track": 0.0,
    # Not a data practice. Counts towards the total, does not score.
    "Other": 0.0,
}

# Cut-off points. PROVISIONAL: unlike the weights, which are argued from the
# meaning of each category, these two numbers are an initial guess. They are
# calibrated by scoring real policies and checking the level matches what a
# person reading them would say — the exposure layer has no metric, it is
# validated by judgement.
MEDIUM_THRESHOLD = 0.5
HIGH_THRESHOLD = 1.0

DISCLAIMER = (
    "Estimacion basada en los temas detectados, no en una lectura "
    "clausula por clausula."
)


def compute_exposure(categories: list) -> Exposure:
    """Weighted exposure over the share of fragments each category holds.

    `categories` are the Category objects built by analyze.py, whose
    `fragment_count` is how many fragments that class won. Unknown category ids
    are ignored rather than raising: a new class must not break the response.
    """
    total = sum(category.fragment_count for category in categories)

    if total == 0:
        # Nothing to score (empty document). Report it instead of inventing a level.
        return Exposure(level="unknown", score=0.0, disclaimer=DISCLAIMER)

    score = sum(
        WEIGHTS.get(category.id, 0.0) * (category.fragment_count / total)
        for category in categories
    )

    if score > HIGH_THRESHOLD:
        level = "high"
    elif score >= MEDIUM_THRESHOLD:
        level = "medium"
    else:
        level = "low"

    return Exposure(level=level, score=round(score, 4), disclaimer=DISCLAIMER)