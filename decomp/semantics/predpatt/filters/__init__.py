"""Filtering functionality for PredPatt predicates and arguments.

This module provides filtering functions to select or exclude predicates
and arguments based on various linguistic and structural criteria.
"""

from .argument_filters import has_direct_arc, is_not_pronoun, is_sbj_or_obj
from .predicate_filters import (
    activate,
    apply_filters,
    filter_events_nucl,
    filter_events_sprl,
    has_subj,
    is_good_ancestor,
    is_good_descendants,
    is_not_copula,
    is_not_have,
    is_not_interrogative,
    is_pred_verb,
)


__all__ = [
    "activate",
    "apply_filters",
    "filter_events_nucl",
    "filter_events_sprl",
    "has_subj",
    "has_direct_arc",
    "is_good_ancestor",
    "is_good_descendants",
    "is_not_copula",
    "is_not_have",
    # Predicate filters
    "is_not_interrogative",
    "is_not_pronoun",
    "is_pred_verb",
    # Argument filters
    "is_sbj_or_obj",
    # Backward compatibility
    "filter_events_NUCL",
    "filter_events_SPRL",
    "hasSubj",
    "isGoodAncestor",
    "isGoodDescendants",
    "isNotCopula",
    "isNotHave",
    "isNotInterrogative",
    "isNotPronoun",
    "isPredVerb",
    "isSbjOrObj"
]

# Backward compatibility aliases
filter_events_NUCL = filter_events_nucl
filter_events_SPRL = filter_events_sprl
hasSubj = has_subj
isGoodAncestor = is_good_ancestor
isGoodDescendants = is_good_descendants
isNotCopula = is_not_copula
isNotHave = is_not_have
isNotInterrogative = is_not_interrogative
isNotPronoun = is_not_pronoun
isPredVerb = is_pred_verb
isSbjOrObj = is_sbj_or_obj
