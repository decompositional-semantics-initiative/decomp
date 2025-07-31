"""Predicate extraction rules for PredPatt.

This module contains rules for identifying predicate root tokens,
building predicate phrases, and handling predicate-specific phenomena.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import (
    EnglishSpecific,
    PredConjRule,
    PredicateRootRule,
    PredPhraseRule,
    SimplifyRule,
)


if TYPE_CHECKING:
    from ..core.predicate import Predicate
    from ..core.token import Token
    from ..parsing.udparse import DepTriple


# predicate root identification rules

class A1(PredicateRootRule):
    """Extract a predicate token from the dependent of clausal relation {ccomp, csub, csubjpass}."""

    rule_type = 'predicate_root'


class A2(PredicateRootRule):
    """Extract a predicate token from the dependent of clausal complement 'xcomp'."""

    rule_type = 'predicate_root'


class B(PredicateRootRule):
    """Extract a predicate token from the dependent of clausal modifier."""

    rule_type = 'predicate_root'


class C(PredicateRootRule):
    """Extract a predicate token from the governor of predicate-indicating relations.

    Relations: {nsubj, nsubjpass, dobj, iobj, ccomp, xcomp, advcl}.
    """

    rule_type = 'predicate_root'

    def __init__(self, e: DepTriple) -> None:
        """Initialize with the dependency edge that triggered this rule.

        Parameters
        ----------
        e : DepTriple
            The dependency edge with a predicate-indicating relation.
        """
        super().__init__()
        self.e = e

    def __repr__(self) -> str:
        """Return string representation showing the edge details.

        Returns
        -------
        str
            Formatted string showing governor, relation, and dependent.
        """
        return f"add_root({self.e.gov})_for_{self.e.rel}_from_({self.e.dep})"


class D(PredicateRootRule):
    """Extract a predicate token from the dependent of apposition."""

    rule_type = 'predicate_root'


class E(PredicateRootRule):
    """Extract a predicate token from the dependent of an adjectival modifier."""

    rule_type = 'predicate_root'


class V(PredicateRootRule):
    """Extract a predicate token from the dependent of 'nmod:poss' (English specific)."""

    rule_type = 'predicate_root'


class F(PredicateRootRule):
    """Extract a conjunct token of a predicate token."""

    rule_type = 'predicate_root'


# predicate conjunction resolution rules

class PredConjBorrowAuxNeg(PredConjRule):
    """Borrow aux and neg tokens from conjoined predicate's name."""

    def __init__(self, friend: Predicate, borrowed_token: Token) -> None:
        """Initialize with the friend predicate and borrowed token.

        Parameters
        ----------
        friend : Predicate
            The predicate we're borrowing from.
        borrowed_token : Token
            The aux or neg token being borrowed.
        """
        super().__init__()
        self.friend = friend
        self.borrowed_token = borrowed_token


class PredConjBorrowTokensXcomp(PredConjRule):
    """Borrow tokens from xcomp in a conjunction or predicates."""

    def __init__(self, friend: Predicate, borrowed_token: Token) -> None:
        """Initialize with the friend predicate and borrowed token.

        Parameters
        ----------
        friend : Predicate
            The predicate we're borrowing from.
        borrowed_token : Token
            The token being borrowed from xcomp.
        """
        super().__init__()
        self.friend = friend
        self.borrowed_token = borrowed_token


# predicate phrase building rules

class N1(PredPhraseRule):
    """Extract a token from the subtree of the predicate root token.

    Adds the token to the predicate phrase.
    """

    pass


class N2(PredPhraseRule):
    """Drop a token, which is an argument root token, from the predicate subtree."""

    pass


class N3(PredPhraseRule):
    """Drop a token, which is another predicate root token, from the predicate subtree."""

    pass


class N4(PredPhraseRule):
    """Drop a token which is a dependent of specific relations from the predicate subtree.

    Relations: {ccomp, csubj, advcl, acl, acl:relcl, nmod:tmod, parataxis, appos, dep}.
    """

    pass


class N5(PredPhraseRule):
    """Drop a conjunct token from the predicate subtree.

    Drops conjuncts of the predicate root token or conjuncts of a xcomp's dependent token.
    """

    pass


class N6(PredPhraseRule):
    """Add a case phrase to the predicate phrase."""

    pass


# simplification rules for predicates

class P1(SimplifyRule):
    """Remove a non-core argument, a nominal modifier, from the predpatt."""

    pass


class P2(SimplifyRule):
    """Remove an argument of other type from the predpatt."""

    pass


class Q(SimplifyRule):
    """Remove an adverbial modifier in the predicate phrase."""

    pass


class R(SimplifyRule):
    """Remove auxiliary in the predicate phrase."""

    pass


# utility rules

class U(SimplifyRule):
    """Strip the punct in the phrase."""

    pass


# english-specific rules

class EnRelclDummyArgFilter(EnglishSpecific):
    """Filter out dummy arguments in English relative clauses."""

    def __init__(self) -> None:
        """Initialize the English relative clause filter."""
        super().__init__()
