"""Abstract base class for graph corpus readers.

This module provides the foundational :class:`Corpus` class for managing collections
of graphs in the decomp framework. The Corpus class serves as an abstract base that
concrete corpus implementations extend to handle specific graph formats.

The module defines a generic corpus container that:
- Accepts raw graphs in an input format
- Transforms them to an output format via an abstract graph builder
- Provides dictionary-like access to the processed graphs
- Handles errors during graph construction gracefully

Type Variables
--------------
InGraph
    The input graph type that will be processed by the corpus reader.

OutGraph
    The output graph type produced after processing.

Type Aliases
------------
GraphDict[T]
    Generic dictionary mapping hashable identifiers to graphs of type T.

Classes
-------
Corpus
    Abstract base class for graph corpus containers with generic type parameters
    for input and output graph formats.
"""

from abc import ABCMeta, abstractmethod
from collections.abc import Hashable, ItemsView, Iterator
from logging import warning
from random import sample
from typing import TypeVar


InGraph = TypeVar('InGraph')  # the input graph type
OutGraph = TypeVar('OutGraph')  # the output graph type

type GraphDict[T] = dict[Hashable, T]


class Corpus[InGraph, OutGraph](metaclass=ABCMeta):
    """Container for graphs.

    Parameters
    ----------
    graphs_raw
        A sequence of graphs in a format that the graphbuilder for a
        subclass of this abstract class can process.
    """

    def __init__(self, graphs_raw: dict[Hashable, InGraph]):
        self._graphs_raw = graphs_raw
        self._graphs: dict[Hashable, OutGraph] = {}
        self._build_graphs()

    def __iter__(self) -> Iterator[Hashable]:
        return iter(self._graphs)

    def items(self) -> ItemsView[Hashable, OutGraph]:
        """Dictionary-like iterator for (graphid, graph) pairs."""
        return self._graphs.items()

    def __getitem__(self, k: Hashable) -> OutGraph:
        return self._graphs[k]

    def __contains__(self, k: Hashable) -> bool:
        return k in self._graphs

    def __len__(self) -> int:
        return len(self._graphs)

    def _build_graphs(self) -> None:
        for graphid, rawgraph in self._graphs_raw.items():
            try:
                self._graphs[graphid] = self._graphbuilder(graphid, rawgraph)

            except ValueError:
                warning(f'{graphid} has no or multiple root nodes')

            except RecursionError:
                warning(f'{graphid} has loops')

    @abstractmethod
    def _graphbuilder(
        self,
        graphid: Hashable,
        rawgraph: InGraph
    ) -> OutGraph:
        raise NotImplementedError

    @property
    def graphs(self) -> dict[Hashable, OutGraph]:
        """The graphs in corpus."""
        return self._graphs

    @property
    def graphids(self) -> list[Hashable]:
        """The graph ids in corpus."""
        return list(self._graphs)

    @property
    def ngraphs(self) -> int:
        """Number of graphs in corpus."""
        return len(self._graphs)

    def sample(self, k: int) -> dict[Hashable, OutGraph]:
        """Sample k graphs without replacement.

        Parameters
        ----------
        k
            the number of graphs to sample
        """
        sampled_keys = sample(list(self._graphs.keys()), k=k)
        return {tid: self._graphs[tid] for tid in sampled_keys}
