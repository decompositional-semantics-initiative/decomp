"""Filtering functions for refining PredPatt extractions.

This module provides predicate and argument filters that can be applied
to refine the output of PredPatt extraction based on linguistic criteria
such as verb type, syntactic role, and semantic properties.

Functions
---------
Predicate Filters
~~~~~~~~~~~~~~~~~
is_pred_verb
    Check if predicate root is a verb.
is_not_copula
    Exclude copular predicates.
is_not_have
    Exclude "have" predicates.
is_not_interrogative
    Exclude interrogative predicates.
has_subj
    Check if predicate has a subject.
is_good_ancestor
    Check if predicate has good dependency ancestors.
is_good_descendants
    Check if predicate has good dependency descendants.
filter_events_nucl
    Filter predicates for NUCL event extraction.
filter_events_sprl
    Filter predicates for SituatedPRL event extraction.

Argument Filters
~~~~~~~~~~~~~~~~
is_sbj_or_obj
    Check if argument is subject or object.
is_not_pronoun
    Exclude pronominal arguments.
has_direct_arc
    Check for direct dependency arc.

Filter Application
~~~~~~~~~~~~~~~~~~
apply_filters
    Apply multiple filters to extractions.
activate
    Activate specific filter configurations.

Notes
-----
Filters can be combined using PredPattOpts to customize extraction behavior.
Backward compatibility aliases use camelCase naming.
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
    # Backward compatibility
    "filter_events_NUCL",
    "filter_events_SPRL",
    "filter_events_nucl",
    "filter_events_sprl",
    "hasSubj",
    "has_direct_arc",
    "has_subj",
    "isGoodAncestor",
    "isGoodDescendants",
    "isNotCopula",
    "isNotHave",
    "isNotInterrogative",
    "isNotPronoun",
    "isPredVerb",
    "isSbjOrObj",
    "is_good_ancestor",
    "is_good_descendants",
    "is_not_copula",
    "is_not_have",
    # Predicate filters
    "is_not_interrogative",
    "is_not_pronoun",
    "is_pred_verb",
    # Argument filters
    "is_sbj_or_obj"
]

# Backward compatibility aliases
filter_events_NUCL = filter_events_nucl  # noqa: N816
filter_events_SPRL = filter_events_sprl  # noqa: N816
hasSubj = has_subj  # noqa: N816
isGoodAncestor = is_good_ancestor  # noqa: N816
isGoodDescendants = is_good_descendants  # noqa: N816
isNotCopula = is_not_copula  # noqa: N816
isNotHave = is_not_have  # noqa: N816
isNotInterrogative = is_not_interrogative  # noqa: N816
isNotPronoun = is_not_pronoun  # noqa: N816
isPredVerb = is_pred_verb  # noqa: N816
isSbjOrObj = is_sbj_or_obj  # noqa: N816
