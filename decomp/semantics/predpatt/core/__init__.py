"""
Core PredPatt classes with modern Python implementation.

This module contains the core data structures used by PredPatt for
representing tokens, predicates, and arguments in dependency parses.
"""

from .argument import Argument, sort_by_position
from .options import PredPattOpts
from .predicate import AMOD, APPOS, NORMAL, POSS, Predicate, argument_names, no_color
from .token import Token


__all__ = [
    "AMOD",
    "APPOS",
    "NORMAL",
    "POSS",
    "Argument",
    "PredPattOpts",
    "Predicate",
    "Token",
    "argument_names",
    "no_color",
    "sort_by_position"
]
