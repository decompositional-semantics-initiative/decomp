"""Argument extraction rules for PredPatt.

This module contains rules for identifying argument root tokens,
resolving missing arguments, and building argument phrases.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import (
    ArgumentRootRule,
    ArgumentResolution,
    ConjunctionResolution,
    ArgPhraseRule,
)

if TYPE_CHECKING:
    from ..core.token import Token
    from ..core.predicate import Predicate
    from ..core.argument import Argument
    from ..parsing.udparse import DepTriple


# argument root identification rules

class g1(ArgumentRootRule):
    """Extract an argument token from the dependent of the following relations {nsubj, nsubjpass, dobj, iobj}."""
    
    def __init__(self, edge: DepTriple) -> None:
        """Initialize with the dependency edge.
        
        Parameters
        ----------
        edge : DepTriple
            The dependency edge with a core argument relation.
        """
        self.edge = edge
        super().__init__()
    
    def __repr__(self) -> str:
        """Return string representation showing the relation.
        
        Returns
        -------
        str
            Formatted string showing the relation type.
        """
        return f'g1({self.edge.rel})'


class h1(ArgumentRootRule):
    """Extract an argument token, which directly depends on the predicate token, from the dependent of the relations {nmod, nmod:npmod, nmod:tmod}."""
    pass


class h2(ArgumentRootRule):
    """Extract an argument token, which indirectly depends on the predicate token, from the dependent of the relations {nmod, nmod:npmod, nmod:tmod}."""
    pass


class i(ArgumentRootRule):
    """Extract an argument token from the governor of an adjectival modifier."""
    pass


class j(ArgumentRootRule):
    """Extract an argument token from the governor of apposition."""
    pass


class w1(ArgumentRootRule):
    """Extract an argument token from the governor of 'nmod:poss' (English specific)."""
    pass


class w2(ArgumentRootRule):
    """Extract an argument token from the dependent of 'nmod:poss' (English specific)."""
    pass


class k(ArgumentRootRule):
    """Extract an argument token from the dependent of the dependent of clausal complement 'ccomp'."""
    pass


# argument resolution rules

class cut_borrow_other(ArgumentResolution):
    """Borrow an argument from another predicate in a cut structure."""
    
    def __init__(self, borrowed: Argument, friend: Predicate) -> None:
        """Initialize with the borrowed argument and friend predicate.
        
        Parameters
        ----------
        borrowed : Argument
            The argument being borrowed.
        friend : Predicate
            The predicate we're borrowing from.
        """
        super().__init__()
        self.friend = friend
        self.borrowed = borrowed


class cut_borrow_subj(ArgumentResolution):
    """Borrow subject from another predicate in a cut structure."""
    
    def __init__(self, subj: Argument, friend: Predicate) -> None:
        """Initialize with the subject argument and friend predicate.
        
        Parameters
        ----------
        subj : Argument
            The subject argument being borrowed.
        friend : Predicate
            The predicate we're borrowing from.
        """
        super().__init__()
        self.friend = friend
        self.subj = subj
    
    def __repr__(self) -> str:
        """Return string representation showing borrowing details.
        
        Returns
        -------
        str
            Formatted string showing what was borrowed from where.
        """
        return f'cut_borrow_subj({self.subj.root})_from({self.friend.root})'


class cut_borrow_obj(ArgumentResolution):
    """Borrow object from another predicate in a cut structure."""
    
    def __init__(self, obj: Argument, friend: Predicate) -> None:
        """Initialize with the object argument and friend predicate.
        
        Parameters
        ----------
        obj : Argument
            The object argument being borrowed.
        friend : Predicate
            The predicate we're borrowing from.
        """
        super().__init__()
        self.friend = friend
        self.obj = obj
    
    def __repr__(self) -> str:
        """Return string representation showing borrowing details.
        
        Returns
        -------
        str
            Formatted string showing what was borrowed from where.
        """
        return f'cut_borrow_obj({self.obj.root})_from({self.friend.root})'


class borrow_subj(ArgumentResolution):
    """Borrow subject from governor in (conj, xcomp of conj root, and advcl).
    
    if gov_rel=='conj' and missing a subject, try to borrow the subject from
    the other event. Still no subject. Try looking at xcomp of conjunction
    root.
    
    if gov_rel==advcl and not event.has_subj() then borrow from governor.
    """
    
    def __init__(self, subj: Argument, friend: Predicate) -> None:
        """Initialize with the subject argument and friend predicate.
        
        Parameters
        ----------
        subj : Argument
            The subject argument being borrowed.
        friend : Predicate
            The predicate we're borrowing from.
        """
        super().__init__()
        self.subj = subj
        self.friend = friend
    
    def __repr__(self) -> str:
        """Return string representation showing borrowing details.
        
        Returns
        -------
        str
            Formatted string showing what was borrowed from where.
        """
        return f'borrow_subj({self.subj.root})_from({self.friend.root})'


class borrow_obj(ArgumentResolution):
    """Borrow object from governor in (conj, xcomp of conj root, and advcl).
    
    if gov_rel=='conj' and missing a subject, try to borrow the subject from
    the other event. Still no subject. Try looking at xcomp of conjunction
    root.
    
    if gov_rel==advcl and not event.has_subj() then borrow from governor.
    """
    
    def __init__(self, obj: Argument, friend: Predicate) -> None:
        """Initialize with the object argument and friend predicate.
        
        Parameters
        ----------
        obj : Argument
            The object argument being borrowed.
        friend : Predicate
            The predicate we're borrowing from.
        """
        super().__init__()
        self.obj = obj
        self.friend = friend
    
    def __repr__(self) -> str:
        """Return string representation showing borrowing details.
        
        Returns
        -------
        str
            Formatted string showing what was borrowed from where.
        """
        return f'borrow_obj({self.obj.root})_from({self.friend.root})'


class share_argument(ArgumentResolution):
    """Create an argument sharing tokens with another argument."""
    pass


class arg_resolve_relcl(ArgumentResolution):
    """Resolve argument of a predicate inside a relative clause.
    
    The missing argument that we take is rooted at the governor of the `acl`
    dependency relation (type acl:*) pointing at the embedded predicate.
    """
    pass


class pred_resolve_relcl(ArgumentResolution):
    """Predicate has an argument from relcl resolution (`arg_resolve_relcl`)."""
    pass


# rules for post added argument root token

class l(ArgumentResolution):
    """Merge the argument token set of xcomp's dependent to the argument token set of the real predicate token."""
    pass


