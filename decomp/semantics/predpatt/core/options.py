"""Options configuration for PredPatt extraction.

This module contains the PredPattOpts class which configures the behavior
of predicate-argument extraction in the PredPatt system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    pass


class PredPattOpts:
    """Configuration options for PredPatt extraction.

    Controls various aspects of predicate-argument extraction including
    simplification, resolution of special constructions, and formatting.

    Parameters
    ----------
    simple : bool, optional
        Extract simple predicates (exclude aux and advmod). Default: False.
    cut : bool, optional
        Cut: treat xcomp as independent predicate. Default: False.
    resolve_relcl : bool, optional
        Resolve relative clause modifiers. Default: False.
    resolve_appos : bool, optional
        Resolve appositives. Default: False.
    resolve_amod : bool, optional
        Resolve adjectival modifiers. Default: False.
    resolve_conj : bool, optional
        Resolve conjunctions. Default: False.
    resolve_poss : bool, optional
        Resolve possessives. Default: False.
    borrow_arg_for_relcl : bool, optional
        Borrow arguments for relative clauses. Default: True.
    big_args : bool, optional
        Use big argument extraction (include all subtree tokens). Default: False.
    strip : bool, optional
        Strip leading/trailing punctuation from phrases. Default: True.
    ud : str, optional
        Universal Dependencies version ("1.0" or "2.0"). Default: "1.0".

    Attributes
    ----------
    simple : bool
        Extract simple predicates (exclude aux and advmod).
    cut : bool
        Cut: treat xcomp as independent predicate.
    resolve_relcl : bool
        Resolve relative clause modifiers.
    resolve_appos : bool
        Resolve appositives.
    resolve_amod : bool
        Resolve adjectival modifiers.
    resolve_conj : bool
        Resolve conjunctions.
    resolve_poss : bool
        Resolve possessives.
    borrow_arg_for_relcl : bool
        Borrow arguments for relative clauses.
    big_args : bool
        Use big argument extraction.
    strip : bool
        Strip leading/trailing punctuation.
    ud : str
        Universal Dependencies version string.
    """

    def __init__(
        self,
        simple: bool = False,
        cut: bool = False,
        resolve_relcl: bool = False,
        resolve_appos: bool = False,
        resolve_amod: bool = False,
        resolve_conj: bool = False,
        resolve_poss: bool = False,
        borrow_arg_for_relcl: bool = True,
        big_args: bool = False,
        strip: bool = True,
        ud: str = "1.0"  # dep_v1.VERSION
    ) -> None:
        """Initialize PredPattOpts with configuration values.

        Parameters are assigned in the exact same order as the original
        to ensure identical behavior and initialization.
        """
        # maintain exact initialization order as original
        self.simple = simple
        self.cut = cut
        self.resolve_relcl = resolve_relcl
        self.resolve_appos = resolve_appos
        self.resolve_amod = resolve_amod
        self.resolve_poss = resolve_poss
        self.resolve_conj = resolve_conj
        self.big_args = big_args
        self.strip = strip
        self.borrow_arg_for_relcl = borrow_arg_for_relcl

        # validation logic - must be exactly "1.0" or "2.0"
        assert str(ud) in {"1.0", "2.0"}, (
            f'the ud version "{ud!s}" is not in {{"1.0", "2.0"}}')
        self.ud = str(ud)
