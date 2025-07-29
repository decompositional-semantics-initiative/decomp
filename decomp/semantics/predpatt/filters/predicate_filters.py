"""Predicate filtering functions for PredPatt.

This module contains filter functions that determine whether predicates
should be included in the final extraction results based on various
linguistic and structural criteria.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..core.predicate import Predicate
    from ..parsing.udparse import UDParse


def is_not_interrogative(pred: Predicate) -> bool:
    """Filter out interrogative predicates.

    Checks if the predicate contains a question mark. This is a simple
    heuristic filter to exclude interrogative sentences.

    Parameters
    ----------
    pred : Predicate
        The predicate to check.

    Returns
    -------
    bool
        True if predicate does not contain '?' (accept), False otherwise (reject).
    """
    # Check if any token text contains '?'
    token_texts = [tk.text for tk in pred.tokens]
    if '?' not in token_texts:
        filter_rules = getattr(pred, 'rules', [])
        filter_rules.append(is_not_interrogative.__name__)
        return True
    return False


def is_pred_verb(pred: Predicate) -> bool:
    """Filter to accept only verbal predicates.

    Checks if the predicate root has a verbal part-of-speech tag
    (starts with 'V').

    Parameters
    ----------
    pred : Predicate
        The predicate to check.

    Returns
    -------
    bool
        True if predicate root tag starts with 'V' (accept), False otherwise (reject).
    """
    if not pred.root.tag.startswith('V'):
        return False
    filter_rules = getattr(pred, 'rules', [])
    filter_rules.append(is_pred_verb.__name__)
    return True


def is_not_copula(pred: Predicate) -> bool:
    """Filter out copula constructions.

    Checks if any of the dependents of pred are copula verbs.
    UD annotates copula verbs only when the nonverbal predicate
    is the head of the clause.

    Parameters
    ----------
    pred : Predicate
        The predicate to check.

    Returns
    -------
    bool
        True if predicate is not a copula construction (accept), False otherwise (reject).
    """
    copula_verbs = ['be', 'am', 'is', 'are', 'was', 'were', 'being', 'been']

    if pred.root.dependents is None:
        raise TypeError(f"Cannot filter predicate {pred}: root token has no dependency information")
    pred_deps_rel = [p.rel for p in pred.root.dependents]
    pred_deps_txt = [p.dep.text for p in pred.root.dependents]
    if 'cop' in pred_deps_rel:
        return False
    # just in case for parsing error (from Stanford Parser)
    if set(pred_deps_txt).intersection(set(copula_verbs)):
        return False
    else:
        filter_rules = getattr(pred, 'rules', [])
        filter_rules.append(is_not_copula.__name__)
        return True


def is_good_ancestor(pred: Predicate) -> bool:
    """Filter predicates with good ancestry.

    Returns true if verb is not dominated by a relation
    that might alter its veridicality. This filter is very
    conservative; many veridical verbs will be excluded.

    Parameters
    ----------
    pred : Predicate
        The predicate to check.

    Returns
    -------
    bool
        True if predicate has good ancestry (accept), False otherwise (reject).
    """
    # Move to ud_filters
    # Technically, conj shouldn't be a problem, but
    # some bad annotations mean we need to exclude it.
    #   ex. "It is a small one and easily missed" ("missed" has
    #   "one" as a head with relation "conj")
    embedding_deps = {"acl", "mwe", "ccomp", "xcomp", "advcl",
                      "acl:relcl", "case", "conj", "parataxis", "csubj",
                      "compound", "nmod"}
    pointer = pred.root # index of predicate
    while pointer.gov_rel != 'root':
        if pointer.gov_rel in embedding_deps:
            return False
        # Replace pointer with its head
        if pointer.gov is None:
            break
        pointer = pointer.gov
    filter_rules = getattr(pred, 'rules', [])
    filter_rules.append(is_good_ancestor.__name__)
    return True


def is_good_descendants(pred: Predicate) -> bool:
    """Filter predicates with good descendants.

    Returns true if verb immediately dominates a relation that might alter
    its veridicality. This filter is very
    conservative; many veridical verbs will be excluded.

    Parameters
    ----------
    pred : Predicate
        The predicate to check.

    Returns
    -------
    bool
        True if predicate has good descendants (accept), False otherwise (reject).
    """
    embedding_deps = {"neg", "advmod", "aux", "mark", "advcl", "appos"}
    if pred.root.dependents is None:
        raise TypeError(f"Cannot check descendants for predicate {pred}: root token has no dependency information")
    for desc in pred.root.dependents:
        # The following is true if child is in fact a child
        # of verb
        if desc.rel in embedding_deps:
            return False
    filter_rules = getattr(pred, 'rules', [])
    filter_rules.append(is_good_descendants.__name__)
    return True


def has_subj(pred: Predicate, passive: bool = False) -> bool:
    """Filter predicates that have subjects.

    Checks if the predicate has a subject dependent. Optionally
    includes passive subjects (nsubjpass) when passive=True.

    Parameters
    ----------
    pred : Predicate
        The predicate to check.
    passive : bool, optional
        Whether to include passive subjects (nsubjpass). Default: False.

    Returns
    -------
    bool
        True if predicate has a subject (accept), False otherwise (reject).
    """
    subj_rels = ('nsubj','nsubjpass') if passive else ('nsubj',)
    # the original filter function considers nsubjpass
    #if (('nsubj' in [x.rel for x in parse.dependents[event.root]])
    #    or ('nsubjpass' in [x.rel for x in parse.dependents[event.root]])):
    if pred.root.dependents is None:
        raise TypeError(f"Cannot check subjects for predicate {pred}: root token has no dependency information")
    for x in pred.root.dependents:
        if x.rel in subj_rels:
            filter_rules = getattr(pred, 'rules', [])
            filter_rules.append(has_subj.__name__)
            return True
    return False


def is_not_have(pred: Predicate) -> bool:
    """Filter out 'have' verbs.

    Excludes predicates with 'have', 'had', or 'has' as the root text.

    Parameters
    ----------
    pred : Predicate
        The predicate to check.

    Returns
    -------
    bool
        True if predicate is not a 'have' verb (accept), False otherwise (reject).
    """
    have_verbs = {'have', 'had', 'has'}
    if pred.root.text in have_verbs:
        return False
    else:
        filter_rules = getattr(pred, 'rules', [])
        filter_rules.append(is_not_have.__name__)
        return True


def filter_events_nucl(event: Predicate, parse: UDParse) -> bool:
    """Apply filters for running Keisuke's NUCLE HIT.

    Combines multiple predicate filters for the NUCL evaluation.
    Only applies if the event is not interrogative.

    Parameters
    ----------
    event : Predicate
        The predicate event to filter.
    parse : UDParse
        The dependency parse (included for compatibility).

    Returns
    -------
    bool
        True if event passes all NUCL filters (accept), False otherwise (reject).
    """
    if is_not_interrogative(event):
        return all(f(event) for f in (is_pred_verb,
                                      is_not_copula,
                                      is_not_have,
                                      has_subj,
                                      is_good_ancestor,
                                      is_good_descendants))
    return False
    #isSbjOrObj (without nsubjpass)
    #isNotPronoun
    #has_direct_arc


def filter_events_sprl(event: Predicate, parse: UDParse) -> bool:
    """Apply filters for running UD SPRL HIT.

    Combines multiple predicate filters for the SPRL evaluation.
    Only applies if the parse is not interrogative.

    Parameters
    ----------
    event : Predicate
        The predicate event to filter.
    parse : UDParse
        The dependency parse (used for interrogative check).

    Returns
    -------
    bool
        True if event passes all SPRL filters (accept), False otherwise (reject).
    """
    if is_not_interrogative(event):
        return all(f(event) for f in (is_pred_verb,
                                      is_good_ancestor,
                                      is_good_descendants,
                                      lambda p: has_subj(p, passive=True), #(including nsubjpass)
                                      # good_morphology, (documented below;
                                      # depends on full UD/CoNLLU schema)
                                      # isSbjOrObj, #(including nsubjpass)
                                      #is_expletive,
                                  ))
    return False


def activate(pred: Predicate) -> None:
    """Apply all predicate and argument filters to a predicate.

    Demonstrates how to apply all available filters to a predicate
    and its arguments. Initializes empty rules lists before applying.

    Parameters
    ----------
    pred : Predicate
        The predicate to apply all filters to.
    """
    # Import here to avoid circular dependency
    from .argument_filters import has_direct_arc, is_not_pronoun, is_sbj_or_obj

    pred.rules = []
    is_not_interrogative(pred)
    is_pred_verb(pred)
    is_not_copula(pred)
    is_good_ancestor(pred)
    is_good_descendants(pred)
    has_subj(pred, passive = True)
    is_not_have(pred)
    for arg in pred.arguments:
        arg.rules = []
        is_sbj_or_obj(arg)
        is_not_pronoun(arg)
        has_direct_arc(pred, arg)


def apply_filters(_filter: Callable[..., bool], pred: Predicate, **options: bool) -> bool:
    """Apply a filter function with proper parameter handling.

    Handles different filter function signatures and parameter requirements.
    Supports both predicate filters and argument filters.

    Parameters
    ----------
    _filter : callable
        The filter function to apply.
    pred : Predicate
        The predicate to filter.
    **options
        Additional options for the filter (e.g., passive for hasSubj).

    Returns
    -------
    bool
        True if filter accepts the predicate/arguments, False otherwise.
    """
    # Import here to avoid circular dependency
    from .argument_filters import has_direct_arc, is_not_pronoun, is_sbj_or_obj

    if _filter in {is_sbj_or_obj, is_not_pronoun}:
        return any(_filter(arg) for arg in pred.arguments)
    elif _filter ==  has_direct_arc:
        return any(_filter(pred, arg) for arg in pred.arguments)
    elif _filter == has_subj:
        passive = options.get('passive')
        if passive:
            return _filter(pred, passive)
        else:
            return _filter(pred)
    else:
        return _filter(pred)
