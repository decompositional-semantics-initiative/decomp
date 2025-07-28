"""Filtering functionality for PredPatt predicates and arguments.

This module provides filtering functions to select or exclude predicates
and arguments based on various linguistic and structural criteria.
"""

from .predicate_filters import (
    isNotInterrogative,
    isPredVerb, 
    isNotCopula,
    isGoodAncestor,
    isGoodDescendants,
    hasSubj,
    isNotHave,
    filter_events_NUCL,
    filter_events_SPRL,
    activate,
    apply_filters
)

from .argument_filters import (
    isSbjOrObj,
    isNotPronoun,
    has_direct_arc
)

__all__ = [
    # Predicate filters
    "isNotInterrogative",
    "isPredVerb",
    "isNotCopula", 
    "isGoodAncestor",
    "isGoodDescendants",
    "hasSubj",
    "isNotHave",
    "filter_events_NUCL",
    "filter_events_SPRL",
    "activate",
    "apply_filters",
    # Argument filters
    "isSbjOrObj",
    "isNotPronoun",
    "has_direct_arc"
]