"""Module for representing UDS sentence and document graphs with NetworkX and RDF support.

This module provides graph representations for Universal Decompositional Semantics (UDS)
at both sentence and document levels. It includes:

- Type aliases for graph elements (nodes, edges, attributes)
- UDSGraph: Abstract base class for all UDS graphs
- UDSSentenceGraph: Sentence-level graphs with syntax/semantics nodes and edges
- UDSDocumentGraph: Document-level graphs connecting sentence graphs

The graphs support querying via SPARQL, conversion to/from RDF, and various
graph operations like finding maxima/minima and extracting subgraphs.
"""

from abc import ABC, abstractmethod
from functools import cached_property, lru_cache
from logging import info, warning
from typing import TYPE_CHECKING, Literal, TypeAlias

from networkx import DiGraph, adjacency_data, adjacency_graph
from overrides import overrides
from pyparsing import ParseException
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.sparql import Query
from rdflib.query import Result


# import RDFConverter (need to check if it exists first)
if TYPE_CHECKING:
    from ...graph import RDFConverter as _RDFConverter
    RDFConverter: type[_RDFConverter] | None = _RDFConverter
else:
    try:
        from ...graph import RDFConverter
    except ImportError:
        RDFConverter = None

# type aliases
NodeID: TypeAlias = str
"""Unique identifier for a node in the graph."""

EdgeKey: TypeAlias = tuple[NodeID, NodeID]
"""Edge identifier as (source_node, target_node) tuple."""

# domain and type literals
DomainType: TypeAlias = Literal['syntax', 'semantics', 'document']
"""The domain a node or edge belongs to."""

NodeType: TypeAlias = Literal['token', 'predicate', 'argument', 'root']
"""The type of a node within its domain."""

EdgeType: TypeAlias = Literal['head', 'nonhead', 'dependency', 'interface']
"""The type of relationship an edge represents."""

# node attributes can vary based on domain
# common attributes: domain, type, position, form, frompredpatt, semantics
# also includes UDS annotation subspaces and properties
NodeAttributes: TypeAlias = dict[str, str | int | bool | dict[str, str] | dict[str, dict[str, dict[str, str | int | bool | float]]] | dict[str, dict[str, dict[str, dict[str, str | int | bool | float]]]]]
"""Dictionary of node attributes including domain, type, and annotation data."""

EdgeAttributes: TypeAlias = dict[str, str | int | bool | dict[str, str] | dict[str, dict[str, dict[str, str | int | bool | float]]] | dict[str, dict[str, dict[str, dict[str, str | int | bool | float]]]]]
"""Dictionary of edge attributes including domain, type, and annotation data."""

# Attribute values can be various types
AttributeValue: TypeAlias = str | int | bool | float | dict[str, str]
"""Union of possible attribute value types."""

QueryResult: TypeAlias = dict[str, NodeAttributes] | dict[EdgeKey, EdgeAttributes]
"""Result type for graph queries, either nodes or edges."""


class UDSGraph(ABC):
    """Abstract base class for sentence- and document-level graphs

    Parameters
    ----------
    graph
        a NetworkX DiGraph
    name
        a unique identifier for the graph
    """

    @abstractmethod
    def __init__(self, graph: DiGraph, name: str):
        self.name = name
        self.graph = graph

    @property
    def nodes(self) -> dict[NodeID, NodeAttributes]:
        """All nodes in the graph with their attributes.

        Returns
        -------
        dict[NodeID, NodeAttributes]
            Mapping from node IDs to their attributes
        """
        return dict(self.graph.nodes)

    @property
    def edges(self) -> dict[EdgeKey, EdgeAttributes]:
        """All edges in the graph with their attributes.

        Returns
        -------
        dict[EdgeKey, EdgeAttributes]
            Mapping from edge tuples to their attributes
        """
        return dict(self.graph.edges)

    def to_dict(self) -> dict[str, dict[str, dict[str, str | int | bool | dict[str, str]]]]:
        """Convert the graph to adjacency dictionary format.

        Returns
        -------
        dict[str, dict[str, dict[str, str | int | bool | dict[str, str]]]]
            NetworkX adjacency data format
        """
        return dict(adjacency_data(self.graph))

    @classmethod
    def from_dict(cls, graph: dict[str, dict[str, dict[str, str | int | bool | dict[str, str]]]], name: str = 'UDS') -> 'UDSGraph':
        """Construct a UDSGraph from a dictionary

        Parameters
        ----------
        graph
            a dictionary constructed by networkx.adjacency_data
        name
            identifier to append to the beginning of node ids
        """
        return cls(adjacency_graph(graph), name)


