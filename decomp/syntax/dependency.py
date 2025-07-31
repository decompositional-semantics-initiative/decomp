# pylint: disable=R1717
# pylint: disable=R0903
"""Module for building and containing dependency trees from CoNLL format.

This module provides functionality to parse CoNLL-U and CoNLL-X formatted
dependency parse data and convert it into NetworkX DiGraph structures for
further processing within the decomp package.

Classes
-------
CoNLLDependencyTreeCorpus
    Corpus containing dependency trees built from CoNLL data.
DependencyGraphBuilder
    Builder class for constructing dependency graphs from CoNLL format.

Type Aliases
------------
ConllRow
    Type alias for a single row of CoNLL data as a list of strings.
ConllData
    Type alias for complete CoNLL data as a list of ConllRow entries.

Constants
---------
CONLL_HEAD
    Column headers for CoNLL-U ('u') and CoNLL-X ('x') formats.
CONLL_NODE_ATTRS
    Node attribute mappings for different CoNLL format versions.
CONLL_EDGE_ATTRS
    Edge attribute mappings for different CoNLL format versions.
"""

from __future__ import annotations

from collections.abc import Hashable

from networkx import DiGraph
from numpy import array

from ..corpus import Corpus


type ConllRow = list[str]
type ConllData = list[ConllRow]

CONLL_HEAD = {'u': ['id', 'form', 'lemma', 'upos', 'xpos',
                    'feats', 'head', 'deprel', 'deps', 'misc'],
              'x': ['id', 'form', 'lemma', 'cpostag', 'postag',
                    'feats', 'head', 'deprel', 'phead', 'pdeprel']}

CONLL_NODE_ATTRS = {'u': {k: CONLL_HEAD['u'].index(k)
                          for k in ['form', 'lemma', 'upos', 'xpos', 'feats']},
                    'x': {k: CONLL_HEAD['x'].index(k)
                          for k in ['form', 'lemma', 'cpostag',
                                    'postag', 'feats']}}

CONLL_EDGE_ATTRS = {'u': {k: CONLL_HEAD['u'].index(k)
                          for k in ['deprel']},
                    'x': {k: CONLL_HEAD['x'].index(k)
                          for k in ['deprel']}}


class CoNLLDependencyTreeCorpus(Corpus[ConllData, DiGraph]):
    """Class for building/containing dependency trees from CoNLL-U.

    Attributes
    ----------
    graphs
        trees constructed from annotated sentences
    graphids
        ids for trees constructed from annotated sentences
    ngraphs
        number of graphs in corpus
    """

    def _graphbuilder(self, graphid: Hashable, rawgraph: ConllData) -> DiGraph:
        return DependencyGraphBuilder.from_conll(rawgraph, str(graphid))


class DependencyGraphBuilder:
    """A dependency graph builder."""

    @classmethod
    def from_conll(cls,
                   conll: ConllData,
                   treeid: str='',
                   spec: str='u') -> DiGraph:
        """Build DiGraph from a CoNLL representation.

        Parameters
        ----------
        conll
            conll representation
        treeid
            a unique identifier for the tree
        spec
            the specification to assume of the conll representation
            ("u" or "x")
        """
        # handle null treeids
        treeid = treeid+'-' if treeid else ''

        # initialize the dependency graph
        depgraph = DiGraph(conll=array(conll))
        depgraph.name = treeid.strip('-')

        # populate graph with nodes
        depgraph.add_nodes_from([cls._conll_node_attrs(treeid, row, spec)
                                 for row in conll])

        # add the root
        depgraph.add_node(treeid+'root-0',
                          position=0,
                          domain='root',
                          type='root')

        # connect nodes
        depgraph.add_edges_from([cls._conll_edge_attrs(treeid, row, spec)
                                 for row in conll])

        return depgraph

    @staticmethod
    def _conll_node_attrs(
        treeid: str, row: ConllRow, spec: str
    ) -> tuple[str, dict[str, str | int]]:
        node_id = row[0]

        node_attrs: dict[str, str | int] = {'domain': 'syntax',
                                            'type': 'token',
                                            'position': int(node_id)}
        other_attrs: dict[str, str] = {}

        for attr, idx in CONLL_NODE_ATTRS[spec].items():
            # convert features into a dictionary
            if attr == 'feats':
                if row[idx] != '_':
                    feat_split = row[idx].split('|')
                    other_attrs = dict([kv.split('=')
                                        for kv in feat_split])

            else:
                node_attrs[attr] = row[idx]

        node_attrs = dict(node_attrs, **other_attrs)

        return (treeid+'syntax-'+node_id, node_attrs)

    @staticmethod
    def _conll_edge_attrs(treeid: str, row: ConllRow, spec: str) -> tuple[str, str, dict[str, str]]:
        child_id = treeid+'syntax-'+row[0]

        parent_position = row[CONLL_HEAD[spec].index('head')]

        if parent_position == '0':
            parent_id = treeid+'root-0'
        else:
            parent_id = treeid+'syntax-'+parent_position

        edge_attrs = {attr: row[idx]
                      for attr, idx in CONLL_EDGE_ATTRS[spec].items()}

        edge_attrs['domain'] = 'syntax'
        edge_attrs['type'] = 'dependency'

        return (parent_id, child_id, edge_attrs)
