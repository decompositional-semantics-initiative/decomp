"""Abstract base classes for graph corpus management.

This module provides the foundation for reading and managing collections of graphs
in the decomp framework. It defines abstract interfaces that are implemented by
concrete corpus readers for specific graph types.

The primary class is :class:`~decomp.corpus.Corpus`, which serves as a generic
container for managing collections of graphs. It handles the conversion from raw
input graphs to processed output graphs through an abstract graph builder method.

Classes
-------
Corpus
    Abstract base class for graph corpus containers that manages collections
    of graphs and provides dictionary-like access to them.

Type Aliases
------------
GraphDict
    Type alias for a dictionary mapping hashable identifiers to output graphs.

Type Variables
--------------
InGraph
    Type variable representing the input graph format that will be processed
    by the corpus reader's graph builder.

OutGraph
    Type variable representing the output graph format produced by the corpus
    reader after processing.

Notes
-----
The corpus module provides the foundation for various specialized corpus readers
in the decomp framework, including dependency syntax corpora and semantic graph
corpora like UDS and PredPatt.
"""

from .corpus import Corpus, GraphDict, InGraph, OutGraph


__all__ = ['Corpus', 'GraphDict', 'InGraph', 'OutGraph']