class UDSSentenceGraph(UDSGraph):
    """A Universal Decompositional Semantics sentence-level graph

    Parameters
    ----------
    graph
        the NetworkX DiGraph from which the sentence-level graph
        is to be constructed
    name
        the name of the graph
    sentence_id
        the UD identifier for the sentence associated with this graph
    document_id
        the UD identifier for the document associated with this graph
    """

    QUERIES: dict[str, Query] = {}

    @overrides
    def __init__(self, graph: DiGraph, name: str, sentence_id: str | None = None,
                 document_id: str | None = None):
        super().__init__(graph, name)
        self.sentence_id = sentence_id
        self.document_id = document_id
        self._rdf: Graph | None = None
        self._add_performative_nodes()

    @property
    def rdf(self) -> Graph:
        """The graph converted to RDF format.

        Returns
        -------
        Graph
            RDFLib graph representation

        Raises
        ------
        AttributeError
            If RDFConverter is not available
        """
        if self._rdf is None:
            if RDFConverter is None:
                raise AttributeError("RDFConverter not available")
            # Type narrowing: RDFConverter is not None at this point
            converter: type[_RDFConverter] = RDFConverter
            self._rdf = converter.networkx_to_rdf(self.graph)
        return self._rdf

    @cached_property
    def rootid(self) -> NodeID:
        """The ID of the graph's root node.

        Returns
        -------
        NodeID
            The root node identifier

        Raises
        ------
        ValueError
            If the graph has no root or multiple roots
        """
        candidates: list[NodeID] = [nid for nid, attrs
                                   in self.graph.nodes.items()
                                   if attrs['type'] == 'root']

        if len(candidates) > 1:
            errmsg = self.name + ' has more than one root'
            raise ValueError(errmsg)

        if len(candidates) == 0:
            errmsg = self.name + ' has no root'
            raise ValueError(errmsg)

        return candidates[0]

    def _add_performative_nodes(self) -> None:
        """Add performative nodes (author, addressee, root predicate) to the graph.

        Creates special nodes that represent the speech act structure:
        - semantics-pred-root: The root predicate node
        - semantics-arg-0: Argument representing the utterance
        - semantics-arg-author: The speaker/writer
        - semantics-arg-addressee: The listener/reader
        """
        max_preds = self.maxima([nid for nid, attrs
                                 in self.semantics_nodes.items()
                                 if attrs['frompredpatt']])

        # new nodes
        self.graph.add_node(self.graph.name+'-semantics-pred-root',
                            domain='semantics', type='predicate',
                            frompredpatt=False)

        self.graph.add_node(self.graph.name+'-semantics-arg-0',
                            domain='semantics', type='argument',
                            frompredpatt=False)

        self.graph.add_node(self.graph.name+'-semantics-arg-author',
                            domain='semantics', type='argument',
                            frompredpatt=False)

        self.graph.add_node(self.graph.name+'-semantics-arg-addressee',
                            domain='semantics', type='argument',
                            frompredpatt=False)

        # new semantics edges
        for predid in max_preds:
            if predid != self.graph.name+'-semantics-pred-root':
                self.graph.add_edge(self.graph.name+'-semantics-arg-0',
                                    predid,
                                    domain='semantics', type='head',
                                    frompredpatt=False)

        self.graph.add_edge(self.graph.name+'-semantics-pred-root',
                            self.graph.name+'-semantics-arg-0',
                            domain='semantics', type='dependency',
                            frompredpatt=False)

        self.graph.add_edge(self.graph.name+'-semantics-pred-root',
                            self.graph.name+'-semantics-arg-author',
                            domain='semantics', type='dependency',
                            frompredpatt=False)

        self.graph.add_edge(self.graph.name+'-semantics-pred-root',
                            self.graph.name+'-semantics-arg-addressee',
                            domain='semantics', type='dependency',
                            frompredpatt=False)

        # new instance edge
        self.graph.add_edge(self.graph.name+'-semantics-arg-0',
                            self.graph.name+'-root-0',
                            domain='interface', type='dependency',
                            frompredpatt=False)

    @lru_cache(maxsize=128)
    def query(self, query: str | Query,
              query_type: str | None = None,
              cache_query: bool = True,
              cache_rdf: bool = True) -> Result | dict[str, NodeAttributes] | dict[EdgeKey, EdgeAttributes]:
        """Query graph using SPARQL 1.1

        Parameters
        ----------
        query
            a SPARQL 1.1 query
        query_type
            whether this is a 'node' query or 'edge' query. If set to
            None (default), a Results object will be returned. The
            main reason to use this option is to automatically format
            the output of a custom query, since Results objects
            require additional postprocessing.
        cache_query
            whether to cache the query; false when querying
            particular nodes or edges using precompiled queries
        clear_rdf
            whether to delete the RDF constructed for querying
            against. This will slow down future queries but saves a
            lot of memory
        """
        results: Result | dict[str, NodeAttributes] | dict[EdgeKey, EdgeAttributes]
        try:
            if isinstance(query, str) and cache_query:
                if query not in self.__class__.QUERIES:
                    self.__class__.QUERIES[query] = prepareQuery(query)

                query = self.__class__.QUERIES[query]

            if query_type == 'node':
                results = self._node_query(query, cache_query=cache_query)

            elif query_type == 'edge':
                results = self._edge_query(query, cache_query=cache_query)

            else:
                results = self.rdf.query(query)

        except ParseException:
            errmsg = 'invalid SPARQL 1.1 query'
            raise ValueError(errmsg)

        if not cache_rdf and hasattr(self, '_rdf'):
            delattr(self, '_rdf')

        return results

    def _node_query(self, query: str | Query,
                    cache_query: bool) -> dict[str, NodeAttributes]:
        """Execute a SPARQL query that returns nodes.

        Parameters
        ----------
        query : str | Query
            SPARQL query expected to return node IDs
        cache_query : bool
            Whether to cache the compiled query

        Returns
        -------
        dict[str, NodeAttributes]
            Mapping from node IDs to their attributes

        Raises
        ------
        ValueError
            If query returns non-node results
        """
        results: list[str] = [r[0].toPython()  # type: ignore[index,union-attr]
                             for r in self.query(query,
                                                 cache_query=cache_query)]

        try:
            return {nodeid: self.graph.nodes[nodeid] for nodeid in results}
        except KeyError:
            raise ValueError(
                'invalid node query: your query must be guaranteed '
                'to capture only nodes, but it appears to also '
                'capture edges and/or properties'
            )

    def _edge_query(self, query: str | Query,
                    cache_query: bool) -> dict[EdgeKey, EdgeAttributes]:
        """Execute a SPARQL query that returns edges.

        Parameters
        ----------
        query : str | Query
            SPARQL query expected to return edge IDs (format: "node1%%node2")
        cache_query : bool
            Whether to cache the compiled query

        Returns
        -------
        dict[EdgeKey, EdgeAttributes]
            Mapping from edge tuples to their attributes

        Raises
        ------
        ValueError
            If query returns non-edge results
        """
        results: list[tuple[str, str]] = [
            tuple(edge[0].toPython().split('%%'))  # type: ignore[index,union-attr]
            for edge in self.query(query, cache_query=cache_query)
        ]

        try:
            return {edge: self.graph.edges[edge]
                    for edge in results}
        except KeyError:
            raise ValueError(
                'invalid edge query: your query must be guaranteed '
                'to capture only edges, but it appears to also '
                'capture nodes and/or properties'
            )

    @property
    def syntax_nodes(self) -> dict[str, NodeAttributes]:
        """All syntax domain token nodes.

        Returns
        -------
        dict[str, NodeAttributes]
            Mapping of node IDs to attributes for syntax tokens
        """
        return {
            nid: attrs for nid, attrs in self.graph.nodes.items()
            if attrs['domain'] == 'syntax'
            if attrs['type'] == 'token'
        }

    @property
    def semantics_nodes(self) -> dict[str, NodeAttributes]:
        """All semantics domain nodes.

        Returns
        -------
        dict[str, NodeAttributes]
            Mapping of node IDs to attributes for semantics nodes
        """
        return {nid: attrs for nid, attrs
                in self.graph.nodes.items()
                if attrs['domain'] == 'semantics'}

    @property
    def predicate_nodes(self) -> dict[str, NodeAttributes]:
        """All predicate nodes in the semantics domain.

        Returns
        -------
        dict[str, NodeAttributes]
            Mapping of node IDs to attributes for predicates
        """
        return {nid: attrs for nid, attrs
                in self.graph.nodes.items()
                if attrs['domain'] == 'semantics'
                if attrs['type']  == 'predicate'}

    @property
    def argument_nodes(self) -> dict[str, NodeAttributes]:
        """All argument nodes in the semantics domain.

        Returns
        -------
        dict[str, NodeAttributes]
            Mapping of node IDs to attributes for arguments
        """
        return {nid: attrs for nid, attrs
                in self.graph.nodes.items()
                if attrs['domain'] == 'semantics'
                if attrs['type']  == 'argument'}

    @property
    def syntax_subgraph(self) -> DiGraph:
        """Subgraph containing only syntax nodes.

        Returns
        -------
        DiGraph
            NetworkX subgraph with syntax nodes
        """
        return self.graph.subgraph(list(self.syntax_nodes))

    @property
    def semantics_subgraph(self) -> DiGraph:
        """Subgraph containing only semantics nodes.

        Returns
        -------
        DiGraph
            NetworkX subgraph with semantics nodes
        """
        return self.graph.subgraph(list(self.semantics_nodes))

    @lru_cache(maxsize=128)
    def semantics_edges(self,
                        nodeid: str | None = None,
                        edgetype: str | None = None) -> dict[EdgeKey, EdgeAttributes]:
        """The edges between semantics nodes
        
        Parameters
        ----------
        nodeid
            The node that must be incident on an edge
        edgetype
            The type of edge ("dependency" or "head")
        """
        if nodeid is None:
            candidates = {eid: attrs for eid, attrs
                          in self.graph.edges.items()
                          if attrs['domain'] == 'semantics'}

        else:
            candidates = {eid: attrs for eid, attrs
                          in self.graph.edges.items()
                          if attrs['domain'] == 'semantics'
                          if nodeid in eid}

        if edgetype is None:
            return candidates
        else:
            return {eid: attrs for eid, attrs in candidates.items()
                    if attrs['type'] == edgetype}

    @lru_cache(maxsize=128)
    def argument_edges(self,
                       nodeid: str | None = None) -> dict[EdgeKey, EdgeAttributes]:
        """The edges between predicates and their arguments
        
        Parameters
        ----------
        nodeid
            The node that must be incident on an edge
        """
        return self.semantics_edges(nodeid, edgetype='dependency')

    @lru_cache(maxsize=128)
    def argument_head_edges(self,
                            nodeid: str | None = None) -> dict[EdgeKey, EdgeAttributes]:
        """The edges between nodes and their semantic heads

        Parameters
        ----------
        nodeid
            The node that must be incident on an edge
        """
        return self.semantics_edges(nodeid, edgetype='head')

    @lru_cache(maxsize=128)
    def syntax_edges(self,
                     nodeid: str | None = None) -> dict[EdgeKey, EdgeAttributes]:
        """The edges between syntax nodes

        Parameters
        ----------
        nodeid
            The node that must be incident on an edge
        """
        if nodeid is None:
            return {
                eid: attrs for eid, attrs in self.graph.edges.items()
                if attrs['domain'] == 'syntax'
            }

        else:
            return {eid: attrs for eid, attrs
                          in self.graph.edges.items()
                          if attrs['domain'] == 'syntax'
                          if nodeid in eid}

    @lru_cache(maxsize=128)
    def instance_edges(self,
                       nodeid: str | None = None) -> dict[EdgeKey, EdgeAttributes]:
        """The edges between syntax nodes and semantics nodes

        Parameters
        ----------
        nodeid
            The node that must be incident on an edge
        """
        if nodeid is None:
            return {eid: attrs for eid, attrs
                          in self.graph.edges.items()
                          if attrs['domain'] == 'interface'}

        else:
            return {eid: attrs for eid, attrs
                          in self.graph.edges.items()
                          if attrs['domain'] == 'interface'
                          if nodeid in eid}

    def span(self,
             nodeid: str,
             attrs: list[str] = ['form']) -> dict[int, list[AttributeValue]]:
        """The span corresponding to a semantics node

        Parameters
        ----------
        nodeid
            the node identifier for a semantics node
        attrs
            a list of syntax node attributes to return

        Returns
        -------
        a mapping from positions in the span to the requested
        attributes in those positions
        """
        if self.graph.nodes[nodeid]['domain'] != 'semantics':
            raise ValueError('Only semantics nodes have (nontrivial) spans')

        is_performative = 'pred-root' in nodeid or\
                          'arg-author' in nodeid or\
                          'arg-addressee' in nodeid or\
                          'arg-0' in nodeid

        if is_performative:
            raise ValueError('Performative nodes do not have spans')


        return {self.graph.nodes[e[1]]['position']: [self.graph.nodes[e[1]][a]
                                               for a in attrs]
                for e in self.instance_edges(nodeid)}

    def head(self,
             nodeid: str,
             attrs: list[str] = ['form']) -> tuple[int, list[AttributeValue]]:
        """The head corresponding to a semantics node

        Parameters
        ----------
        nodeid
            the node identifier for a semantics node
        attrs
            a list of syntax node attributes to return

        Returns
        -------
        a pairing of the head position and the requested
        attributes
        """
        if self.graph.nodes[nodeid]['domain'] != 'semantics':
            raise ValueError('Only semantics nodes have heads')

        is_performative = 'pred-root' in nodeid or\
                          'arg-author' in nodeid or\
                          'arg-addressee' in nodeid or\
                          'arg-0' in nodeid

        if is_performative:
            raise ValueError('Performative nodes do not have heads')

        return [(self.graph.nodes[e[1]]['position'],
                 [self.graph.nodes[e[1]][a] for a in attrs])
                for e, attr in self.instance_edges(nodeid).items()
                if attr['type'] == 'head'][0]

    def maxima(self, nodeids: list[str] | None = None) -> list[str]:
        """Find nodes not dominated by any other nodes in the set.

        Parameters
        ----------
        nodeids : list[str] | None, optional
            Nodes to consider. If None, uses all nodes.

        Returns
        -------
        list[str]
            Node IDs that have no incoming edges from other nodes in the set
        """
        if nodeids is None:
            nodeids = list(self.graph.nodes)

        return [nid for nid in nodeids
                if all(e[0] == nid
                       for e in self.graph.edges
                       if e[0] in nodeids
                       if e[1] in nodeids
                       if nid in e)]

    def minima(self, nodeids: list[str] | None = None) -> list[str]:
        """Find nodes not dominating any other nodes in the set.

        Parameters
        ----------
        nodeids : list[str] | None, optional
            Nodes to consider. If None, uses all nodes.

        Returns
        -------
        list[str]
            Node IDs that have no outgoing edges to other nodes in the set
        """
        if nodeids is None:
            nodeids = list(self.graph.nodes)

        return [nid for nid in nodeids
                if all(e[0] != nid
                       for e in self.graph.edges
                       if e[0] in nodeids
                       if e[1] in nodeids
                       if nid in e)]

    def add_annotation(self,
                       node_attrs: dict[str, NodeAttributes],
                       edge_attrs: dict[EdgeKey, EdgeAttributes],
                       add_heads: bool = True,
                       add_subargs: bool = False,
                       add_subpreds: bool = False,
                       add_orphans: bool = False) -> None:
        """Add node and or edge annotations to the graph

        Parameters
        ----------
        node_attrs
        edge_attrs
        add_heads
        add_subargs
        add_subpreds
        add_orphans
        """
        for node, attrs in node_attrs.items():
            self._add_node_annotation(node, attrs,
                                      add_heads, add_subargs,
                                      add_subpreds, add_orphans)

        for edge, attrs in edge_attrs.items():
            self._add_edge_annotation(edge, attrs)

    def _add_node_annotation(self, node: NodeID, attrs: NodeAttributes,
                             add_heads: bool, add_subargs: bool,
                             add_subpreds: bool, add_orphans: bool) -> None:
        """Add annotation to a node, potentially creating new nodes.

        Parameters
        ----------
        node : NodeID
            Node identifier
        attrs : NodeAttributes
            Attributes to add
        add_heads : bool
            Whether to add head nodes
        add_subargs : bool
            Whether to add subargument nodes
        add_subpreds : bool
            Whether to add subpredicate nodes
        add_orphans : bool
            Whether to add orphan nodes
        """
        if node in self.graph.nodes:
            self.graph.nodes[node].update(attrs)

        elif 'headof' in attrs and attrs['headof'] in self.graph.nodes:
            edge = (attrs['headof'], node)

            if not add_heads:
                info(
                    f'head edge {edge} in {self.name} '
                    'found in annotations but not added'
                )

            else:
                infomsg = 'adding head edge ' + str(edge) + ' to ' + self.name
                info(infomsg)

                attrs = dict(attrs,
                             **{'domain': 'semantics',
                                'type': 'argument',
                                'frompredpatt': False})

                self.graph.add_node(node,
                                    **{k: v
                                       for k, v in attrs.items()
                                       if k not in ['headof',
                                                    'head',
                                                    'span']})
                self.graph.add_edge(*edge, domain='semantics', type='head')

                instedge = (node, attrs['head'])
                self.graph.add_edge(*instedge, domain='interface', type='head')

                # for nonhead in attrs['span']:
                #     if nonhead != attrs['head']:
                #         instedge = (node, nonhead)
                #         self.graph.add_edge(*instedge, domain='interface', type='head')

        elif 'subargof' in attrs and attrs['subargof'] in self.graph.nodes:
            edge = (attrs['subargof'], node)

            if not add_subargs:
                infomsg = 'subarg edge ' + str(edge) + ' in ' + self.name +\
                          ' found in annotations but not added'
                info(infomsg)

            else:
                infomsg = 'adding subarg edge ' + str(edge) + ' to ' +\
                          self.name
                info(infomsg)

                attrs = dict(attrs,
                             **{'domain': 'semantics',
                                'type': 'argument',
                                'frompredpatt': False})

                self.graph.add_node(node,
                                    **{k: v
                                       for k, v in attrs.items()
                                       if k != 'subargof'})
                self.graph.add_edge(*edge,
                                    domain='semantics',
                                    type='subargument')

                instedge = (node, node.replace('semantics-subarg', 'syntax'))
                self.graph.add_edge(*instedge, domain='interface', type='head')

        elif 'subpredof' in attrs and attrs['subpredof'] in self.graph.nodes:
            edge = (attrs['subpredof'], node)

            if not add_subpreds:
                info(
                    f'subpred edge {edge} in {self.name} '
                    'found in annotations but not added'
                )

            else:
                info(
                    f'adding subpred edge {edge} to {self.name}'
                )

                attrs = dict(attrs,
                             **{'domain': 'semantics',
                                'type': 'predicate',
                                'frompredpatt': False})

                self.graph.add_node(node,
                                    **{k: v
                                       for k, v in attrs.items()
                                       if k != 'subpredof'})

                self.graph.add_edge(*edge,
                                    domain='semantics',
                                    type='subpredicate')

                instedge = (node, node.replace('semantics-subpred', 'syntax'))
                self.graph.add_edge(*instedge, domain='interface', type='head')

        elif not add_orphans:
            info(
                f'orphan node {node} in {self.name} '
                'found in annotations but not added'
            )

        else:
            warnmsg = 'adding orphan node ' + node + ' in ' + self.name
            warning(warnmsg)

            attrs = dict(attrs,
                         **{'domain': 'semantics',
                            'type': 'predicate',
                            'frompredpatt': False})

            self.graph.add_node(node,
                                **{k: v
                                   for k, v in attrs.items()
                                   if k != 'subpredof'})

            synnode = node.replace('semantics-pred', 'syntax')
            synnode = synnode.replace('semantics-arg', 'syntax')
            synnode = synnode.replace('semantics-subpred', 'syntax')
            synnode = synnode.replace('semantics-subarg', 'syntax')

            instedge = (node, synnode)

            self.graph.add_edge(*instedge, domain='interface', type='head')

            if self.rootid is not None:
                self.graph.add_edge(self.rootid, node)

    def _add_edge_annotation(self, edge: EdgeKey, attrs: EdgeAttributes) -> None:
        """Add annotation to an edge.

        Parameters
        ----------
        edge : EdgeKey
            Edge tuple (source, target)
        attrs : EdgeAttributes
            Attributes to add
        """
        if edge in self.graph.edges:
            self.graph.edges[edge].update(attrs)
        else:
            warnmsg = 'adding unlabeled edge ' + str(edge) + ' to ' + self.name
            warning(warnmsg)
            self.graph.add_edge(*edge, **attrs)

    @cached_property
    def sentence(self) -> str:
        """The sentence text reconstructed from syntax nodes.

        Returns
        -------
        str
            The sentence text with tokens in surface order
        """
        id_word = {}
        for nodeid, nodeattr in self.syntax_nodes.items():
            pos = nodeattr.get('position')
            form = nodeattr.get('form')
            if isinstance(pos, int) and isinstance(form, str):
                id_word[pos - 1] = form

        return ' '.join([
            id_word[i] for i in range(max(list(id_word.keys()))+1)
        ])


