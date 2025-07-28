"""
Parsing module for PredPatt with modern Python implementation.

This module contains the dependency parsing data structures used by PredPatt
for representing parsed sentences and their dependency relations.
"""

from .loader import load_conllu
from .udparse import DepTriple, UDParse


__all__ = ["DepTriple", "UDParse", "load_conllu"]
