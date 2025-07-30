# pylint: disable=W0221
# pylint: disable=R0903
# pylint: disable=R1704
"""Corpus management for PredPatt semantic extractions.

This module provides functionality for loading and managing collections of
PredPatt semantic graphs from CoNLL-U format dependency corpora.

Key Components
--------------
:class:`PredPattCorpus`
    Container class extending the base Corpus for managing PredPatt semantic
    extractions paired with their dependency graphs
"""

from collections.abc import Hashable
from os.path import basename, splitext
from typing import TextIO, cast

from networkx import DiGraph

from ...corpus import Corpus
from ...syntax.dependency import CoNLLDependencyTreeCorpus
from .core.options import PredPattOpts
from .extraction.engine import PredPattEngine as PredPatt
from .graph import PredPattGraphBuilder
from .parsing.loader import load_conllu


class PredPattCorpus(Corpus[tuple[PredPatt, DiGraph], DiGraph]):
    """Container for managing collections of PredPatt semantic graphs.

    This class extends the base Corpus class to handle PredPatt extractions
    paired with their dependency graphs. It provides methods for loading
    corpora from CoNLL format and converting them to NetworkX graphs with
    semantic annotations.
    """

    def _graphbuilder(
        self,
        graphid: Hashable,
        predpatt_depgraph: tuple[PredPatt, DiGraph]
    ) -> DiGraph:
        """Build a unified graph from PredPatt extraction and dependency parse.

        Combines syntactic information from the dependency graph with semantic
        predicate-argument structures extracted by PredPatt into a single
        NetworkX graph representation.

        Parameters
        ----------
        graphid : Hashable
            Unique identifier for the graph, used as prefix for node IDs
        predpatt_depgraph : tuple[PredPatt, DiGraph]
            Tuple containing the PredPatt extraction and its source
            dependency graph

        Returns
        -------
        DiGraph
            NetworkX graph containing both syntactic and semantic layers
        """
        predpatt, depgraph = predpatt_depgraph

        return PredPattGraphBuilder.from_predpatt(predpatt, depgraph, str(graphid))

    @classmethod
    def from_conll(
        cls,
        corpus: str | TextIO,
        name: str = 'ewt',
        options: PredPattOpts | None = None
    ) -> 'PredPattCorpus':
        """Load a CoNLL-U dependency corpus and extract predicate-argument structures.

        Parses Universal Dependencies format data and applies PredPatt extraction
        rules to identify predicates and their arguments. Each sentence in the
        corpus is processed to create a semantic graph.

        Parameters
        ----------
        corpus : str | TextIO
            Path to a .conllu file, raw CoNLL-U formatted string, or open file handle
        name : str, optional
            Corpus name used as prefix for graph identifiers. Default is 'ewt'
        options : PredPattOpts | None, optional
            Configuration options for PredPatt extraction. If None, uses default
            options with relative clause resolution and argument borrowing enabled

        Returns
        -------
        PredPattCorpus
            Corpus containing PredPatt extractions and their graphs

        Raises
        ------
        ValueError
            If PredPatt cannot parse the provided CoNLL-U data, likely due to
            incompatible Universal Dependencies version
        """
        # Import here to avoid circular import
        from . import DEFAULT_PREDPATT_OPTIONS
        options = DEFAULT_PREDPATT_OPTIONS if options is None else options

        corp_is_str = isinstance(corpus, str)

        if corp_is_str and splitext(basename(cast(str, corpus)))[1] == '.conllu':
            with open(cast(str, corpus)) as infile:
                data = infile.read()

        elif corp_is_str:
            data = cast(str, corpus)

        else:
            data = cast(TextIO, corpus).read()

        # load the CoNLL dependency parses as graphs
        ud_corp_dict = {
            f"{name}-{i+1}": [
                line.split()
                for line in block.split('\n')
                if len(line) > 0
                if line[0] != '#'
            ]
            for i, block in enumerate(data.split('\n\n'))
        }
        ud_corp_hashable = {cast(Hashable, k): v for k, v in ud_corp_dict.items()}
        ud_corp = CoNLLDependencyTreeCorpus(ud_corp_hashable)

        # extract the predpatt for those dependency parses
        try:
            predpatt = {
                f"{name}-{sid.split('_')[1]}": PredPatt(ud_parse, opts=options)
                for sid, ud_parse in load_conllu(data)
            }

        except ValueError:
            errmsg = (
                "PredPatt was unable to parse the CoNLL you provided. "
                "This is likely due to using a version of UD that is "
                "incompatible with PredPatt. Use of version 1.2 is suggested."
            )

            raise ValueError(errmsg) from None

        return cls({
            n: (pp, ud_corp[n])
            for n, pp in predpatt.items()
        })
