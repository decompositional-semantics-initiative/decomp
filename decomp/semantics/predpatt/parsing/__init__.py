"""Dependency parsing structures and loaders for PredPatt.

This module provides data structures and functions for working with
Universal Dependencies parses that serve as input to the PredPatt
semantic extraction system.

Classes
-------
DepTriple
    Named tuple representing a single dependency relation.
UDParse
    Container for dependency parse trees with tokens and relations.

Functions
---------
load_conllu
    Load dependency parses from CoNLL-U format files.
"""

from .loader import load_conllu
from .udparse import DepTriple, UDParse


__all__ = ["DepTriple", "UDParse", "load_conllu"]
