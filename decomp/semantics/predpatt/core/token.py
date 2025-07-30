"""Token representation for dependency parsing in PredPatt.

This module defines the core :class:`Token` class that represents individual
tokens (words) in a dependency parse tree. Tokens store linguistic information
including text, part-of-speech tags, and dependency relations.

Key Components
--------------
:class:`Token`
    Represents a single token with its linguistic properties and dependency
    relations. Used as the basic unit in dependency parsing for predicate-argument
    extraction.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..utils.ud_schema import dep_v1, postag


if TYPE_CHECKING:
    from ..parsing.udparse import DepTriple
    from ..typing import UDSchema


class Token:
    """Represents a single token in a dependency parse.

    Attributes
    ----------
    position : int
        The position of the token in the sentence (0-based).
    text : str
        The text content of the token.
    tag : str
        The part-of-speech tag of the token.
    dependents : list[DepTriple] | None
        List of dependent edges where this token is the governor.
        Initially set to None.
    gov : Token | None
        The governing token (parent) in the dependency tree.
        Initially set to None.
    gov_rel : str | None
        The dependency relation to the governing token.
        Initially set to None.
    ud : UDSchema
        The Universal Dependencies module (dep_v1 or dep_v2) that defines
        relation types and constants.
    """

    def __init__(self, position: int, text: str, tag: str, ud: UDSchema = dep_v1) -> None:
        """Initialize a Token.

        Parameters
        ----------
        position : int
            The position of the token in the sentence (0-based).
        text : str
            The text content of the token.
        tag : str
            The part-of-speech tag of the token.
        ud : UDSchema, optional
            The Universal Dependencies module, by default dep_v1.
        """
        # maintain exact initialization order
        self.position: int = position
        self.text: str = text
        self.tag: str = tag
        self.dependents: list[DepTriple] | None = None
        self.gov: Token | None = None
        self.gov_rel: str | None = None
        self.ud: UDSchema = ud

    def __repr__(self) -> str:
        """Return string representation of the token.

        Returns
        -------
        str
            String in format 'text/position'.
        """
        return f'{self.text}/{self.position}'

    @property
    def isword(self) -> bool:
        """Check if the token is not punctuation.

        Returns
        -------
        bool
            True if the token is not punctuation, False otherwise.
        """
        return self.tag != postag.PUNCT

    def argument_like(self) -> bool:
        """Check if this token looks like the root of an argument.

        Returns
        -------
        bool
            True if the token's gov_rel is in ARG_LIKE relations.
        """
        return self.gov_rel in self.ud.ARG_LIKE

    def hard_to_find_arguments(self) -> bool:
        """Check if this is potentially the root of a predicate with hard-to-find arguments.

        This func is only called when one of its dependents is an easy
        predicate. Here, we're checking:
        Is this potentially the root of an easy predicate, which will have an
        argment?

        Returns
        -------
        bool
            True if this could be a predicate root with hard-to-find arguments.
        """
        # amod:
        # there is nothing wrong with a negotiation,
        # but nothing helpful about generating one that is just for show .
        #        ^      ^              ^
        #        --amod--       (a easy predicate, dependent of "helpful"
        #                       which is hard_to_find_arguments)
        if self.dependents is None:
            raise TypeError(
                f"Cannot iterate over None dependents for token '{self.text}' "
                f"at position {self.position}. Token not properly initialized "
                f"with dependency information."
            )

        for e in self.dependents:
            if e.rel in self.ud.SUBJ or e.rel in self.ud.OBJ:
                return False

        return self.gov_rel in self.ud.HARD_TO_FIND_ARGS
