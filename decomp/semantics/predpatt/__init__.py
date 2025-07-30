# pylint: disable=W0221
# pylint: disable=R0903
# pylint: disable=R1704
"""PredPatt semantic role labeling module.

This module provides functionality for extracting predicate-argument structures
from Universal Dependencies parses using the PredPatt framework. It identifies
verbal predicates and their arguments through linguistic rules applied to
dependency parse trees.

Key Components
--------------
:class:`PredPattCorpus`
    Container class for managing collections of PredPatt semantic extractions
    paired with their dependency graphs. See :mod:`decomp.semantics.predpatt.corpus`

:class:`PredPattGraphBuilder`
    Static methods for converting PredPatt extractions into unified NetworkX
    graphs containing both syntactic and semantic information.
    See :mod:`decomp.semantics.predpatt.graph`

:data:`DEFAULT_PREDPATT_OPTIONS`
    Default configuration options for PredPatt extraction with relative clause
    resolution and argument borrowing enabled

The extracted semantic structures can be integrated with the Universal
Decompositional Semantics (UDS) framework for further annotation.
"""

from .core.argument import Argument
from .core.options import PredPattOpts
from .core.predicate import Predicate
from .core.token import Token
from .corpus import PredPattCorpus
from .extraction.engine import PredPattEngine as PredPatt
from .graph import PredPattGraphBuilder
from .parsing.loader import load_comm, load_conllu


__all__ = [
    'DEFAULT_PREDPATT_OPTIONS',
    'Argument',
    'PredPatt',
    'PredPattCorpus',
    'PredPattGraphBuilder',
    'PredPattOpts',
    'Predicate',
    'Token',
    'load_comm',
    'load_conllu',
]


DEFAULT_PREDPATT_OPTIONS = PredPattOpts(
    resolve_relcl=True,
    borrow_arg_for_relcl=True,
    resolve_conj=False,
    cut=True
)  # resolve relative clause


