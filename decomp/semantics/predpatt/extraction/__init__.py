"""Core extraction engine for PredPatt semantic structures.

This module contains the main extraction engine that orchestrates the
application of linguistic rules to extract predicate-argument structures
from Universal Dependencies parses.

Classes
-------
PredPattEngine
    Main engine for extracting predicates and arguments from dependency parses.

See Also
--------
decomp.semantics.predpatt.rules : Linguistic rules used by the engine
decomp.semantics.predpatt.filters : Filters for refining extractions
"""

from __future__ import annotations

from .engine import PredPattEngine


__all__ = ["PredPattEngine"]