class UDSDocumentGraph(UDSGraph):
    """A Universal Decompositional Semantics document-level graph

    Parameters
    ----------
    graph
        the NetworkX DiGraph from which the document-level graph
        is to be constructed
    name
        the name of the graph
    """

    @overrides
    def __init__(self, graph: DiGraph, name: str):
        super().__init__(graph, name)

    def add_annotation(
        self,
        node_attrs: dict[str, NodeAttributes],
        edge_attrs: dict[EdgeKey, EdgeAttributes],
        sentence_ids: dict[str, str]
    ) -> None:
        """Add node and or edge annotations to the graph

        Parameters
        ----------
        node_attrs
            the node annotations to be added
        edge_attrs
            the edge annotations to be added
        sentence_ids
            the IDs of all sentences in the document
        """
        for node, attrs in node_attrs.items():
            self._add_node_annotation(node, attrs)

        for edge, attrs in edge_attrs.items():
            self._add_edge_annotation(edge, attrs, sentence_ids)

    def _add_edge_annotation(self, edge: EdgeKey, attrs: EdgeAttributes, sentence_ids: dict[str, str]) -> None:
        """Add annotation to a document-level edge.

        Parameters
        ----------
        edge : EdgeKey
            Edge tuple (source, target)
        attrs : EdgeAttributes
            Attributes to add
        sentence_ids : dict[str, str]
            Mapping of graph names to sentence IDs
        """
        if edge in self.graph.edges:
            self.graph.edges[edge].update(attrs)
        else:
            # Verify that the annotation is intra-document
            s1 = '-'.join(edge[0].split('-')[:3])
            s2 = '-'.join(edge[1].split('-')[:3])

            if s1 not in sentence_ids or s2 not in sentence_ids:
                warning(
                    f'Skipping cross-document annotation from {edge[0]} '
                    f'to {edge[1]}'
                )
                return

            attrs = dict(
                attrs,
                **{'domain': 'document',
                   'type': 'relation',
                   'frompredpatt': False,
                   'id': edge[1]}
            )

        self.graph.add_edge(*edge, **attrs)

    def _add_node_annotation(self, node: NodeID, attrs: NodeAttributes) -> None:
        """Add annotation to a document-level node.

        Note: Document-level node annotations are uncommon; most document
        annotations are edge-based.

        Parameters
        ----------
        node : NodeID
            Node identifier
        attrs : NodeAttributes
            Attributes to add
        """
        # we do not currently have a use case for document node annotations,
        # but it is included for completeness.
        if node in self.graph.nodes:
            warning(
                f'Attempting to add a node annotation to node {node} '
                f'in document graph {self.name}. Document-level '
                'annotations should likely be edge attributes.'
            )
            self.graph.nodes[node].update(attrs)
        else:
            warning(
                f'Attempting to add annotation to unknown node {node} '
                f'in document graph {self.name}'
            )
