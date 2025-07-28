"""Argument filtering functions for PredPatt.

This module contains filter functions that determine whether arguments
should be included in the final extraction results based on various
linguistic and structural criteria.
"""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..core.argument import Argument
    from ..core.predicate import Predicate


def isSbjOrObj(arg: Argument) -> bool:
    """Filter to accept core arguments (subjects and objects).

    Accepts arguments with core grammatical relations: nsubj, dobj, iobj.

    Parameters
    ----------
    arg : Argument
        The argument to check.

    Returns
    -------
    bool
        True if argument is a core argument (accept), False otherwise (reject).
    """
    if arg.root.gov_rel in ('nsubj', 'dobj', 'iobj'):
        filter_rules = getattr(arg, 'rules', [])
        filter_rules.append(isSbjOrObj.__name__)
        return True
    return False


def isNotPronoun(arg: Argument) -> bool:
    """Filter out pronoun arguments.

    Excludes arguments that are pronouns (PRP tag) or specific
    pronoun-like words: that, this, which, what.

    Parameters
    ----------
    arg : Argument
        The argument to check.

    Returns
    -------
    bool
        True if argument is not a pronoun (accept), False otherwise (reject).
    """
    if arg.root.tag == 'PRP':
        return False
    if arg.root.text.lower() in ['that', 'this', 'which', 'what']:
        return False
    else:
        filter_rules = getattr(arg, 'rules', [])
        filter_rules.append(isNotPronoun.__name__)
        return True


def has_direct_arc(pred: Predicate, arg: Argument) -> bool:
    """Check if the argument and predicate has a direct arc.

    Verifies that the argument root token is directly governed
    by the predicate root token.

    Parameters
    ----------
    pred : Predicate
        The predicate.
    arg : Argument
        The argument to check.

    Returns
    -------
    bool
        True if there is a direct dependency arc (accept), False otherwise (reject).
    """
    if arg.root.gov == pred.root:
        filter_rules = getattr(arg, 'rules', [])
        filter_rules.append(has_direct_arc.__name__)
        return True
    return False
