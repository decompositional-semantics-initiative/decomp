"""
Rules module for PredPatt with modern Python implementation.

This module contains all the rules used in the PredPatt extraction process,
organized into logical categories for better maintainability.
"""

from __future__ import annotations

# Import base rule class
from .base import Rule

# Import rule categories
from .base import (
    PredicateRootRule,
    ArgumentRootRule,
    PredConjRule,
    ArgumentResolution,
    ConjunctionResolution,
    SimplifyRule,
    PredPhraseRule,
    ArgPhraseRule,
    LanguageSpecific,
    EnglishSpecific,
)

# Import predicate extraction rules
from .predicate_rules import (
    a1,
    a2,
    b,
    c,
    d,
    e,
    f,
    v,
)

# Import argument extraction rules
from .argument_rules import (
    g1,
    h1,
    h2,
    i,
    j,
    k,
    w1,
    w2,
)

# Import predicate conjunction rules
from .predicate_rules import (
    pred_conj_borrow_aux_neg,
    pred_conj_borrow_tokens_xcomp,
)

# Import argument resolution rules
from .argument_rules import (
    cut_borrow_other,
    cut_borrow_subj,
    cut_borrow_obj,
    borrow_subj,
    borrow_obj,
    share_argument,
    arg_resolve_relcl,
    pred_resolve_relcl,
    l,
    m,
)

# Import phrase rules
from .predicate_rules import (
    n1,
    n2,
    n3,
    n4,
    n5,
    n6,
)

from .argument_rules import (
    clean_arg_token,
    move_case_token_to_pred,
    predicate_has,
    drop_appos,
    drop_unknown,
    drop_cc,
    drop_conj,
    special_arg_drop_direct_dep,
    embedded_advcl,
    embedded_ccomp,
    embedded_unknown,
)

# Import simplification rules
from .predicate_rules import (
    p1,
    p2,
    q,
    r,
)

# Import utility rules
from .predicate_rules import u

# Import language-specific rules
from .predicate_rules import en_relcl_dummy_arg_filter

# Import helper functions
from .helpers import gov_looks_like_predicate

__all__ = [
    # Base classes
    "Rule",
    "PredicateRootRule",
    "ArgumentRootRule",
    "PredConjRule",
    "ArgumentResolution",
    "ConjunctionResolution",
    "SimplifyRule",
    "PredPhraseRule",
    "ArgPhraseRule",
    "LanguageSpecific",
    "EnglishSpecific",
    
    # Predicate root rules
    "a1", "a2", "b", "c", "d", "e", "f", "v",
    
    # Argument root rules
    "g1", "h1", "h2", "i", "j", "k", "w1", "w2",
    
    # Predicate conjunction rules
    "pred_conj_borrow_aux_neg",
    "pred_conj_borrow_tokens_xcomp",
    
    # Argument resolution rules
    "cut_borrow_other",
    "cut_borrow_subj",
    "cut_borrow_obj",
    "borrow_subj",
    "borrow_obj",
    "share_argument",
    "arg_resolve_relcl",
    "pred_resolve_relcl",
    "l",
    "m",
    
    # Predicate phrase rules
    "n1", "n2", "n3", "n4", "n5", "n6",
    
    # Argument phrase rules
    "clean_arg_token",
    "move_case_token_to_pred",
    "predicate_has",
    "drop_appos",
    "drop_unknown",
    "drop_cc",
    "drop_conj",
    "special_arg_drop_direct_dep",
    "embedded_advcl",
    "embedded_ccomp",
    "embedded_unknown",
    
    # Simplification rules
    "p1", "p2", "q", "r",
    
    # Utility rules
    "u",
    
    # Language-specific rules
    "en_relcl_dummy_arg_filter",
    
    # Helper functions
    "gov_looks_like_predicate",
]