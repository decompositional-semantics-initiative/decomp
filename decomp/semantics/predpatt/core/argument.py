"""Argument representation for predicate-argument structures.

This module provides the Argument class, which represents
arguments extracted from dependency parse trees in the PredPatt semantic
extraction system. Arguments are the participants in predicate-argument
structures, such as subjects, objects, and other dependents of predicates.

Arguments can be simple (single tokens) or complex (multi-token phrases),
and support operations like copying, creating references (for shared
arguments), and expanding coordinated structures.

Classes
-------
Argument
    The main class representing predicate arguments.

Functions
---------
sort_by_position
    Utility function for sorting items by position.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..typing import T
from ..utils.ud_schema import dep_v1
from .token import Token


if TYPE_CHECKING:
    from ..rules.base import Rule
    from ..typing import UDSchema


def sort_by_position(x: list[T]) -> list[T]:
    """Sort items by their position attribute."""
    return sorted(x, key=lambda y: y.position)


class Argument:
    """Represents an argument of a predicate.

    Arguments are extracted from dependency parse trees and represent
    the participants in predicate-argument structures.

    Parameters
    ----------
    root : Token
        The root token of the argument.
    ud : module, optional
        The Universal Dependencies module to use (default: dep_v1).
    rules : list, optional
        List of rules that led to this argument's extraction.

    Attributes
    ----------
    root : Token
        The root token of the argument.
    rules : list
        List of extraction rules applied.
    position : int
        Position of the root token (copied from root.position).
    ud : module
        The UD version module being used.
    tokens : list[Token]
        List of tokens forming the argument phrase.
    share : bool
        Whether this is a shared/borrowed argument (default: False).
    """

    def __init__(
        self,
        root: Token,
        ud: UDSchema = dep_v1,
        rules: list[Rule] | None = None,
        share: bool = False,
    ) -> None:
        """Initialize an Argument.

        Parameters
        ----------
        root : Token
            The root token of the argument.
        ud : module, optional
            The Universal Dependencies module to use.
        rules : list, optional
            List of rules that led to this argument's extraction.
            WARNING: Default is mutable list - modifying one argument's
            rules may affect others if default is used. This behavior
            is intentional to match the original PredPatt implementation.
        """
        # maintain exact initialization order as original
        self.root = root
        self.rules = rules if rules is not None else []
        self.position = root.position
        self.ud = ud
        self.tokens: list[Token] = []
        self.share = share
        self.type: str | None = None

    def __repr__(self) -> str:
        """Return string representation.

        Returns
        -------
        str
            String in format 'Argument(root)'.
        """
        return f"Argument({self.root})"

    def copy(self) -> Argument:
        """Create a copy of this argument.

        Creates a new Argument with the same root and copied lists
        for rules and tokens. The share flag is not copied.

        Returns
        -------
        Argument
            A new argument with copied rules and tokens lists.
        """
        x = Argument(self.root, self.ud, self.rules[:])
        x.tokens = self.tokens[:]
        return x

    def reference(self) -> Argument:
        """Create a reference (shared) copy of this argument.

        Creates a new Argument marked as shared (share=True) with
        the same tokens list (not copied). Used for borrowed arguments.

        Returns
        -------
        Argument
            A new argument with share=True and shared tokens list.
        """
        x = Argument(self.root, self.ud, self.rules[:])
        x.tokens = self.tokens  # share the same list
        x.share = True
        return x

    def is_reference(self) -> bool:
        """Check if this is a reference (shared) argument.

        Returns
        -------
        bool
            True if share attribute is True.
        """
        return self.share

    def isclausal(self) -> bool:
        """Check if this is a clausal argument.

        Clausal arguments are those with governor relations indicating
        embedded clauses: ccomp, csubj, csubjpass, or xcomp.

        Returns
        -------
        bool
            True if the argument root has a clausal governor relation.
        """
        return self.root.gov_rel in {self.ud.ccomp, self.ud.csubj,
                                     self.ud.csubjpass, self.ud.xcomp}

    def phrase(self) -> str:
        """Get the argument phrase.

        Joins the text of all tokens in the argument with spaces.
        The tokens are joined in the order they appear in the tokens list,
        which may be sorted by position during phrase extraction.

        Returns
        -------
        str
            Space-joined text of all tokens in the argument.
        """
        return " ".join(x.text for x in self.tokens)

    def coords(self) -> list[Argument]:
        """Get coordinated arguments including this one.

        Expands coordinated structures by finding conjunct dependents
        of the root token. Does not expand ccomp or csubj arguments.

        Returns
        -------
        list[Argument]
            List of arguments including self and any conjuncts,
            sorted by position.
        """
        # import here to avoid circular dependency
        from .. import rules as R  # noqa: N812

        coords = [self]
        # don't consider the conjuncts of ccomp, csubj and amod
        if self.root.gov_rel not in {self.ud.ccomp, self.ud.csubj}:
            if self.root.dependents is None:
                raise TypeError(
                    f"Cannot find coordinated arguments for argument {self}: "
                    f"root token has no dependency information",
                )
            for e in self.root.dependents:
                if e.rel == self.ud.conj:
                    coords.append(Argument(e.dep, self.ud, [R.m()]))
        return sort_by_position(coords)