class m(ConjunctionResolution):
    """Extract a conjunct token of the argument root token."""
    pass


# argument phrase building rules

class clean_arg_token(ArgPhraseRule):
    """Extract a token from the subtree of the argument root token, and add it to the argument phrase."""
    
    def __init__(self, x: Token) -> None:
        """Initialize with the token to include.
        
        Parameters
        ----------
        x : Token
            The token to add to the argument phrase.
        """
        super().__init__()
        self.x = x
    
    def __repr__(self) -> str:
        """Return string representation showing the token.
        
        Returns
        -------
        str
            Formatted string showing which token is included.
        """
        return f"clean_arg_token({self.x})"


class move_case_token_to_pred(ArgPhraseRule):
    """Extract a case token from the subtree of the argument root token."""
    
    def __init__(self, x: Token) -> None:
        """Initialize with the case token to move.
        
        Parameters
        ----------
        x : Token
            The case token to move to predicate.
        """
        super().__init__()
        self.x = x
    
    def __repr__(self) -> str:
        """Return string representation showing the token.
        
        Returns
        -------
        str
            Formatted string showing which token is moved.
        """
        return f"move_case_token({self.x})_to_pred"


class predicate_has(ArgPhraseRule):
    """Drop a token, which is a predicate root token, from the subtree of the argument root token."""
    
    def __init__(self, x: Token) -> None:
        """Initialize with the predicate token to drop.
        
        Parameters
        ----------
        x : Token
            The predicate token to exclude.
        """
        super().__init__()
        self.x = x
    
    def __repr__(self) -> str:
        """Return string representation showing the token.
        
        Returns
        -------
        str
            Formatted string showing which token is dropped.
        """
        return f"predicate_has({self.x})"


