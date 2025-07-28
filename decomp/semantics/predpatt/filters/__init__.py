"""Filtering functionality for PredPatt predicates and arguments.

This module provides filtering functions to select or exclude predicates
and arguments based on various linguistic and structural criteria.
"""

from .argument_filters import has_direct_arc, isNotPronoun, isSbjOrObj
from .predicate_filters import (
    activate,
    apply_filters,
    filter_events_NUCL,
    filter_events_SPRL,
    hasSubj,
    isGoodAncestor,
    isGoodDescendants,
    isNotCopula,
    isNotHave,
    isNotInterrogative,
    isPredVerb,
)


__all__ = [
    "activate",
    "apply_filters",
    "filter_events_NUCL",
    "filter_events_SPRL",
    "hasSubj",
    "has_direct_arc",
    "isGoodAncestor",
    "isGoodDescendants",
    "isNotCopula",
    "isNotHave",
    # Predicate filters
    "isNotInterrogative",
    "isNotPronoun",
    "isPredVerb",
    # Argument filters
    "isSbjOrObj"
]
