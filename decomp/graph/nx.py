"""Module for converting from networkx to RDF"""

from networkx import DiGraph
from rdflib import Graph


class NXConverter:
    """A converter between RDFLib graphs and NetworkX digraphs

    Parameters
    ----------
    graph
        the graph to convert
    """

    def __init__(self, rdfgraph: Graph):
        self.nxgraph = DiGraph()
        self.rdfgraph = rdfgraph

    @classmethod
    def rdf_to_networkx(cls, rdfgraph: Graph) -> DiGraph:
        """Convert an RDFLib graph to a NetworkX digraph

        Parameters
        ----------
        rdfgraph
            the RDFLib graph to convert
        """
        converter = cls(rdfgraph)

        raise NotImplementedError

        # nxdict = to_dict_of_dicts(nxgraph)

        # for nodeid1, edgedict in nxdict.items():
        #     converter._add_node_attributes(nodeid1)

        #     for nodeid2, properties in edgedict.items():
        #         converter._add_node_attributes(nodeid2)
        #         converter._add_edge_attributes(nodeid1, nodeid2, properties)

        # cls._reset_attributes()

        # return converter.rdfgraph

    # def _add_node_attributes(self, nodeid):
    #     for propid, val in self.nxgraph.nodes[nodeid].items():
    #         triple = self.__class__._construct_property(nodeid, propid, val)
    #         self.rdfgraph.add(triple)

    # def _add_edge_attributes(self, nodeid1, nodeid2, properties):
    #     triple = self.__class__._construct_edge(nodeid1, nodeid2)
    #     self.rdfgraph.add(triple)

    #     edgeid = triple[1]

    #     for propid, val in properties.items():
    #         triple = self.__class__._construct_property(edgeid, propid, val)
    #         self.rdfgraph.add(triple)

    # @classmethod
    # def _construct_node(cls, nodeid):
    #     if nodeid not in cls.NODES:
    #         cls.NODES[nodeid] = URIRef(nodeid)

    #     return cls.NODES[nodeid]

    # @classmethod
    # def _construct_edge(cls, nodeid1, nodeid2):
    #     node1 = cls._construct_node(nodeid1)
    #     node2 = cls._construct_node(nodeid2)

    #     edgeid = nodeid1 + '%%' + nodeid2

    #     if edgeid not in cls.EDGES:
    #         cls.EDGES[edgeid] = URIRef(edgeid)

    #     return (node1, cls.EDGES[edgeid], node2)

    # @classmethod
    # def _construct_property(cls, nodeid, propid, val):
    #     if nodeid not in cls.NODES:
    #         cls.NODES[nodeid] = URIRef(nodeid)

    #     if propid not in cls.NODES:
    #         cls.PROPERTIES[propid] = URIRef(propid)

    #     if propid in ['type', 'subtype']:
    #         if val not in cls.VALUES:
    #             cls.VALUES[val] = URIRef(val)

    #         return (cls.NODES[nodeid],
    #                 cls.PROPERTIES[propid],
    #                 cls.VALUES[val])

    #     else:
    #         return (cls.NODES[nodeid],
    #                 cls.PROPERTIES[propid],
    #                 Literal(val))

    # @classmethod
    # def _reset_attributes(cls):
    #     cls.NODES = {}
    #     cls.EDGES = {}
