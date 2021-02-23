"""Module for representing UDS sentence and document graphs."""

from logging import info, warning
from abc import ABC, abstractmethod
from overrides import overrides
from functools import lru_cache
from typing import Union, Optional, Any
from typing import Dict, List, Tuple
from memoized_property import memoized_property
from pyparsing import ParseException
from rdflib import Graph
from rdflib.query import Result
from rdflib.plugins.sparql.sparql import Query
from rdflib.plugins.sparql import prepareQuery
from networkx import DiGraph, adjacency_data, adjacency_graph
from ...graph import RDFConverter


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
    def nodes(self):
        """All the nodes in the graph"""
        return self.graph.nodes

    @property
    def edges(self):
        """All the edges in the graph"""
        return self.graph.edges

    def to_dict(self) -> Dict:
        """Convert the graph to a dictionary"""

        return adjacency_data(self.graph)

    @classmethod
    def from_dict(cls, graph: Dict[str, Any], name: str = 'UDS') -> 'UDSGraph':
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

    QUERIES = {}

    @overrides
    def __init__(self, graph: DiGraph, name: str, sentence_id: Optional[str] = None,
                 document_id: Optional[str] = None):
        super().__init__(graph, name)
        self.sentence_id = sentence_id
        self.document_id = document_id
        self._add_performative_nodes()

    @property
    def rdf(self) -> Graph:
        """The graph as RDF"""
        if hasattr(self, '_rdf'):
            return self._rdf
        else:
            self._rdf = RDFConverter.networkx_to_rdf(self.graph)
            return self._rdf

    @memoized_property
    def rootid(self):
        """The ID of the graph's root node"""
        candidates = [nid for nid, attrs
                      in self.graph.nodes.items()
                      if attrs['type'] == 'root']
        
        if len(candidates) > 1:
            errmsg = self.name + ' has more than one root'
            raise ValueError(errmsg)

        if len(candidates) == 0:
            errmsg = self.name + ' has no root'
            raise ValueError(errmsg)        
        
        return candidates[0]

    def _add_performative_nodes(self):
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
    def query(self, query: Union[str, Query],
              query_type: Optional[str] = None,
              cache_query: bool = True,
              cache_rdf: bool = True) -> Union[Result,
                                               Dict[str,
                                                    Dict[str, Any]]]:
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
        try:
            if isinstance(query, str) and cache_query:
                if query not in self.__class__.QUERIES:
                    self.__class__.QUERIES[query] = prepareQuery(query)

                query = self.__class__.QUERIES[query]

            if query_type == 'node':
                results = self._node_query(query,
                                           cache_query=cache_query)

            elif query_type == 'edge':
                results = self._edge_query(query,
                                           cache_query=cache_query)

            else:
                results = self.rdf.query(query)

        except ParseException:
            errmsg = 'invalid SPARQL 1.1 query'
            raise ValueError(errmsg)

        if not cache_rdf and hasattr(self, '_rdf'):
            delattr(self, '_rdf')
        
        return results

    def _node_query(self, query: Union[str, Query],
                    cache_query: bool) -> Dict[str,
                                               Dict[str, Any]]:

        results = [r[0].toPython()
                   for r in self.query(query,
                                       cache_query=cache_query)]

        try:
            return {nodeid: self.graph.nodes[nodeid] for nodeid in results}
        except KeyError:
            errmsg = 'invalid node query: your query must be guaranteed ' +\
                     'to capture only nodes, but it appears to also ' +\
                     'capture edges and/or properties'
            raise ValueError(errmsg)

    def _edge_query(self, query: Union[str, Query],
                    cache_query: bool) -> Dict[Tuple[str, str],
                                               Dict[str, Any]]:

        results = [tuple(edge[0].toPython().split('%%'))
                   for edge in self.query(query,
                                          cache_query=cache_query)]

        try:
            return {edge: self.graph.edges[edge]
                    for edge in results}
        except KeyError:
            errmsg = 'invalid edge query: your query must be guaranteed ' +\
                     'to capture only edges, but it appears to also ' +\
                     'capture nodes and/or properties'
            raise ValueError(errmsg)

    @property
    def syntax_nodes(self) -> Dict[str, Dict[str, Any]]:
        """The syntax nodes in the graph"""

        return {nid: attrs for nid, attrs
                in self.graph.nodes.items()
                if attrs['domain'] == 'syntax'
                if attrs['type'] == 'token'}

    @property
    def semantics_nodes(self) -> Dict[str, Dict[str, Any]]:
        """The semantics nodes in the graph"""

        return {nid: attrs for nid, attrs
                in self.graph.nodes.items()
                if attrs['domain'] == 'semantics'}

    @property
    def predicate_nodes(self) -> Dict[str, Dict[str, Any]]:
        """The predicate (semantics) nodes in the graph"""

        return {nid: attrs for nid, attrs
                in self.graph.nodes.items()
                if attrs['domain'] == 'semantics'
                if attrs['type']  == 'predicate'}

    @property
    def argument_nodes(self) -> Dict[str, Dict[str, Any]]:
        """The argument (semantics) nodes in the graph"""

        return {nid: attrs for nid, attrs
                in self.graph.nodes.items()
                if attrs['domain'] == 'semantics'
                if attrs['type']  == 'argument'}

    @property
    def syntax_subgraph(self) -> DiGraph:
        """The part of the graph with only syntax nodes"""

        return self.graph.subgraph(list(self.syntax_nodes))

    @property
    def semantics_subgraph(self) -> DiGraph:
        """The part of the graph with only semantics nodes"""

        return self.graph.subgraph(list(self.semantics_nodes))

    @lru_cache(maxsize=128)
    def semantics_edges(self,
                        nodeid: Optional[str] = None,
                        edgetype: Optional[str] = None) -> Dict[Tuple[str, str],
                                                                Dict[str, Any]]:
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
                       nodeid: Optional[str] = None) -> Dict[Tuple[str, str],
                                                             Dict[str, Any]]:
        """The edges between predicates and their arguments
        
        Parameters
        ----------
        nodeid
            The node that must be incident on an edge
        """

        return self.semantics_edges(nodeid, edgetype='dependency')
        
    @lru_cache(maxsize=128)
    def argument_head_edges(self,
                            nodeid: Optional[str] = None) -> Dict[Tuple[str,
                                                                        str],
                                                                  Dict[str,
                                                                       Any]]:
        """The edges between nodes and their semantic heads

        Parameters
        ----------
        nodeid
            The node that must be incident on an edge
        """

        return self.semantics_edges(nodeid, edgetype='head')

    @lru_cache(maxsize=128)
    def syntax_edges(self,
                     nodeid: Optional[str] = None) -> Dict[Tuple[str, str],
                                                           Dict[str, Any]]:
        """The edges between syntax nodes


        Parameters
        ----------
        nodeid
            The node that must be incident on an edge
        """

        if nodeid is None:
            return {eid: attrs for eid, attrs
                          in self.graph.edges.items()
                          if attrs['domain'] == 'syntax'}

        else:
            return {eid: attrs for eid, attrs
                          in self.graph.edges.items()
                          if attrs['domain'] == 'syntax'
                          if nodeid in eid}

    @lru_cache(maxsize=128)
    def instance_edges(self,
                       nodeid: Optional[str] = None) -> Dict[Tuple[str, str],
                                                             Dict[str, Any]]:
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
             attrs: List[str] = ['form']) -> Dict[int, List[Any]]:
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
            errmsg = 'Only semantics nodes have (nontrivial) spans'
            raise ValueError(errmsg)

        is_performative = 'pred-root' in nodeid or\
                          'arg-author' in nodeid or\
                          'arg-addressee' in nodeid or\
                          'arg-0' in nodeid
        
        if is_performative:
            errmsg = 'Performative nodes do not have spans'
            raise ValueError(errmsg)

        
        return {self.graph.nodes[e[1]]['position']: [self.graph.nodes[e[1]][a]
                                               for a in attrs]
                for e in self.instance_edges(nodeid)}

    def head(self,
             nodeid: str,
             attrs: List[str] = ['form']) -> Tuple[int, List[Any]]:
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
            errmsg = 'Only semantics nodes have heads'
            raise ValueError(errmsg)

        is_performative = 'pred-root' in nodeid or\
                          'arg-author' in nodeid or\
                          'arg-addressee' in nodeid or\
                          'arg-0' in nodeid
        
        if is_performative:
            errmsg = 'Performative nodes do not have heads'
            raise ValueError(errmsg)
        
        return [(self.graph.nodes[e[1]]['position'],
                 [self.graph.nodes[e[1]][a] for a in attrs])
                for e, attr in self.instance_edges(nodeid).items()
                if attr['type'] == 'head'][0]

    def maxima(self, nodeids: Optional[List[str]] = None) -> List[str]:
        """The nodes in nodeids not dominated by any other nodes in nodeids"""

        if nodeids is None:
            nodeids = list(self.graph.nodes)

        return [nid for nid in nodeids
                if all(e[0] == nid
                       for e in self.graph.edges
                       if e[0] in nodeids
                       if e[1] in nodeids
                       if nid in e)]

    def minima(self, nodeids: Optional[List[str]] = None) -> List[str]:
        """The nodes in nodeids not dominating any other nodes in nodeids"""

        if nodeids is None:
            nodeids = list(self.graph.nodes)

        return [nid for nid in nodeids
                if all(e[0] != nid
                       for e in self.graph.edges
                       if e[0] in nodeids
                       if e[1] in nodeids
                       if nid in e)]

    def add_annotation(self,
                       node_attrs: Dict[str, Dict[str, Any]],
                       edge_attrs: Dict[str, Dict[str, Any]],
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

    def _add_node_annotation(self, node, attrs,
                             add_heads, add_subargs,
                             add_subpreds, add_orphans):
        if node in self.graph.nodes:
            self.graph.nodes[node].update(attrs)

        elif 'headof' in attrs and attrs['headof'] in self.graph.nodes:
            edge = (attrs['headof'], node)

            if not add_heads:
                infomsg = 'head edge ' + str(edge) + ' in ' + self.name +\
                          ' found in annotations but not added'
                info(infomsg)

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
                infomsg = 'subpred edge ' + str(edge) + ' in ' + self.name +\
                          ' found in annotations but not added'
                info(infomsg)

            else:
                infomsg = 'adding subpred edge ' + str(edge) + ' to ' +\
                          self.name
                info(infomsg)

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
            infomsg = 'orphan node ' + node + ' in ' + self.name +\
                      ' found in annotations but not added'
            info(infomsg)

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

    def _add_edge_annotation(self, edge, attrs):
        if edge in self.graph.edges:
            self.graph.edges[edge].update(attrs)
        else:
            warnmsg = 'adding unlabeled edge ' + str(edge) + ' to ' + self.name
            warning(warnmsg)
            self.graph.add_edges_from([(edge[0], edge[1], attrs)])

    @memoized_property
    def sentence(self) -> str:
        """The sentence annotated by this graph"""
        id_word = {nodeattr['position']-1: nodeattr['form']
                   for nodeid, nodeattr in self.syntax_nodes.items()}
        return ' '.join([id_word[i] for i in range(max(list(id_word.keys()))+1)])


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

    def add_annotation(self,
                   node_attrs: Dict[str, Dict[str, Any]],
                   edge_attrs: Dict[str, Dict[str, Any]]) -> None:
        """Add node and or edge annotations to the graph

        Parameters
        ----------
        node_attrs
            the node annotations to be added
        edge_attrs
            the edge annotations to be added
        """
        for node, attrs in node_attrs.items():
            self._add_node_annotation(node, attrs)

        for edge, attrs in edge_attrs.items():
            self._add_edge_annotation(edge, attrs)

    def _add_edge_annotation(self, edge, attrs):
        if edge in self.graph.edges:
            self.graph.edges[edge].update(attrs)
        else:
            # This will create edges dynamically
            attrs = dict(attrs, **{'domain': 'document',
                            'type': 'relation',
                            'frompredpatt': False,
                            'id': edge[1]})
        self.graph.add_edges_from([(edge[0], edge[1], attrs)])

    def _add_node_annotation(self, node, attrs):
        # We do not currently have a use case for document node annotations,
        # but it is included for completeness.
        if node in self.graph.nodes:
            warnmsg = f'Attempting to add a node annotation to node {node} '\
                      f'in document graph {self.name}. Document-level '\
                      'annotations should likely be edge attributes.'
            warning(warnmsg)
            self.graph.nodes[node].update(attrs)
        else:
            warnmsg = f'Attempting to add annotation to unknown node {node} '\
                      f'in document graph {self.name}'
            warning(warnmsg)
