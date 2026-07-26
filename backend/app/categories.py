"""The 9 official categories, in the fixed order from specs/4_data_contract.md.

Do not reorder: this order is the one used across the dataset, the training
table columns, and the API contract.
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
]
