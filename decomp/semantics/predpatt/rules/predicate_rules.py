"""Predicate extraction rules for PredPatt.

This module contains rules for identifying predicate root tokens,
building predicate phrases, and handling predicate-specific phenomena.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import (
    PredicateRootRule,
    PredConjRule,
    PredPhraseRule,
    SimplifyRule,
    EnglishSpecific,
)

if TYPE_CHECKING:
    from ..core.token import Token
    from ..core.predicate import Predicate
    from ..parsing.udparse import DepTriple


# predicate root identification rules

class a1(PredicateRootRule):
    """Extract a predicate token from the dependent of clausal relation {ccomp, csub, csubjpass}."""
    
    rule_type = 'predicate_root'


class a2(PredicateRootRule):
    """Extract a predicate token from the dependent of clausal complement 'xcomp'."""
    
    rule_type = 'predicate_root'


class b(PredicateRootRule):
    """Extract a predicate token from the dependent of clausal modifier."""
    
    rule_type = 'predicate_root'


class c(PredicateRootRule):
    """Extract a predicate token from the governor of the relations {nsubj, nsubjpass, dobj, iobj, ccomp, xcomp, advcl}."""
    
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


class d(PredicateRootRule):
    """Extract a predicate token from the dependent of apposition."""
    
    rule_type = 'predicate_root'


class e(PredicateRootRule):
    """Extract a predicate token from the dependent of an adjectival modifier."""
    
    rule_type = 'predicate_root'


class v(PredicateRootRule):
    """Extract a predicate token from the dependent of the possessive relation 'nmod:poss' (English specific)."""
    
    rule_type = 'predicate_root'


class f(PredicateRootRule):
    """Extract a conjunct token of a predicate token."""
    
    rule_type = 'predicate_root'


# predicate conjunction resolution rules

class pred_conj_borrow_aux_neg(PredConjRule):
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


class pred_conj_borrow_tokens_xcomp(PredConjRule):
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

class n1(PredPhraseRule):
    """Extract a token from the subtree of the predicate root token, and add it to the predicate phrase."""
    pass


class n2(PredPhraseRule):
    """Drop a token, which is an argument root token, from the subtree of the predicate root token."""
    pass


class n3(PredPhraseRule):
    """Drop a token, which is another predicate root token, from the subtree of the predicate root token."""
    pass


class n4(PredPhraseRule):
    """Drop a token, which is the dependent of the relations set {ccomp, csubj, advcl, acl, acl:relcl, nmod:tmod, parataxis, appos, dep}, from the subtree of the predicate root token."""
    pass


class n5(PredPhraseRule):
    """Drop a token, which is a conjunct of the predicate root token or a conjunct of a xcomp's dependent token, from the subtree of the predicate root token."""
    pass


class n6(PredPhraseRule):
    """Add a case phrase to the predicate phrase."""
    pass


# simplification rules for predicates

class p1(SimplifyRule):
    """Remove a non-core argument, a nominal modifier, from the predpatt."""
    pass


class p2(SimplifyRule):
    """Remove an argument of other type from the predpatt."""
    pass


class q(SimplifyRule):
    """Remove an adverbial modifier in the predicate phrase."""
    pass


class r(SimplifyRule):
    """Remove auxiliary in the predicate phrase."""
    pass


# utility rules

class u(SimplifyRule):
    """Strip the punct in the phrase."""
    pass


# english-specific rules

class en_relcl_dummy_arg_filter(EnglishSpecific):
    """Filter out dummy arguments in English relative clauses."""
    
    def __init__(self) -> None:
        """Initialize the English relative clause filter."""
        super().__init__()