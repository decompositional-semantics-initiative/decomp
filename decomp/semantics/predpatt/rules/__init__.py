"""
Rules module for PredPatt with modern Python implementation.

This module contains all the rules used in the PredPatt extraction process,
organized into logical categories for better maintainability.
"""

from __future__ import annotations

# Import argument extraction rules
# Import argument resolution rules
from .argument_rules import (
    G1,
    H1,
    H2,
    W1,
    W2,
    ArgResolveRelcl,
    BorrowObj,
    BorrowSubj,
    CleanArgToken,
    CutBorrowObj,
    CutBorrowOther,
    CutBorrowSubj,
    DropAppos,
    DropCc,
    DropConj,
    DropUnknown,
    EmbeddedAdvcl,
    EmbeddedCcomp,
    EmbeddedUnknown,
    J,
    K,
    L,
    M,
    MoveCaseTokenToPred,
    PredicateHas,
    PredResolveRelcl,
    RuleI,
    ShareArgument,
    SpecialArgDropDirectDep,
)
from .argument_rules import (
    EnRelclDummyArgFilter as EnRelclDummyArgFilterArg,
)
from .argument_rules import (
    RuleI as I,
)

# Import base rule class
# Import rule categories
from .base import (
    ArgPhraseRule,
    ArgumentResolution,
    ArgumentRootRule,
    ConjunctionResolution,
    EnglishSpecific,
    LanguageSpecific,
    PredConjRule,
    PredicateRootRule,
    PredPhraseRule,
    Rule,
    SimplifyRule,
)

# Import helper functions
from .helpers import gov_looks_like_predicate

# Import predicate extraction rules
# Import predicate conjunction rules
# Import phrase rules
# Import simplification rules
# Import utility rules
# Import language-specific rules
from .predicate_rules import (
    A1,
    A2,
    N1,
    N2,
    N3,
    N4,
    N5,
    N6,
    P1,
    P2,
    B,
    C,
    D,
    E,
    F,
    PredConjBorrowAuxNeg,
    PredConjBorrowTokensXcomp,
    Q,
    R,
    U,
    V,
)
from .predicate_rules import (
    EnRelclDummyArgFilter as EnRelclDummyArgFilterPred,
)


# Create lowercase aliases for backward compatibility
# This allows code to use either R.g1 or R.G1
g1 = G1
h1 = H1
h2 = H2
i = I
j = J
k = K
l_rule = L
l = L  # Keep for compatibility
m = M
w1 = W1
w2 = W2

a1 = A1
a2 = A2
b = B
c = C
d = D
e = E
f = F
v = V

n1 = N1
n2 = N2
n3 = N3
n4 = N4
n5 = N5
n6 = N6

p1 = P1
p2 = P2
q = Q
r = R
u = U

arg_resolve_relcl = ArgResolveRelcl
borrow_obj = BorrowObj
borrow_subj = BorrowSubj
clean_arg_token = CleanArgToken
cut_borrow_obj = CutBorrowObj
cut_borrow_other = CutBorrowOther
cut_borrow_subj = CutBorrowSubj
drop_appos = DropAppos
drop_cc = DropCc
drop_conj = DropConj
drop_unknown = DropUnknown
embedded_advcl = EmbeddedAdvcl
embedded_ccomp = EmbeddedCcomp
embedded_unknown = EmbeddedUnknown
move_case_token_to_pred = MoveCaseTokenToPred
pred_resolve_relcl = PredResolveRelcl
predicate_has = PredicateHas
share_argument = ShareArgument
special_arg_drop_direct_dep = SpecialArgDropDirectDep
pred_conj_borrow_aux_neg = PredConjBorrowAuxNeg
pred_conj_borrow_tokens_xcomp = PredConjBorrowTokensXcomp

# For the two en_relcl_dummy_arg_filter classes, use the argument one as default
en_relcl_dummy_arg_filter = EnRelclDummyArgFilterArg

__all__ = [
    # Predicate root rules (PascalCase)
    "A1",
    "A2",
    # Argument root rules (PascalCase)
    "G1",
    "H1",
    "H2",
    # Predicate phrase rules (PascalCase)
    "N1",
    "N2",
    "N3",
    "N4",
    "N5",
    "N6",
    # Simplification rules (PascalCase)
    "P1",
    "P2",
    "W1",
    "W2",
    "ArgPhraseRule",
    "ArgResolveRelcl",
    "ArgumentResolution",
    "ArgumentRootRule",
    "B",
    "BorrowObj",
    "BorrowSubj",
    "C",
    # Argument phrase rules (PascalCase)
    "CleanArgToken",
    "ConjunctionResolution",
    "CutBorrowObj",
    # Argument resolution rules (PascalCase)
    "CutBorrowOther",
    "CutBorrowSubj",
    "D",
    "DropAppos",
    "DropCc",
    "DropConj",
    "DropUnknown",
    "E",
    "EmbeddedAdvcl",
    "EmbeddedCcomp",
    "EmbeddedUnknown",
    # Language-specific rules
    "EnRelclDummyArgFilterArg",
    "EnRelclDummyArgFilterPred",
    "EnglishSpecific",
    "F",
    "I",
    "J",
    "K",
    "L",
    "LanguageSpecific",
    "M",
    "MoveCaseTokenToPred",
    # Predicate conjunction rules (PascalCase)
    "PredConjBorrowAuxNeg",
    "PredConjBorrowTokensXcomp",
    "PredConjRule",
    "PredPhraseRule",
    "PredResolveRelcl",
    "PredicateHas",
    "PredicateRootRule",
    "Q",
    "R",
    # Base classes
    "Rule",
    "ShareArgument",
    "SimplifyRule",
    "SpecialArgDropDirectDep",
    # Utility rules (PascalCase)
    "U",
    "V",
    # Lowercase aliases
    "a1",
    "a2",
    "arg_resolve_relcl",
    "b",
    "borrow_obj",
    "borrow_subj",
    "c",
    # Lowercase aliases
    "clean_arg_token",
    "cut_borrow_obj",
    # Lowercase aliases
    "cut_borrow_other",
    "cut_borrow_subj",
    "d",
    "drop_appos",
    "drop_cc",
    "drop_conj",
    "drop_unknown",
    "e",
    "embedded_advcl",
    "embedded_ccomp",
    "embedded_unknown",
    "en_relcl_dummy_arg_filter",
    "f",
    # Lowercase aliases
    "g1",
    # Helper functions
    "gov_looks_like_predicate",
    "h1",
    "h2",
    "i",
    "j",
    "k",
    "l",
    "l_rule",
    "m",
    "move_case_token_to_pred",
    # Lowercase aliases
    "n1",
    "n2",
    "n3",
    "n4",
    "n5",
    "n6",
    # Lowercase aliases
    "p1",
    "p2",
    # Lowercase aliases
    "pred_conj_borrow_aux_neg",
    "pred_conj_borrow_tokens_xcomp",
    "pred_resolve_relcl",
    "predicate_has",
    "q",
    "r",
    "share_argument",
    "special_arg_drop_direct_dep",
    # Lowercase aliases
    "u",
    "v",
    "w1",
    "w2",
]
