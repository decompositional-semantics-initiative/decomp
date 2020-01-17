# pylint: disable=W0102
# pylint: disable=W0212
# pylint: disable=W0221
# pylint: disable=W0231
# pylint: disable=W0640
# pylint: disable=C0103
"""Module for containing representing UDS graphs"""

import os
import json
import requests

from pkg_resources import resource_filename
from os.path import basename, splitext
from glob import glob
from logging import info, warning
from functools import lru_cache
from typing import Union, Optional, Any, TextIO
from typing import Dict, List, Tuple, Set
from io import BytesIO
from zipfile import ZipFile
from memoized_property import memoized_property
from pyparsing import ParseException
from rdflib import Graph
from rdflib.query import Result
from rdflib.plugins.sparql.sparql import Query
from rdflib.plugins.sparql import prepareQuery
from networkx import DiGraph, adjacency_data, adjacency_graph
from .predpatt import PredPattCorpus
from ..graph import RDFConverter


class UDSCorpus(PredPattCorpus):
    """A collection of Universal Decompositional Semantics graphs

    Parameters
    ----------
    graphs
        the predpatt graphs to associate the annotations with
    annotations
        additional annotations to associate with predpatt nodes; in
        most cases, no such annotations will be passed, since the
        standard UDS annotations are automatically loaded
    split
        the split to load: "train", "dev", or "test"
    """

    DATA_DIR = resource_filename('decomp', 'data/')

    def __init__(self,
                 graphs: Optional[PredPattCorpus] = None,
                 annotations: List['UDSDataset'] = [],
                 version: str = '1.0',
                 split: Optional[str] = None):

        self.version = version

        self._corpus_paths = {splitext(basename(p))[0].split('-')[-1]: p
                              for p
                              in glob(os.path.join(self.__class__.DATA_DIR,
                                                   version,
                                                   '*.json'))}

        
        self._annotation_dir = os.path.join(self.__class__.DATA_DIR,
                                            version,
                                            'annotations/')
        self._annotation_paths = glob(os.path.join(self._annotation_dir,
                                                   '*.json'))

        
        if not (split is None or split in ['train', 'dev', 'test']):
            errmsg = 'split must be "train", "dev", or "test"'
            raise ValueError(errmsg)

        all_built = all(s in self._corpus_paths
                        for s in ['train', 'dev', 'test'])

        self._graphs = {}
        
        if graphs is None and split in self._corpus_paths:
            fpath = self._corpus_paths[split]
            corp_split = self.__class__.from_json(fpath)
            self._graphs.update(corp_split._graphs)

        elif graphs is None and split is None and all_built:
            for fpath in self._corpus_paths.values():
                corp_split = self.__class__.from_json(fpath)
                self._graphs.update(corp_split._graphs)

        elif graphs is None:
            url = 'https://github.com/UniversalDependencies/' +\
                  'UD_English-EWT/archive/r1.2.zip'

            udewt = requests.get(url).content

            with ZipFile(BytesIO(udewt)) as zf:
                conll_names = [fname for fname in zf.namelist()
                               if splitext(fname)[-1] == '.conllu']

                for fn in conll_names:
                    with zf.open(fn) as conll:
                        conll_str = conll.read().decode('utf-8')
                        sname = splitext(basename(fn))[0].split('-')[-1]
                        spl = self.__class__.from_conll(conll_str,
                                                        self._annotation_paths,
                                                        name='ewt-'+sname)

                        # in case additional annotations are passed;
                        # this should generally NOT happen, since this
                        # branch is only entered on first build, but
                        # if someone imported this class directly from
                        # the semantics module without first building
                        # the dataset, they could in principle try to
                        # pass annotations, so we want to do something
                        # reasonable here
                        for ann in annotations:
                            spl.add_annotation(ann)

                        if sname == split or split is None:
                            json_name = 'uds-ewt-'+sname+'.json'
                            json_path = os.path.join(self.__class__.DATA_DIR,
                                                     version,
                                                     json_name)
                            spl.to_json(json_path)
                            self._graphs.update(spl._graphs)

                            self._corpus_paths[sname] = json_path

        else:
            self._graphs = graphs

            for ann in annotations:
                self.add_annotation(ann)

    @classmethod
    def from_conll(cls,
                   corpus: Union[str, TextIO],
                   annotations: List[Union[str, TextIO]] = [],
                   name: str = 'ewt') -> 'UDSCorpus':
        """Load UDS graph corpus from CoNLL (dependencies) and JSON (annotations)

        This method should only be used if the UDS corpus is being
        (re)built. Otherwise, loading the corpus from the JSON shipped
        with this package using UDSCorpus.__init__ or
        UDSCorpus.from_json is suggested.

        Parameters
        ----------
        corpus
            (path to) Universal Dependencies corpus in conllu format
        annotations
            (paths to) annotations in JSON
        name
            corpus name to be appended to the beginning of graph ids
        """

        predpatt_corpus = PredPattCorpus.from_conll(corpus, name=name)
        predpatt_graphs = {name: UDSGraph(g, name)
                           for name, g in predpatt_corpus.items()}

        annotations = [UDSDataset.from_json(ann) for ann in annotations]

        return cls(predpatt_graphs, annotations)

    @classmethod
    def from_json(cls, jsonfile: Union[str, TextIO]) -> 'UDSCorpus':
        """Load annotated UDS graph corpus (including annotations) from JSON

        This is the suggested method for loading the UDS corpus.

        Parameters
        ----------
        jsonfile
            file containing Universal Decompositional Semantics corpus
            in JSON format
        """

        ext = splitext(basename(jsonfile))[-1]

        if isinstance(jsonfile, str) and ext == '.json':
            with open(jsonfile) as infile:
                graphs_json = json.load(infile)

        elif isinstance(jsonfile, str):
            graphs_json = json.loads(jsonfile)

        else:
            graphs_json = json.load(jsonfile)

        graphs = {name: UDSGraph.from_dict(g_json, name)
                  for name, g_json in graphs_json.items()}

        return cls(graphs)

    def add_annotation(self, annotation: 'UDSDataset') -> None:
        """Add annotations to UDS graphs in the corpus

        Parameters
        ----------
        annotation
            the annotations to add to the graphs in the corpus
        """

        for gname, (node_attrs, edge_attrs) in annotation.items():
            if gname in self._graphs:
                self._graphs[gname].add_annotation(node_attrs, edge_attrs)

    def to_json(self,
                outfile: Optional[Union[str, TextIO]] = None) -> Optional[str]:
        """Serialize corpus to json

        Parameters
        ----------
        outfile
            file to write corpus to
        """

        graphs_serializable = {name: graph.to_dict()
                               for name, graph in self.graphs.items()}

        if outfile is None:
            return json.dumps(graphs_serializable)

        elif isinstance(outfile, str):
            with open(outfile, 'w') as out:
                json.dump(graphs_serializable, out)

        else:
            json.dump(graphs_serializable, outfile)

    @lru_cache(maxsize=128)
    def query(self, query: Union[str, Query],
              query_type: Optional[str] = None,
              cache_query: bool = True,
              cache_rdf: bool = True) -> Union[Result,
                                               Dict[str,
                                                    Dict[str, Any]]]:
        """Query all graphs in the corpus using SPARQL 1.1

        Parameters
        ----------
        query
            a SPARQL 1.1 query
        query_type
            whether this is a 'node' query or 'edge' query. If set to
            None (default), a Results objects will be returned. The
            main reason to use this option is to automatically format
            the output of a custom query, since Results objects
            require additional postprocessing.
        cache_query
            whether to cache the query. This should usually be set to
            True. It should generally only be False when querying
            particular nodes or edges--e.g. as in precompiled queries.
        clear_rdf
            whether to delete the RDF constructed for querying
            against. This will slow down future queries but saves a
            lot of memory
        """

        return {gid: graph.query(query, query_type,
                                 cache_query, cache_rdf)
                for gid, graph in self.items()}
            
    @memoized_property
    def semantic_node_type_subspaces(self) -> Dict[str, Set[str]]:
        """The UDS node type subspaces in the corpus"""

        tups = set((k, frozenset(v))
                   for g in self._graphs.values()
                   for _, attrs in g.semantics_nodes.items()
                   for k, v in attrs.items()
                   if isinstance(v, dict))

        subspaces = set(k for k, _ in tups)
        
        return {k1: set(k2
                        for k, v in tups
                        for k2 in v
                        if k == k1)
                for k1 in subspaces}

    @memoized_property
    def semantic_edge_type_subspaces(self) -> Dict[str, Set[str]]:
        """The UDS edge type subspaces in the corpus"""

        tups = set((k, frozenset(v))
                   for g in self._graphs.values()
                   for _, attrs in g.semantics_edges().items()
                   for k, v in attrs.items()
                   if isinstance(v, dict))

        subspaces = set(k for k, _ in tups)
        
        return {k1: set(k2
                        for k, v in tups
                        for k2 in v
                        if k == k1)
                for k1 in subspaces}

    @memoized_property
    def semantic_type_subspaces(self) -> Dict[str, Set[str]]:
        """The UDS type subspaces in the corpus"""

        return dict(self.semantic_node_type_subspaces,
                    **self.semantic_edge_type_subspaces)


