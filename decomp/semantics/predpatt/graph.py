"""Graph construction for PredPatt semantic extractions.

This module provides functionality for converting PredPatt extractions into
unified NetworkX graphs that combine syntactic dependencies with semantic
predicate-argument structures.

Classes
-------
PredPattGraphBuilder
    Static methods for building NetworkX graphs from PredPatt extractions,
    creating unified representations with syntax, semantics, and interface layers.
"""

from networkx import DiGraph

from .core.argument import Argument
from .core.predicate import Predicate
from .extraction.engine import PredPattEngine as PredPatt


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
        predpattgraph.add_nodes_from([
            (n, attr)
            for n, attr in depgraph.nodes.items()
        ])
        predpattgraph.add_edges_from([
            (n1, n2, attr)
            for (n1, n2), attr
            in depgraph.edges.items()
        ])

        # add links between predicate nodes and syntax nodes
        events_list = predpatt.events or []
        predpattgraph.add_edges_from([
            edge
            for event in events_list
            for edge
            in cls._instantiation_edges(
                graphid,
                event,
                'pred'
            )
        ])

        # add links between argument nodes and syntax nodes
        edges = [
            edge
            for event in events_list
            for arg in event.arguments
            for edge
            in cls._instantiation_edges(graphid, arg, 'arg')
        ]

        predpattgraph.add_edges_from(edges)

        # add links between predicate nodes and argument nodes
        predarg_edges: list[tuple[str, str, dict[str, str | bool]]] = [
            edge
            for event in events_list
            for arg in event.arguments
            for edge in cls._predarg_edges(
                graphid, event, arg,
                arg.position
                in [e.position
                    for e
                    in events_list]
            )
        ]

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
    def _instantiation_edges(
        graphid: str,
        node: Predicate | Argument,
        typ: str
    ) -> list[tuple[str, str, dict[str, str]]]:
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
        parent_id = f"{graphid}semantics-{typ}-{node.position+1}"
        child_head_token_id = f"{graphid}syntax-{node.position+1}"
        child_span_token_ids = [
            f"{graphid}syntax-{tok.position+1}"
            for tok in node.tokens
            if child_head_token_id != f"{graphid}syntax-{tok.position+1}"
        ]

        return [
            (
                parent_id, child_head_token_id, {
                    'domain': 'interface',
                    'type': 'head'
                }
            )
        ] + [
            (
                parent_id, tokid, {
                    'domain': 'interface',
                    'type': 'nonhead'
                }
            )
            for tokid in child_span_token_ids
        ]

    @staticmethod
    def _predarg_edges(
        graphid: str,
        parent_node: Predicate,
        child_node: Argument,
        pred_child: bool
    ) -> list[tuple[str, str, dict[str, str | bool]]]:
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
        parent_id = f"{graphid}semantics-pred-{parent_node.position+1}"
        child_id = f"{graphid}semantics-arg-{child_node.position+1}"

        if pred_child:
            child_id_pred = f"{graphid}semantics-pred-{child_node.position+1}"
            return [
                (
                    parent_id, child_id, {
                        'domain': 'semantics',
                        'type': 'dependency',
                        'frompredpatt': True
                    }
                ),
                (
                    child_id, child_id_pred, {
                        'domain': 'semantics',
                        'type': 'head',
                        'frompredpatt': True
                    }
                )
            ]

        return [
            (
                parent_id, child_id, {
                    'domain': 'semantics',
                    'type': 'dependency',
                    'frompredpatt': True
                }
            )
        ]
