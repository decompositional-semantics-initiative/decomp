# pylint: disable=W0221
# pylint: disable=R0903
# pylint: disable=R1704
"""Module for extracting predicates and arguments from dependency parses using PredPatt.

This module provides the core functionality for semantic role labeling by extracting
predicate-argument structures from Universal Dependencies parses. It includes:

- PredPattCorpus: Container for managing collections of PredPatt graphs
- PredPattGraphBuilder: Converts PredPatt extractions to NetworkX graphs
- Integration with UDS (Universal Decompositional Semantics) framework

The module identifies verbal predicates and their arguments using linguistic rules
applied to dependency parse trees, creating a semantic representation that can be
further annotated with UDS properties.
"""

from __future__ import annotations

from collections.abc import Hashable
from os.path import basename, splitext
from typing import TextIO, cast

from networkx import DiGraph

from ...corpus import Corpus
from ...syntax.dependency import CoNLLDependencyTreeCorpus
from .core.argument import Argument
from .core.options import PredPattOpts
from .core.predicate import Predicate
from .core.token import Token
from .extraction.engine import PredPattEngine as PredPatt

# Import from modernized modules
from .parsing.loader import load_comm, load_conllu


DEFAULT_PREDPATT_OPTIONS = PredPattOpts(resolve_relcl=True,
                                        borrow_arg_for_relcl=True,
                                        resolve_conj=False,
                                        cut=True)  # Resolve relative clause


class PredPattCorpus(Corpus[tuple[PredPatt, DiGraph], DiGraph]):
    """Container for managing collections of PredPatt semantic graphs.
    
    This class extends the base Corpus class to handle PredPatt extractions
    paired with their dependency graphs. It provides methods for loading
    corpora from CoNLL format and converting them to NetworkX graphs with
    semantic annotations.
    
    Attributes
    ----------
    _graphs : dict[Hashable, DiGraph]
        Mapping from graph identifiers to NetworkX directed graphs
        containing both syntactic and semantic information
    """

    def _graphbuilder(self,
                      graphid: Hashable,
                      predpatt_depgraph: tuple[PredPatt, DiGraph]) -> DiGraph:
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
    def from_conll(cls,
                   corpus: str | TextIO,
                   name: str = 'ewt',
                   options: PredPattOpts | None = None) -> PredPattCorpus:
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
        ud_corp_dict = {name+'-'+str(i+1): [line.split()
                                       for line in block.split('\n')
                                       if len(line) > 0
                                       if line[0] != '#']
                   for i, block in enumerate(data.split('\n\n'))}
        ud_corp_hashable = {cast(Hashable, k): v for k, v in ud_corp_dict.items()}
        ud_corp = CoNLLDependencyTreeCorpus(ud_corp_hashable)

        # extract the predpatt for those dependency parses
        try:
            predpatt = {name+'-'+sid.split('_')[1]: PredPatt(ud_parse,
                                                             opts=options)
                        for sid, ud_parse in load_conllu(data)}

        except ValueError:
            errmsg = 'PredPatt was unable to parse the CoNLL you provided.' +\
                     ' This is likely due to using a version of UD that is' +\
                     ' incompatible with PredPatt. Use of version 1.2 is' +\
                     ' suggested.'

            raise ValueError(errmsg) from None

        return cls({n: (pp, ud_corp[n])
                    for n, pp in predpatt.items()})


