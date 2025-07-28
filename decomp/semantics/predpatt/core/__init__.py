"""
Core PredPatt classes with modern Python implementation.

This module contains the core data structures used by PredPatt for
representing tokens, predicates, and arguments in dependency parses.
"""

from .argument import Argument, sort_by_position
from .options import PredPattOpts
from .predicate import Predicate, NORMAL, POSS, APPOS, AMOD, argument_names, no_color
from .token import Token

__all__ = [
    "Token", 
    "Predicate", 
    "Argument",
    "PredPattOpts",
    "NORMAL", 
    "POSS", 
    "APPOS", 
    "AMOD",
    "argument_names",
    "no_color",
    "sort_by_position"
]