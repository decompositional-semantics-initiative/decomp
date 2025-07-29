"""Universal Decompositional Semantics (UDS) representation framework.

This module provides a comprehensive framework for working with Universal Decompositional
Semantics (UDS) datasets. UDS is a semantic annotation framework that captures diverse
semantic properties of natural language texts through real-valued annotations on
predicate-argument structures.

The module is organized hierarchically:

- **Annotations** (:mod:`~decomp.semantics.uds.annotation`): Provides classes for handling
  UDS property annotations in both raw (multi-annotator) and normalized (aggregated) formats.

- **Graphs** (:mod:`~decomp.semantics.uds.graph`): Implements graph representations at
  sentence and document levels, integrating syntactic dependency structures with semantic
  annotations.

- **Documents** (:mod:`~decomp.semantics.uds.document`): Represents complete documents
  containing multiple sentences with their associated graphs and metadata.

- **Corpus** (:mod:`~decomp.semantics.uds.corpus`): Manages collections of UDS documents
  and provides functionality for loading, querying, and serializing UDS datasets.

Classes
-------
NormalizedUDSAnnotation
    Annotations with aggregated values and confidence scores from multiple annotators.

RawUDSAnnotation
    Annotations preserving individual annotator responses before aggregation.

UDSSentenceGraph
    Graph representation of a single sentence with syntax and semantics layers.

UDSDocumentGraph
    Graph connecting multiple sentence graphs within a document.

UDSDocument
    Container for sentence graphs and document-level annotations.

UDSCorpus
    Collection of UDS documents with support for various data formats and queries.

Notes
-----
The UDS framework builds upon the PredPatt system for extracting predicate-argument
structures and extends it with rich semantic annotations. All graph representations
use NetworkX for the underlying graph structure and support SPARQL queries via RDF
conversion.
"""

from .annotation import NormalizedUDSAnnotation, RawUDSAnnotation
from .corpus import UDSCorpus
from .document import UDSDocument
from .graph import UDSDocumentGraph, UDSSentenceGraph


__all__ = [
    'NormalizedUDSAnnotation',
    'RawUDSAnnotation',
    'UDSCorpus',
    'UDSDocument',
    'UDSDocumentGraph',
    'UDSSentenceGraph'
]
