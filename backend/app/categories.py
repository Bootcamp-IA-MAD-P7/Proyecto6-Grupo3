"""The 10 classes of the multiclass target, in fixed order.
The first 9 are the official categories from specs/4_data_contract.md; `Other`
is the tenth class of the multiclass target (fragments that describe no data
practice: introductions, contact details, definitions).
Do not reorder: this order maps the columns of the model's probability matrix.
"""
CATEGORIES = [
    "first_party_collection_use",
    "third_party_sharing_collection",
    "user_choice_control",
    "user_access_edit_deletion",
    "data_retention",
    "data_security",
    "policy_change",
    "do_not_track",
    "international_specific_audiences",
    "Other",
]