class drop_appos(ArgPhraseRule):
    """Drop apposition from argument phrase."""
    
    def __init__(self, x: Token) -> None:
        """Initialize with the apposition token to drop.
        
        Parameters
        ----------
        x : Token
            The apposition token to exclude.
        """
        super().__init__()
        self.x = x
    
    def __repr__(self) -> str:
        """Return string representation showing the token.
        
        Returns
        -------
        str
            Formatted string showing which token is dropped.
        """
        return f"drop_appos({self.x})"


class drop_unknown(ArgPhraseRule):
    """Drop unknown dependency from argument phrase."""
    
    def __init__(self, x: Token) -> None:
        """Initialize with the unknown token to drop.
        
        Parameters
        ----------
        x : Token
            The unknown token to exclude.
        """
        super().__init__()
        self.x = x
    
    def __repr__(self) -> str:
        """Return string representation showing the token.
        
        Returns
        -------
        str
            Formatted string showing which token is dropped.
        """
        return f"drop_unknown({self.x})"


class drop_cc(ArgPhraseRule):
    """Drop the argument's cc (coordinating conjunction) from the subtree of the argument root token."""
    
    def __init__(self, x: Token) -> None:
        """Initialize with the cc token to drop.
        
        Parameters
        ----------
        x : Token
            The coordinating conjunction token to exclude.
        """
        super().__init__()
        self.x = x
    
    def __repr__(self) -> str:
        """Return string representation showing the token.
        
        Returns
        -------
        str
            Formatted string showing which token is dropped.
        """
        return f"drop_cc({self.x})"


class drop_conj(ArgPhraseRule):
    """Drop the argument's conjuct from the subtree of the argument root token."""
    
    def __init__(self, x: Token) -> None:
        """Initialize with the conjunct token to drop.
        
        Parameters
        ----------
        x : Token
            The conjunct token to exclude.
        """
        super().__init__()
        self.x = x
    
    def __repr__(self) -> str:
        """Return string representation showing the token.
        
        Returns
        -------
        str
            Formatted string showing which token is dropped.
        """
        return f"drop_conj({self.x})"


class special_arg_drop_direct_dep(ArgPhraseRule):
    """Drop special direct dependencies from argument phrase."""
    
    def __init__(self, x: Token) -> None:
        """Initialize with the token to drop.
        
        Parameters
        ----------
        x : Token
            The token to exclude.
        """
        super().__init__()
        self.x = x
    
    def __repr__(self) -> str:
        """Return string representation showing the token.
        
        Returns
        -------
        str
            Formatted string showing which token is dropped.
        """
        return f"special_arg_drop_direct_dep({self.x})"


class embedded_advcl(ArgPhraseRule):
    """Drop embedded adverbial clause from argument phrase."""
    
    def __init__(self, x: Token) -> None:
        """Initialize with the advcl token to drop.
        
        Parameters
        ----------
        x : Token
            The adverbial clause token to exclude.
        """
        super().__init__()
        self.x = x
    
    def __repr__(self) -> str:
        """Return string representation showing the token.
        
        Returns
        -------
        str
            Formatted string showing which token is dropped.
        """
        return f"drop_embedded_advcl({self.x})"


class embedded_ccomp(ArgPhraseRule):
    """Drop embedded clausal complement from argument phrase."""
    
    def __init__(self, x: Token) -> None:
        """Initialize with the ccomp token to drop.
        
        Parameters
        ----------
        x : Token
            The clausal complement token to exclude.
        """
        super().__init__()
        self.x = x
    
    def __repr__(self) -> str:
        """Return string representation showing the token.
        
        Returns
        -------
        str
            Formatted string showing which token is dropped.
        """
        return f"drop_embedded_ccomp({self.x})"


class embedded_unknown(ArgPhraseRule):
    """Drop embedded unknown structure from argument phrase."""
    
    def __init__(self, x: Token) -> None:
        """Initialize with the unknown token to drop.
        
        Parameters
        ----------
        x : Token
            The unknown embedded token to exclude.
        """
        super().__init__()
        self.x = x
    
    def __repr__(self) -> str:
        """Return string representation showing the token.
        
        Returns
        -------
        str
            Formatted string showing which token is dropped.
        """
        return f"drop_embedded_unknown({self.x})"