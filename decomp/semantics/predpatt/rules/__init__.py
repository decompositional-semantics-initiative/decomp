"""Linguistic rules for predicate-argument extraction in PredPatt.

This module implements the rule system that drives PredPatt's extraction
of predicates and arguments from Universal Dependencies parses. Rules are
organized into categories based on their linguistic function.

The rule system consists of:

- **Predicate rules**: Identify verbal and non-verbal predicates
- **Argument rules**: Extract syntactic arguments of predicates
- **Resolution rules**: Handle complex phenomena like coordination
- **Simplification rules**: Optional rules for simplified extraction

Classes
-------
Rule
    Abstract base class for all extraction rules.
PredicateRootRule
    Rules for identifying predicate root tokens.
ArgumentRootRule
    Rules for extracting argument root tokens.
PredPhraseRule
    Rules for building predicate phrases.
ArgPhraseRule
    Rules for building argument phrases.
ArgumentResolution
    Rules for resolving complex argument structures.
ConjunctionResolution
    Rules for handling coordinated structures.
SimplifyRule
    Rules for simplified extraction mode.
LanguageSpecific
    Base class for language-specific rules.
EnglishSpecific
    Rules specific to English syntax.

Functions
---------
gov_looks_like_predicate
    Helper to check if a governor token is predicate-like.

Notes
-----
Rules are identified by single letters (A-W) or letter-number combinations
(A1, N2). Lowercase aliases are provided for backward compatibility.
"""

from __future__ import annotations

# import argument extraction rules
# import argument resolution rules
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

# import base rule class
# import rule categories
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

# import helper functions
from .helpers import gov_looks_like_predicate

# import predicate extraction rules
# import predicate conjunction rules
# import phrase rules
# import simplification rules
# import utility rules
# import language-specific rules
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


# create lowercase aliases for backward compatibility
# this allows code to use either R.g1 or R.G1
g1 = G1
h1 = H1
h2 = H2
i = I
j = J
k = K
l_rule = L
l = L  # noqa: E741 - Keep for compatibility
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

# for the two en_relcl_dummy_arg_filter classes, use the argument one as default
en_relcl_dummy_arg_filter = EnRelclDummyArgFilterArg

__all__ = [
    # predicate root rules (PascalCase)
    "A1",
    "A2",
    # argument root rules (PascalCase)
    "G1",
    "H1",
    "H2",
    # predicate phrase rules (PascalCase)
    "N1",
    "N2",
    "N3",
    "N4",
    "N5",
    "N6",
    # simplification rules (PascalCase)
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
    # argument phrase rules (PascalCase)
    "CleanArgToken",
    "ConjunctionResolution",
    "CutBorrowObj",
    # argument resolution rules (PascalCase)
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
    # language-specific rules
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
    # predicate conjunction rules (PascalCase)
    "PredConjBorrowAuxNeg",
    "PredConjBorrowTokensXcomp",
    "PredConjRule",
    "PredPhraseRule",
    "PredResolveRelcl",
    "PredicateHas",
    "PredicateRootRule",
    "Q",
    "R",
    # base classes
    "Rule",
    "ShareArgument",
    "SimplifyRule",
    "SpecialArgDropDirectDep",
    # utility rules (PascalCase)
    "U",
    "V",
    # lowercase aliases
    "a1",
    "a2",
    "arg_resolve_relcl",
    "b",
    "borrow_obj",
    "borrow_subj",
    "c",
    # lowercase aliases
    "clean_arg_token",
    "cut_borrow_obj",
    # lowercase aliases
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
    # lowercase aliases
    "g1",
    # helper functions
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
    # lowercase aliases
    "n1",
    "n2",
    "n3",
    "n4",
    "n5",
    "n6",
    # lowercase aliases
    "p1",
    "p2",
    # lowercase aliases
    "pred_conj_borrow_aux_neg",
    "pred_conj_borrow_tokens_xcomp",
    "pred_resolve_relcl",
    "predicate_has",
    "q",
    "r",
    "share_argument",
    "special_arg_drop_direct_dep",
    # lowercase aliases
    "u",
    "v",
    "w1",
    "w2",
]
