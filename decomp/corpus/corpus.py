"""Module for defining abstract graph corpus readers"""

from abc import ABCMeta, abstractmethod

from random import sample
from logging import warning
from typing import Dict, List, Tuple, Iterable, Hashable, Any, TypeVar

InGraph = TypeVar('InGraph')  # the input graph type
OutGraph = TypeVar('OutGraph')  # the output graph type


class Corpus(metaclass=ABCMeta):
    """Container for graphs

    Parameters
    ----------
    graphs_raw
        a sequence of graphs in a format that the graphbuilder for a
        subclass of this abstract class can process
    """

    def __init__(self, graphs_raw: Iterable[InGraph]):
        self._graphs_raw = graphs_raw
        self._build_graphs()

    def __iter__(self) -> Iterable[Hashable]:
        return iter(self._graphs)

    def items(self) -> Iterable[Tuple[Hashable, OutGraph]]:
        """Dictionary-like iterator for (graphid, graph) pairs"""
        return self._graphs.items()

    def __getitem__(self, k: Hashable) -> Any:
        return self._graphs[k]

    def __contains__(self, k: Hashable) -> bool:
        return k in self._graphs

    def __len__(self) -> int:
        return len(self._graphs)

    def _build_graphs(self) -> None:
        self._graphs = {}

        for graphid, rawgraph in self._graphs_raw.items():
            try:
                self._graphs[graphid] = self._graphbuilder(graphid, rawgraph)
            except ValueError:
                warning(graphid+' has no or multiple root nodes')
            except RecursionError:
                warning(graphid+' has loops')

    @abstractmethod
    def _graphbuilder(self,
                      graphid: Hashable,
                      rawgraph: InGraph) -> OutGraph:
        raise NotImplementedError

    @property
    def graphs(self) -> Dict[Hashable, OutGraph]:
        """the graphs in corpus"""
        return self._graphs

    @property
    def graphids(self) -> List[Hashable]:
        """The graph ids in corpus"""

        return list(self._graphs)

    @property
    def ngraphs(self) -> int:
        """Number of graphs in corpus"""

        return len(self._graphs)

    def sample(self, k: int) -> Dict[Hashable, OutGraph]:
        """Sample k graphs without replacement

        Parameters
        ----------
        k
            the number of graphs to sample
        """
        
        return {tid: self._graphs[tid]
                for tid
                in sample(self._graphs.keys(), k=k)}
