"""Module for converting from networkx to RDF"""

from typing import Any
from networkx import DiGraph, to_dict_of_dicts
from rdflib import Graph, URIRef, Literal


class RDFConverter:
    """A converter between NetworkX digraphs and RDFLib graphs

    Parameters
    ----------
    nxgraph
        the graph to convert
    """

    SUBSPACES: dict[str, URIRef] = {}
    PROPERTIES: dict[str, URIRef] = {'domain': URIRef('domain'),
                                     'type': URIRef('type'),
                                     'subspace': URIRef('subspace'),
                                     'confidence': URIRef('confidence')}
    VALUES: dict[str, URIRef] = {}

    def __init__(self, nxgraph: DiGraph):
        self.nxgraph = nxgraph
        self.rdfgraph = Graph()
        self.nodes: dict[str, URIRef] = {}

    @classmethod
    def networkx_to_rdf(cls, nxgraph: DiGraph) -> Graph:
        """Convert a NetworkX digraph to an RDFLib graph

        Parameters
        ----------
        nxgraph
            the NetworkX graph to convert
        """

        converter = cls(nxgraph)

        nxdict = to_dict_of_dicts(nxgraph)

        for nodeid1, edgedict in nxdict.items():
            converter._add_node_attributes(nodeid1)
            for nodeid2 in edgedict:
                converter._add_node_attributes(nodeid2)
                converter._add_edge_attributes(nodeid1, nodeid2)

        return converter.rdfgraph

    def _add_node_attributes(self, nodeid: str) -> None:
        self._construct_node(nodeid)
        
        self._add_attributes(nodeid,
                             list(self.nxgraph.nodes[nodeid].items()))

        
    def _add_edge_attributes(self, nodeid1: str, nodeid2: str) -> None:
        edgeid = self._construct_edge(nodeid1, nodeid2)
        edgetup = (nodeid1, nodeid2)
        
        self._add_attributes(edgeid,
                             list(self.nxgraph.edges[edgetup].items()))
        

    def _add_attributes(self, nid: str, attributes: list[tuple[str, Any]]) -> None:
        triples = []
        
        for attrid1, attrs1 in attributes:
            if not isinstance(attrs1, dict):
                if isinstance(attrs1, list) or isinstance(attrs1, tuple):
                    errmsg = 'Cannot convert list- or tuple-valued' +\
                             ' attributes to RDF'
                    raise ValueError(errmsg)
                    
                triples += self._construct_property(nid,
                                                    attrid1,
                                                    attrs1)

            else:            
                for attrid2, attrs2 in attrs1.items():
                    triples += self._construct_property(nid,
                                                        attrid2,
                                                        attrs2,
                                                        attrid1)

        for t in triples:
            self.rdfgraph.add(t)                    
        
    def _construct_node(self, nodeid: str) -> None:        
        if nodeid not in self.nodes:
            self.nodes[nodeid] = URIRef(nodeid)

    def _construct_edge(self, nodeid1: str, nodeid2: str) -> str:
        edgeid = nodeid1 + '%%' + nodeid2

        if edgeid not in self.nodes:
            node1 = self.nodes[nodeid1]
            node2 = self.nodes[nodeid2]

            self.nodes[edgeid] = URIRef(edgeid)
            triple = (node1, self.nodes[edgeid], node2)

            self.rdfgraph.add(triple)
            
            return edgeid

        else:
            return edgeid

    def _construct_property(self, nodeid: str, propid: str, val: Any,
                            subspaceid: str | None = None) -> list[tuple[URIRef, URIRef, URIRef | Literal]]:

        c = self.__class__
        triples: list[tuple[URIRef, URIRef, URIRef | Literal]]
        
        if isinstance(val, dict) and subspaceid is not None:
            # We currently do not support querying on raw UDS
            # annotations, all of which have dict-valued 'value'
            # and 'confidence' fields.
            if isinstance(val['value'], dict) or isinstance(val['confidence'], dict):
                raise TypeError('Attempted query of graph with raw properties. Querying '\
                                'graphs with raw properties is prohibited.')
            triples = c._construct_subspace(subspaceid, propid)        
            triples += [(self.nodes[nodeid],
                         c.PROPERTIES[propid],
                         Literal(val['value'])),
                        (self.nodes[nodeid],
                         c.PROPERTIES[propid+'-confidence'],
                         Literal(val['confidence']))]

        elif propid in ['domain', 'type']:
            if val not in c.VALUES:
                c.VALUES[val] = URIRef(val)
            
            triples = [(self.nodes[nodeid],
                        c.PROPERTIES[propid],
                        c.VALUES[val])]

        else:
            if propid not in c.PROPERTIES:
                c.PROPERTIES[propid] = URIRef(propid)
            
            triples = [(self.nodes[nodeid],
                        c.PROPERTIES[propid],
                        Literal(val))]            
            
        return triples

    @classmethod
    def _construct_subspace(cls, subspaceid: str, propid: str) -> list[tuple[URIRef, URIRef, URIRef | Literal]]:
        if subspaceid not in cls.SUBSPACES:
            cls.SUBSPACES[subspaceid] = URIRef(subspaceid)
            
        if propid not in cls.PROPERTIES:
            cls.PROPERTIES[propid] = URIRef(propid)
            cls.PROPERTIES[propid+'-confidence'] = URIRef(propid+'-confidence')

        return [(cls.PROPERTIES[propid],
                 cls.PROPERTIES['subspace'],
                 cls.SUBSPACES[subspaceid]),
                (cls.PROPERTIES[propid+'-confidence'],
                 cls.PROPERTIES['subspace'],
                 cls.SUBSPACES[subspaceid]),                
                (cls.PROPERTIES[propid],
                 cls.PROPERTIES['confidence'],
                 cls.PROPERTIES[propid+'-confidence'])]
