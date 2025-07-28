"""Predicate filtering functions for PredPatt.

This module contains filter functions that determine whether predicates
should be included in the final extraction results based on various
linguistic and structural criteria.
"""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..core.predicate import Predicate
    from ..parsing.udparse import UDParse


def isNotInterrogative(pred: Predicate) -> bool:
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
    # tokens = [tk.text for tk in pred.tokens]
    tokens = pred.tokens
    if '?' not in tokens:
        filter_rules = getattr(pred, 'rules', [])
        filter_rules.append(isNotInterrogative.__name__)
        return True
    return False


def isPredVerb(pred: Predicate) -> bool:
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
    filter_rules.append(isPredVerb.__name__)
    return True


def isNotCopula(pred: Predicate) -> bool:
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

    pred_deps_rel = [p.rel for p in pred.root.dependents]
    pred_deps_txt = [p.dep.text for p in pred.root.dependents]
    if 'cop' in pred_deps_rel:
        return False
    # just in case for parsing error (from Stanford Parser)
    if set(pred_deps_txt).intersection(set(copula_verbs)):
        return False
    else:
        filter_rules = getattr(pred, 'rules', [])
        filter_rules.append(isNotCopula.__name__)
        return True


def isGoodAncestor(pred: Predicate) -> bool:
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
        pointer = pointer.gov
    filter_rules = getattr(pred, 'rules', [])
    filter_rules.append(isGoodAncestor.__name__)
    return True


def isGoodDescendants(pred: Predicate) -> bool:
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
    for desc in pred.root.dependents:
        # The following is true if child is in fact a child
        # of verb
        if desc.rel in embedding_deps:
            return False
    filter_rules = getattr(pred, 'rules', [])
    filter_rules.append(isGoodDescendants.__name__)
    return True


def hasSubj(pred: Predicate, passive: bool = False) -> bool:
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
    for x in pred.root.dependents:
        if x.rel in subj_rels:
            filter_rules = getattr(pred, 'rules', [])
            filter_rules.append(hasSubj.__name__)
            return True
    return False


def isNotHave(pred: Predicate) -> bool:
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
        filter_rules.append(isNotHave.__name__)
        return True


def filter_events_NUCL(event: Predicate, parse: UDParse) -> bool:
    """Filters for running Keisuke's NUCLE HIT.

    Combines multiple predicate filters for the NUCL evaluation.
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
        True if event passes all NUCL filters (accept), False otherwise (reject).
    """
    if isNotInterrogative(parse):
        return all(f(event) for f in (isPredVerb,
                                      isNotCopula,
                                      isNotHave,
                                      hasSubj,
                                      isGoodAncestor,
                                      isGoodDescendants))
    #isSbjOrObj (without nsubjpass)
    #isNotPronoun
    #has_direct_arc


def filter_events_SPRL(event: Predicate, parse: UDParse) -> bool:
    """Filters for running UD SPRL HIT.

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
    if isNotInterrogative(parse):
        return all(f(event) for f in (isPredVerb,
                                      isGoodAncestor,
                                      isGoodDescendants,
                                      lambda p: hasSubj(p, passive=True), #(including nsubjpass)
                                      # good_morphology, (documented below;
                                      # depends on full UD/CoNLLU schema)
                                      # isSbjOrObj, #(including nsubjpass)
                                      #is_expletive,
                                  ))


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
    from .argument_filters import has_direct_arc, isNotPronoun, isSbjOrObj

    pred.rules = []
    isNotInterrogative(pred)
    isPredVerb(pred)
    isNotCopula(pred)
    isGoodAncestor(pred)
    isGoodDescendants(pred)
    hasSubj(pred, passive = True)
    isNotHave(pred)
    for arg in pred.arguments:
        arg.rules = []
        isSbjOrObj(arg)
        isNotPronoun(arg)
        has_direct_arc(pred, arg)


def apply_filters(_filter, pred: Predicate, **options) -> bool:
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
    from .argument_filters import has_direct_arc, isNotPronoun, isSbjOrObj

    if _filter in {isSbjOrObj, isNotPronoun}:
        return any(_filter(arg) for arg in pred.arguments)
    elif _filter ==  has_direct_arc:
        return any(_filter(pred, arg) for arg in pred.arguments)
    elif _filter == hasSubj:
        passive = options.get('passive')
        if passive:
            return _filter(pred, passive)
        else:
            return _filter(pred)
    else:
        return _filter(pred)
