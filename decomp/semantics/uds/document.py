"""Module for representing UDS documents with sentence-level and document-level graphs.

This module provides the UDSDocument class for managing Universal Decompositional Semantics
(UDS) documents. Each document contains:

- A collection of sentence-level graphs (UDSSentenceGraph)
- A document-level graph (UDSDocumentGraph) connecting nodes across sentences
- Metadata including document name, genre, and timestamp
- Methods for adding sentences and annotations to the document

The document structure preserves the hierarchical relationship between documents
and their constituent sentences while enabling document-level semantic annotations.
"""

import re
from functools import cached_property
from typing import TypeAlias, cast

from networkx import DiGraph

from .graph import EdgeAttributes, EdgeKey, NodeAttributes, UDSDocumentGraph, UDSSentenceGraph


# type aliases
SentenceGraphDict: TypeAlias = dict[str, UDSSentenceGraph]
"""Mapping from graph names to their UDSSentenceGraph objects."""

SentenceIDDict: TypeAlias = dict[str, str]
"""Mapping from graph names to their UD sentence identifiers."""


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

    def to_dict(self) -> dict[str, dict[str, dict[str, dict[str, int | bool | str]]]]:
        """Convert the document graph to a dictionary.

        Returns
        -------
        dict[str, dict[str, dict[str, dict[str, int | bool | str]]]]
            NetworkX adjacency data format for the document graph
        """
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
        """Extract timestamp from document name.

        Looks for patterns like 'YYYYMMDD_HHMMSS' or 'YYYYMMDDHHMMSS'
        in the document name.

        Parameters
        ----------
        document_name : str
            The document name to parse

        Returns
        -------
        str | None
            The timestamp string if found, None otherwise
        """
        timestamp = re.search(r'\d{8}_?\d{6}', document_name)
        
        return timestamp[0] if timestamp else None

    def add_sentence_graphs(
        self, 
        sentence_graphs: SentenceGraphDict,
        sentence_ids: SentenceIDDict
    ) -> None:
        """Add sentence graphs to the document.

        Creates document-level nodes for each semantics node in the sentence
        graphs and updates the sentence graph metadata with document information.

        Parameters
        ----------
        sentence_graphs : SentenceGraphDict
            Dictionary mapping graph names to UDSSentenceGraph objects
        sentence_ids : SentenceIDDict
            Dictionary mapping graph names to UD sentence identifiers
        """
        for gname, graph in sentence_graphs.items():
            sentence_graphs[gname].sentence_id = sentence_ids[gname]
            sentence_graphs[gname].document_id = self.name
            
            self.sentence_graphs[gname] = graph
            self.sentence_ids[gname] = sentence_ids[gname]
            
            for node_name, node in graph.semantics_nodes.items():
                semantics = {'graph': gname, 'node': node_name}
                document_node_name = node_name.replace('semantics', 'document')
                self.document_graph.graph.add_node(
                    document_node_name,
                    domain='document', type=node['type'],
                    frompredpatt=False, semantics=semantics
                )

    def add_annotation(
        self, 
        node_attrs: dict[str, NodeAttributes],
        edge_attrs: dict[EdgeKey, EdgeAttributes]
    ) -> None:
        """Add annotations to the document-level graph.

        Delegates to the document graph's add_annotation method, passing
        along the sentence IDs for validation.

        Parameters
        ----------
        node_attrs : dict[str, NodeAttributes]
            Node annotations keyed by node ID
        edge_attrs : dict[EdgeKey, EdgeAttributes]
            Edge annotations keyed by (source, target) tuples
        """
        self.document_graph.add_annotation(node_attrs, edge_attrs, self.sentence_ids)

    def semantics_node(self, document_node: str) -> dict[str, dict[str, int | bool | str]]:
        """Get the semantics node corresponding to a document node.

        Document nodes maintain references to their corresponding semantics
        nodes through the 'semantics' attribute, which contains the graph
        name and node ID.

        Parameters
        ----------
        document_node : str
            The document domain node ID

        Returns
        -------
        dict[str, dict[str, int | bool | str]]
            Single-item dict mapping node ID to its attributes

        Raises
        ------
        TypeError
            If the semantics attribute is not a dictionary
        KeyError
            If required keys are missing from semantics dict
        """
        semantics = self.document_graph.nodes[document_node]['semantics']
        if not isinstance(semantics, dict):
            raise TypeError(f"Expected 'semantics' to be a dict but got {type(semantics)}")
        if 'graph' not in semantics or 'node' not in semantics:
            raise KeyError("Expected 'semantics' dict to have 'graph' and 'node' keys")
        graph_id = cast(str, semantics['graph'])
        node_id = cast(str, semantics['node'])
        semantics_node = self.sentence_graphs[graph_id].semantics_nodes[node_id]
        return {node_id: semantics_node}

    @cached_property
    def text(self) -> str:
        """The full document text reconstructed from sentences.

        Concatenates the text from all sentence graphs in sorted order
        with space separation.

        Returns
        -------
        str
            The complete document text
        """
        return ' '.join([
            sent_graph.sentence 
            for gname, sent_graph in sorted(self.sentence_graphs.items())
        ])