class PredPattGraphBuilder:
    """Constructs NetworkX graphs from PredPatt extractions.
    
    This class provides static methods for converting PredPatt's predicate
    and argument objects into a unified graph representation that includes
    both syntactic dependencies and semantic relations.
    """

    @classmethod
    def from_predpatt(cls,
                      predpatt: PredPatt,
                      depgraph: DiGraph,
                      graphid: str = '') -> DiGraph:
        """Build a unified graph from PredPatt extraction and dependency parse.

        Creates a NetworkX graph that contains:
        - All syntax nodes and edges from the original dependency parse
        - Semantic predicate and argument nodes extracted by PredPatt
        - Interface edges linking semantic nodes to their syntactic heads
        - Semantic edges connecting predicates to their arguments

        Parameters
        ----------
        predpatt : PredPatt
            The PredPatt extraction containing identified predicates and arguments
        depgraph : DiGraph
            The source dependency graph with syntactic relations
        graphid : str, optional
            Identifier prefix for all nodes in the graph. Default is empty string
            
        Returns
        -------
        DiGraph
            NetworkX graph with nodes in three domains:
            - syntax: original dependency parse nodes
            - semantics: predicate and argument nodes
            - interface: edges linking syntax and semantics
        """
        # handle null graphids
        graphid = graphid+'-' if graphid else ''

        # initialize the predpatt graph
        # predpattgraph = DiGraph(predpatt=predpatt)
        predpattgraph = DiGraph()
        predpattgraph.name = graphid.strip('-')

        # include all of the syntax edges in the original dependendency graph
        predpattgraph.add_nodes_from([(n, attr)
                                      for n, attr in depgraph.nodes.items()])
        predpattgraph.add_edges_from([(n1, n2, attr)
                                      for (n1, n2), attr
                                      in depgraph.edges.items()])

        # add links between predicate nodes and syntax nodes
        events_list = predpatt.events or []
        predpattgraph.add_edges_from([edge
                                      for event in events_list
                                      for edge
                                      in cls._instantiation_edges(graphid,
                                                                  event,
                                                                  'pred')])

        # add links between argument nodes and syntax nodes
        edges = [edge
                 for event in events_list
                 for arg in event.arguments
                 for edge
                 in cls._instantiation_edges(graphid, arg, 'arg')]

        predpattgraph.add_edges_from(edges)

        # add links between predicate nodes and argument nodes
        predarg_edges: list[tuple[str, str, dict[str, str | bool]]] = [edge
                 for event in events_list
                 for arg in event.arguments
                 for edge in cls._predarg_edges(graphid, event, arg,
                                                arg.position
                                                in [e.position
                                                    for e
                                                    in events_list])]

        predpattgraph.add_edges_from(predarg_edges)

        # mark that all the semantic nodes just added were from predpatt
        # this is done to distinguish them from nodes added through annotations
        for node in predpattgraph.nodes:
            if 'semantics' in node:
                predpattgraph.nodes[node]['domain'] = 'semantics'
                predpattgraph.nodes[node]['frompredpatt'] = True

                if 'arg' in node:
                    predpattgraph.nodes[node]['type'] = 'argument'
                elif 'pred' in node:
                    predpattgraph.nodes[node]['type'] = 'predicate'

        return predpattgraph

    @staticmethod
    def _instantiation_edges(graphid: str, node: Predicate | Argument, typ: str) -> list[tuple[str, str, dict[str, str]]]:
        """Create edges linking semantic nodes to their syntactic realizations.
        
        Generates interface edges from a semantic node (predicate or argument)
        to its head token and span tokens in the syntax layer.
        
        Parameters
        ----------
        graphid : str
            Graph identifier prefix for node IDs
        node : Predicate | Argument
            Semantic node to link to syntax
        typ : str
            Node type ('pred' for predicate, 'arg' for argument)
            
        Returns
        -------
        list[tuple[str, str, dict[str, str]]]
            List of edge tuples (source, target, attributes) where:
            - source is the semantic node ID
            - target is a syntax token ID
            - attributes mark domain as 'interface' and type as 'head' or 'nonhead'
        """
        parent_id = graphid+'semantics-'+typ+'-'+str(node.position+1)
        child_head_token_id = graphid+'syntax-'+str(node.position+1)
        child_span_token_ids = [graphid+'syntax-'+str(tok.position+1)
                                for tok in node.tokens
                                if child_head_token_id !=
                                graphid+'syntax-'+str(tok.position+1)]

        return [(parent_id, child_head_token_id,
                 {'domain': 'interface',
                  'type': 'head'})] +\
               [(parent_id, tokid, {'domain': 'interface',
                                    'type': 'nonhead'})
                for tokid in child_span_token_ids]

    @staticmethod
    def _predarg_edges(graphid: str, parent_node: Predicate, child_node: Argument, pred_child: bool) -> list[tuple[str, str, dict[str, str | bool]]]:
        """Create semantic edges between predicates and their arguments.
        
        Generates edges in the semantics domain connecting predicate nodes
        to their argument nodes. Handles special case where an argument
        is itself a predicate (e.g., in control constructions).
        
        Parameters
        ----------
        graphid : str
            Graph identifier prefix for node IDs
        parent_node : Predicate
            The predicate node
        child_node : Argument  
            The argument node
        pred_child : bool
            Whether the argument position corresponds to a predicate
            
        Returns
        -------
        list[tuple[str, str, dict[str, str | bool]]]
            List of semantic edges with 'dependency' type. If pred_child
            is True, also includes a 'head' edge from argument to its
            predicate realization
        """
        parent_id = graphid+'semantics-pred-'+str(parent_node.position+1)
        child_id = graphid+'semantics-arg-'+str(child_node.position+1)

        if pred_child:
            child_id_pred = graphid +\
                            'semantics-pred-' +\
                            str(child_node.position+1)
            return [
                (parent_id, child_id, {
                    'domain': 'semantics',
                    'type': 'dependency',
                    'frompredpatt': True
                }),
                (child_id, child_id_pred, {
                    'domain': 'semantics',
                    'type': 'head',
                    'frompredpatt': True
                })
            ]

        return [(parent_id,
                 child_id,
                 {'domain': 'semantics',
                  'type': 'dependency',
                  'frompredpatt': True})]
