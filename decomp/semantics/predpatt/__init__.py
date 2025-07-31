"""PredPatt predicate-argument structure extraction module.

This module provides functionality for extracting predicate-argument structures
from Universal Dependencies parses using the PredPatt framework. It identifies
verbal predicates and their arguments through linguistic rules applied to
dependency parse trees.

The extracted semantic structures can be integrated with the Universal
Decompositional Semantics (UDS) framework for further annotation.

.. note::
   Automatic parsing functionality (from_sentence, from_constituency) is a planned
   future feature. Currently, you must provide pre-parsed Universal Dependencies
   data using load_conllu() or similar methods. To prepare for future parsing
   features, install with: ``pip install decomp[parsing]``

Classes
-------
Argument
    Represents an argument of a predicate with its token span.
Predicate
    Represents a predicate with its arguments and type.
Token
    Represents a single token in a dependency parse.
PredPattOpts
    Configuration options for controlling extraction behavior.
PredPatt
    Main extraction engine (alias for PredPattEngine).
PredPattCorpus
    Container for collections of PredPatt extractions.
PredPattGraphBuilder
    Converts PredPatt extractions to NetworkX graphs.

Functions
---------
load_conllu
    Load dependency parses from CoNLL-U format files.
load_comm
    Load dependency parses from Concrete communications.

Constants
---------
DEFAULT_PREDPATT_OPTIONS
    Default configuration with relative clause resolution enabled.
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