class UDSGraph:
    """A Universal Decompositional Semantics graph

    Parameters
    ----------
    graph
    name
    """

    QUERIES = {}

    def __init__(self, graph: DiGraph, name: str):
        self.name = name
        self.graph = graph

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
            None (default), a Results objects will be returned. The
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

        if not cache_rdf:
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
    def sentence(self) -> str:
        """The sentence the graph annotates"""

        return self.graph.nodes[self.rootid]['sentence']

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

    def to_dict(self) -> Dict:
        """Convert the graph to a dictionary"""

        return adjacency_data(self.graph)

    @property
    def nodes(self):
        """All the nodes in the graph"""
        
        return self.graph.nodes

    @property
    def edges(self):
        """All the edges in the graph"""        
        return self.graph.edges
    
    @classmethod
    def from_dict(cls, graph: Dict, name: str = 'UDS') -> 'UDSGraph':
        """Construct a UDSGraph from a dictionary

        Parameters
        ----------
        graph
            a dictionary constructed by networkx.adjacency_data
        name
            identifier to append to the beginning of node ids
        """

        return cls(adjacency_graph(graph), name)

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


class UDSDataset:
    """A Universal Decompositional Semantics dataset

    Parameters
    ----------
    annotation
        mapping from node ids or pairs of node ids separated by %% to
        attribute-value pairs; node ids must not contain %%
    """

    CACHE = {}

    def __init__(self, annotation: Dict[str, Dict[str, Any]]):
        self.annotation = annotation

        self.node_attributes = {gname: {node: a
                                        for node, a in attrs.items()
                                        if '%%' not in node}
                                for gname, attrs in self.annotation.items()}

        self.edge_attributes = {gname: {tuple(edge.split('%%')): a
                                        for edge, a in attrs.items()
                                        if '%%' in edge}
                                for gname, attrs in self.annotation.items()}

    def __getitem__(self, k):
        node_attrs = self.node_attributes[k]
        edge_attrs = self.edge_attributes[k]

        return node_attrs, edge_attrs

    def items(self):
        """Dictionary-like items generator for attributes

        Yields node_attributes for a node as well as the attributes for
        all edges that touch it
        """

        for name, node_attrs in self.node_attributes.items():
            yield name, (node_attrs, self.edge_attributes[name])

    @classmethod
    def from_json(cls, jsonfile: Union[str, TextIO]) -> 'UDSDataset':
        """Load Universal Decompositional Semantics dataset from JSON

        The format of the JSON passed to this class method must be:

        ::

            {GRAPHID_1: {NODEID_1_1: {ATTRIBUTE_I: VALUE,
                                      ATTRIBUTE_J: VALUE,
                                      ...},
                         ...},
             GRAPHID_2: {NODEID_2_1: {ATTRIBUTE_K: VALUE,
                                      ATTRIBUTE_L: VALUE,
                                      ...},
                         ...},
             ...
            }


        Graph and node identifiers must match the graph and node
        identifiers of the predpatt graphs to which the annotations
        will be added.

        VALUE in the above may be anything, but if it is
        dictionary-valued, it is assumed to have the following
        structure:

        ::

            {SUBSPACE_1: {PROP_1_1: {VER_1_1_1: {'value': VALUE,
                                                 'confidence': VALUE},
                                     VER_1_1_2: {'value': VALUE,
                                                 'confidence': VALUE},
                                      ...},
                         ...},
             SUBSPACE_2: {PROP_2_1: {VER_2_1_1: {'value': VALUE,
                                                 'confidence': VALUE},
                                     VER_2_1_2: {'value': VALUE,
                                                 'confidence': VALUE},
                                      ...},
                         ...},
            }

        Parameters
        ----------
        jsonfile
            (path to) file containing annotations as JSON
        """

        if jsonfile in cls.CACHE:
            return cls.CACHE[jsonfile]

        ext = splitext(basename(jsonfile))[-1]

        if isinstance(jsonfile, str) and ext == '.json':
            with open(jsonfile) as infile:
                annotation = json.load(infile)

        elif isinstance(jsonfile, str):
            annotation = json.loads(jsonfile)

        else:
            annotation = json.load(jsonfile)

        cls.CACHE[jsonfile] = cls(annotation)

        return cls.CACHE[jsonfile]
