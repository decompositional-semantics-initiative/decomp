"""Module for representing UDS documents."""

import re
from typing import Any, TypeAlias, cast

from memoized_property import memoized_property
from networkx import DiGraph

from .graph import UDSDocumentGraph, UDSSentenceGraph


# Type aliases
SentenceGraphDict: TypeAlias = dict[str, UDSSentenceGraph]
SentenceIDDict: TypeAlias = dict[str, str]


class UDSDocument:
    """A Universal Decompositional Semantics document

    Parameters
    ----------
    sentence_graphs
        the UDSSentenceGraphs associated with each sentence in the document
    sentence_ids
        the UD sentence IDs for each graph
    name
        the name of the document (i.e. the UD document ID)
    genre
        the genre of the document (e.g. `weblog`)
    timestamp
        the timestamp of the UD document on which this UDSDocument is based
    doc_graph
        the NetworkX DiGraph for the document. If not provided, this will be
        initialized without edges from sentence_graphs
    """

    def __init__(self, sentence_graphs: SentenceGraphDict,
                 sentence_ids: SentenceIDDict, name: str, genre: str,
                 timestamp: str | None = None, doc_graph: UDSDocumentGraph | None = None):
        self.sentence_graphs: SentenceGraphDict = {}
        self.sentence_ids: SentenceIDDict = {}
        self.name = name
        self.genre = genre
        self.timestamp = timestamp

        # Initialize the document-level graph
        if doc_graph:
            self.document_graph = doc_graph
        else:
            self.document_graph = UDSDocumentGraph(DiGraph(), name)

        # Initialize the sentence-level graphs
        self.add_sentence_graphs(sentence_graphs, sentence_ids)

    def to_dict(self) -> dict:
        """Convert the graph to a dictionary"""
        return self.document_graph.to_dict()

    @classmethod
    def from_dict(cls, document: dict[str, dict], sentence_graphs: dict[str, UDSSentenceGraph],
                       sentence_ids: dict[str, str], name: str = 'UDS') -> 'UDSDocument':
        """Construct a UDSDocument from a dictionary

        Since only the document graphs are serialized, the sentence
        graphs must also be provided to this method call in order
        to properly associate them with their documents.

        Parameters
        ----------
        document
            a dictionary constructed by networkx.adjacency_data,
            containing the graph for the document
        sentence_graphs
            a dictionary containing (possibly a superset of) the
            sentence-level graphs for the sentences in the document
        sentence_ids
            a dictionary containing (possibly a superset of) the
            UD sentence IDs for each graph
        name
            identifier to append to the beginning of node ids
        """
        document_graph = cast(UDSDocumentGraph, UDSDocumentGraph.from_dict(document, name))
        sent_graph_names = set(map(lambda node: node['semantics']['graph'], document['nodes']))
        sent_graphs = {}
        sent_ids = {}
        for gname in sent_graph_names:
            sentence_graphs[gname].document_id = name
            sentence_graphs[gname].sentence_id = sentence_ids[gname]
            sent_graphs[gname] = sentence_graphs[gname]
            sent_ids[gname] = sentence_ids[gname]
        genre = name.split('-')[0]
        timestamp = cls._get_timestamp_from_document_name(name)
        return cls(sent_graphs, sent_ids, name, genre, timestamp, document_graph)

    @staticmethod
    def _get_timestamp_from_document_name(document_name: str) -> str | None:
        timestamp = re.search(r'\d{8}_?\d{6}', document_name)
        return timestamp[0] if timestamp else None

    def add_sentence_graphs(self, sentence_graphs: SentenceGraphDict,
                                  sentence_ids: SentenceIDDict) -> None:
        """Add additional sentences to a document

        Parameters
        ----------
        sentence_graphs
            a dictionary containing the sentence-level graphs
            for the sentences in the document
        sentence_ids
            a dictionary containing the UD sentence IDs for each graph
        name
            identifier to append to the beginning of node ids
        """
        for gname, graph in sentence_graphs.items():
            sentence_graphs[gname].sentence_id = sentence_ids[gname]
            sentence_graphs[gname].document_id = self.name
            self.sentence_graphs[gname] = graph
            self.sentence_ids[gname] = sentence_ids[gname]
            for node_name, node in graph.semantics_nodes.items():
                semantics = {'graph': gname, 'node': node_name}
                document_node_name = node_name.replace('semantics', 'document')
                self.document_graph.graph.add_node(document_node_name,
                            domain='document', type=node['type'],
                            frompredpatt=False, semantics=semantics)

    def add_annotation(self, node_attrs: dict[str, dict[str, Any]],
                             edge_attrs: dict[str, dict[str, Any]]) -> None:
        """Add node or edge annotations to the document-level graph

        Parameters
        ----------
        node_attrs
            the node annotations to be added
        edge_attrs
            the edge annotations to be added
        """
        self.document_graph.add_annotation(node_attrs, edge_attrs, self.sentence_ids)

    def semantics_node(self, document_node: str) -> dict[str, dict]:
        """The semantics node for a given document node

        Parameters
        ----------
        document_node
            the document domain node whose semantics node is to be
            retrieved
        """
        semantics = self.document_graph.nodes[document_node]['semantics']
        semantics_node = self.sentence_graphs[semantics['graph']].semantics_nodes[semantics['node']]
        return {semantics['node']: semantics_node}

    @memoized_property  # type: ignore[misc]
    def text(self) -> str:
        """The document text"""
        return ' '.join([sent_graph.sentence for gname, sent_graph in sorted(self.sentence_graphs.items())])
