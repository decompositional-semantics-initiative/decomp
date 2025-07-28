"""Module for defining abstract graph corpus readers"""

from abc import ABCMeta, abstractmethod
from collections.abc import Hashable, Iterator
from logging import warning
from random import sample
from typing import Generic, TypeAlias, TypeVar


InGraph = TypeVar('InGraph')  # the input graph type
OutGraph = TypeVar('OutGraph')  # the output graph type

GraphDict: TypeAlias = dict[Hashable, OutGraph]


class Corpus(Generic[InGraph, OutGraph], metaclass=ABCMeta):
    """Container for graphs

    Parameters
    ----------
    graphs_raw
        a sequence of graphs in a format that the graphbuilder for a
        subclass of this abstract class can process
    """

    def __init__(self, graphs_raw: dict[Hashable, InGraph]):
        self._graphs_raw = graphs_raw
        self._graphs: dict[Hashable, OutGraph] = {}
        self._build_graphs()

    def __iter__(self) -> Iterator[Hashable]:
        return iter(self._graphs)

    def items(self) -> Iterator[tuple[Hashable, OutGraph]]:
        """Dictionary-like iterator for (graphid, graph) pairs"""
        return iter(self._graphs.items())

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
                warning(str(graphid)+' has no or multiple root nodes')
            except RecursionError:
                warning(str(graphid)+' has loops')

    @abstractmethod
    def _graphbuilder(self,
                      graphid: Hashable,
                      rawgraph: InGraph) -> OutGraph:
        raise NotImplementedError

    @property
    def graphs(self) -> dict[Hashable, OutGraph]:
        """The graphs in corpus"""
        return self._graphs

    @property
    def graphids(self) -> list[Hashable]:
        """The graph ids in corpus"""
        return list(self._graphs)

    @property
    def ngraphs(self) -> int:
        """Number of graphs in corpus"""
        return len(self._graphs)

    def sample(self, k: int) -> dict[Hashable, OutGraph]:
        """Sample k graphs without replacement

        Parameters
        ----------
        k
            the number of graphs to sample
        """
        sampled_keys = sample(list(self._graphs.keys()), k=k)
        return {tid: self._graphs[tid] for tid in sampled_keys}
