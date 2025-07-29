"""Module for representing UDS corpora with sentence and document collections.

This module provides the UDSCorpus class for managing collections of Universal
Decompositional Semantics (UDS) graphs at both sentence and document levels.
It includes:

- Loading corpora from various formats (CoNLL, JSON)
- Managing sentence-level and document-level graphs
- Adding annotations to existing graphs
- Querying graphs using SPARQL
- Serialization and deserialization functionality

The UDSCorpus extends PredPattCorpus to support UDS-specific annotations and
document-level semantic relationships.
"""

import importlib.resources
import json
import os
from collections.abc import Callable, Sequence
from functools import lru_cache
from glob import glob
from io import BytesIO
from logging import warn
from os.path import basename, splitext
from random import sample
from typing import TextIO, TypeAlias, cast
from zipfile import ZipFile

import requests
from rdflib.plugins.sparql.sparql import Query
from rdflib.query import Result

from ..predpatt import PredPattCorpus
from .annotation import NormalizedUDSAnnotation, RawUDSAnnotation, UDSAnnotation
from .document import SentenceGraphDict, UDSDocument
from .graph import EdgeAttributes, EdgeKey, NodeAttributes, UDSSentenceGraph
from .metadata import UDSCorpusMetadata, UDSPropertyMetadata


Location: TypeAlias = str | TextIO
"""File location as either a file path string or an open file handle."""


class UDSCorpus(PredPattCorpus):
    """A collection of Universal Decompositional Semantics graphs

    Parameters
    ----------
    sentences
        the predpatt sentence graphs to associate the annotations with
    documents
        the documents associated with the predpatt sentence graphs
    sentence_annotations
        additional annotations to associate with predpatt nodes on
        sentence-level graphs; in most cases, no such annotations
        will be passed, since the standard UDS annotations are 
        automatically loaded
    document_annotations
        additional annotations to associate with predpatt nodes on
        document-level graphs
    version
        the version of UDS datasets to use
    split
        the split to load: "train", "dev", or "test"
    annotation_format
        which annotation type to load ("raw" or "normalized")
    """

    UD_URL = 'https://github.com/UniversalDependencies/' +\
             'UD_English-EWT/archive/r1.2.zip'
    ANN_DIR = str(importlib.resources.files('decomp') / 'data')
    CACHE_DIR = str(importlib.resources.files('decomp') / 'data')

    def __init__(self,
                 sentences: PredPattCorpus | None = None,
                 documents: dict[str, UDSDocument] | None = None,
                 sentence_annotations: list[UDSAnnotation] = [],
                 document_annotations: list[UDSAnnotation] = [],
                 version: str = '2.0',
                 split: str | None = None,
                 annotation_format: str = 'normalized'):
        self._validate_arguments(sentences, documents,
                                 version, split, annotation_format)

        self.version = version
        self.annotation_format = annotation_format

        self._metadata = UDSCorpusMetadata()

        # methods inherited from Corpus that reference the self._graphs
        # attribute will operate on sentence-level graphs only
        # more specific type than parent's dict[Hashable, OutGraph]
        # we're intentionally narrowing the type from the parent class
        self._graphs: SentenceGraphDict = {}  # type: ignore[assignment] # narrowing parent's dict[Hashable, Any] to dict[str, UDSSentenceGraph]
        self._sentences = self._graphs
        self._documents: dict[str, UDSDocument] = {}

        self._initialize_paths(version, annotation_format)
        all_built = self._check_build_status()

        if sentences is None and split in self._sentences_paths:
            self._load_split(split)

        elif sentences is None and split is None and all_built:
            for split in ['train', 'dev', 'test']:
                self._load_split(split)

        elif sentences is None:
            # download UD-EWT
            udewt = requests.get(self.UD_URL).content

            if sentence_annotations or document_annotations:
                warn("sentence and document annotations ignored")

            self._process_conll(split, udewt)

        else:
            if isinstance(sentences, PredPattCorpus):
                self._sentences = {str(name): UDSSentenceGraph(g, str(name))
                                  for name, g in sentences.items()}
                self._graphs = self._sentences

            self._documents = documents or {}

            if sentence_annotations:
                for ann in sentence_annotations:
                    self.add_annotation(ann)

            if document_annotations:
                for ann in document_annotations:
                    self.add_annotation(document_annotation=ann)

    def _validate_arguments(self, sentences: PredPattCorpus | None, documents: dict[str, UDSDocument] | None,
                            version: str, split: str | None, annotation_format: str) -> None:
        """Validate constructor arguments for consistency.

        Parameters
        ----------
        sentences : PredPattCorpus | None
            Optional sentence graphs
        documents : dict[str, UDSDocument] | None
            Optional document collection
        version : str
            UDS version
        split : str | None
            Data split (train/dev/test)
        annotation_format : str
            Format (raw/normalized)

        Raises
        ------
        ValueError
            If arguments are inconsistent or invalid
        """
        # neither documents nor graphs should be supplied to the constructor
        # without the other
        if sentences is None and documents is not None:
            raise ValueError(
                'UDS documents were provided without sentences. '
                'Cannot construct corpus.'
            )

        elif sentences is not None and documents is None:
            raise ValueError(
                'UDS sentences were provided without documents. '
                'Cannot construct corpus.'
            )

        if not (split is None or split in ['train', 'dev', 'test']):
            raise ValueError('split must be "train", "dev", or "test"')

        if annotation_format not in ['raw', 'normalized']:
            raise ValueError(
                f'Unrecognized annotation format {annotation_format}. '
                'Must be either "raw" or "normalized".'
            )

    def _initialize_paths(self, version: str, annotation_format: str) -> None:
        """Initialize file paths for data loading.

        Sets up paths for sentence/document graphs and annotations based on
        version and format. Extracts zip files if needed.

        Parameters
        ----------
        version : str
            UDS dataset version
        annotation_format : str
            'raw' or 'normalized' format
        """
        self._sentences_paths = {splitext(basename(p))[0].split('-')[-2]: p
                                 for p
                                 in glob(os.path.join(self.CACHE_DIR,
                                                      version,
                                                      annotation_format,
                                                      'sentence',
                                                      '*.json'))}

        self._documents_paths = {splitext(basename(p))[0].split('-')[-2]: p
                                 for p
                                 in glob(os.path.join(self.CACHE_DIR,
                                                      version,
                                                      annotation_format,
                                                      'document',
                                                      '*.json'))}

        self._sentences_annotation_dir = os.path.join(self.ANN_DIR,
                                                      version,
                                                      annotation_format,
                                                      'sentence',
                                                      'annotations')

        self._documents_annotation_dir = os.path.join(self.ANN_DIR,
                                                      version,
                                                      annotation_format,
                                                      'document',
                                                      'annotations')

        sent_ann_paths = glob(os.path.join(self._sentences_annotation_dir,
                                           '*.json'))
        doc_ann_paths = glob(os.path.join(self._documents_annotation_dir,
                                          '*.json'))

        # out of the box, the annotations are stored as zip files and the
        # JSON they contain must be extracted
        if not sent_ann_paths:
            zipped_sent_paths = os.path.join(self._sentences_annotation_dir,
                                             '*.zip')
            zipped_sentence_annotations = glob(zipped_sent_paths)

            for zipped in zipped_sentence_annotations:
                ZipFile(zipped).extractall(path=self._sentences_annotation_dir)

            sent_ann_paths = glob(os.path.join(self._sentences_annotation_dir,
                                               '*.json'))

        if not doc_ann_paths:
            zipped_doc_paths = os.path.join(self._documents_annotation_dir,
                                            '*.zip')

            zipped_document_annotations = glob(zipped_doc_paths)

            for zipped in zipped_document_annotations:
                ZipFile(zipped).extractall(path=self._documents_annotation_dir)

            doc_ann_paths = glob(os.path.join(self._documents_annotation_dir,
                                              '*.json'))

        self._sentence_annotation_paths = sent_ann_paths
        self._document_annotation_paths = doc_ann_paths

    def _check_build_status(self) -> bool:
        """Check if all data splits are built and available.

        Returns
        -------
        bool
            True if train/dev/test splits are all available
        """
        sentences_built = bool(self._sentences_paths) and \
                          all(s in self._sentences_paths
                              for s in ['train', 'dev', 'test'])
        documents_built = bool(self._documents_paths) and \
                          all(s in self._documents_paths
                              for s in ['train', 'dev', 'test'])

        return sentences_built and documents_built

    def _load_split(self, split: str) -> None:
        """Load a specific data split into the corpus.

        Parameters
        ----------
        split : str
            Split name ('train', 'dev', or 'test')
        """
        sentence_fpath = self._sentences_paths[split]
        doc_fpath = self._documents_paths[split]
        split_corpus = self.__class__.from_json(sentence_fpath, doc_fpath)

        self._metadata += split_corpus.metadata

        self._sentences.update(split_corpus._sentences)
        self._documents.update(split_corpus._documents)

    def _process_conll(self, split: str | None, udewt: bytes) -> None:
        """Process CoNLL data from UD-EWT archive.

        Extracts and processes CoNLL files, creates UDS graphs, and saves
        to cache.

        Parameters
        ----------
        split : str | None
            Specific split to process, or None for all
        udewt : bytes
            UD-EWT archive content
        """
        with ZipFile(BytesIO(udewt)) as zf:
            conll_names = [fname for fname in zf.namelist()
                           if splitext(fname)[-1] == '.conllu']

            for fn in conll_names:
                with zf.open(fn) as conll:
                    conll_str = conll.read().decode('utf-8')
                    sname = splitext(basename(fn))[0].split('-')[-1]
                    spl = self.__class__.from_conll_and_annotations(conll_str,
                                                                    self._sentence_annotation_paths,
                                                                    self._document_annotation_paths,
                                                                    annotation_format=self.annotation_format,
                                                                    version=self.version,
                                                                    name='ewt-'+sname)

                    if sname == split or split is None:
                        # add metadata
                        self._metadata += spl.metadata

                        # prepare sentences
                        sentences_json_name = '-'.join(['uds', 'ewt', 'sentences',
                                                        sname, self.annotation_format]) +\
                                              '.json'
                        sentences_json_path = os.path.join(self.__class__.CACHE_DIR,
                                                           self.version,
                                                           self.annotation_format,
                                                           'sentence',
                                                           sentences_json_name)

                        self._sentences.update(spl._sentences)
                        self._sentences_paths[sname] = sentences_json_path

                        # prepare documents
                        documents_json_name = '-'.join(['uds', 'ewt', 'documents',
                                                        sname, self.annotation_format]) +\
                                              '.json'
                        documents_json_path = os.path.join(self.__class__.CACHE_DIR,
                                                           self.version,
                                                           self.annotation_format,
                                                           'document',
                                                           documents_json_name)

                        self._documents.update(spl._documents)
                        self._documents_paths[sname] = documents_json_path

                        # serialize both
                        spl.to_json(sentences_json_path, documents_json_path)

    @classmethod
    def from_conll_and_annotations(cls,
                                   corpus: Location,
                                   sentence_annotations: Sequence[Location] = [],
                                   document_annotations: Sequence[Location] = [],
                                   annotation_format: str = 'normalized',
                                   version: str = '2.0',
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
        sentence_annotations
            a list of paths to JSON files or open JSON files containing
            sentence-level annotations
        document_annotations
            a list of paths to JSON files or open JSON files containing
            document-level annotations
        annotation_format
            Whether the annotation is raw or normalized
        version
            the version of UDS datasets to use
        name
            corpus name to be appended to the beginning of graph ids
        """
        # select appropriate loader based on format
        loader: Callable[[str | TextIO], RawUDSAnnotation | NormalizedUDSAnnotation]
        if annotation_format == 'raw':
            loader = RawUDSAnnotation.from_json
        elif annotation_format == 'normalized':
            loader = NormalizedUDSAnnotation.from_json
        else:
            raise ValueError('annotation_format must be either'
                             '"raw" or "normalized"')

        predpatt_corpus = PredPattCorpus.from_conll(corpus, name=name)
        predpatt_sentence_graphs = {str(graph_name): UDSSentenceGraph(g, str(graph_name))
                                    for graph_name, g in predpatt_corpus.items()}
        predpatt_documents = cls._initialize_documents(predpatt_sentence_graphs)

        # process sentence-level graph annotations
        processed_sentence_annotations = []

        for ann_path in sentence_annotations:
            ann = loader(ann_path)
            processed_sentence_annotations.append(ann)

        # process document-level graph annotations
        processed_document_annotations = []

        for ann_path in document_annotations:
            ann = loader(ann_path)
            processed_document_annotations.append(ann)

        # create corpus and add annotations after creation
        # cast needed because constructor expects PredPattCorpus but we have dict[str, UDSSentenceGraph]
        uds_corpus: UDSCorpus = cls(cast(PredPattCorpus | None, predpatt_sentence_graphs), predpatt_documents)

        # add sentence annotations
        for ann in processed_sentence_annotations:
            uds_corpus.add_sentence_annotation(ann)

        # add document annotations
        for ann in processed_document_annotations:
            uds_corpus.add_document_annotation(ann)

        return uds_corpus

    @classmethod
    def _load_ud_ids(cls, sentence_ids_only: bool = False) -> dict[str, dict[str, str]] | dict[str, str]:
        """Load Universal Dependencies IDs for sentences and documents.

        Parameters
        ----------
        sentence_ids_only : bool, optional
            If True, return only sentence IDs. Default is False.

        Returns
        -------
        dict[str, dict[str, str]] | dict[str, str]
            Full ID mapping or just sentence IDs based on parameter
        """
        # load in the document and sentence IDs for each sentence-level graph
        ud_ids_path = os.path.join(cls.ANN_DIR, 'ud_ids.json')

        with open(ud_ids_path) as ud_ids_file:
            ud_ids: dict[str, dict[str, str]] = json.load(ud_ids_file)

            if sentence_ids_only:
                return {k: v['sentence_id'] for k, v in ud_ids.items()}

            else:
                return ud_ids

    @classmethod
    def from_json(cls, sentences_jsonfile: Location,
                  documents_jsonfile: Location) -> 'UDSCorpus':
        """Load annotated UDS graph corpus (including annotations) from JSON

        This is the suggested method for loading the UDS corpus.

        Parameters
        ----------
        sentences_jsonfile
            file containing Universal Decompositional Semantics corpus
            sentence-level graphs in JSON format
        documents_jsonfile
            file containing Universal Decompositional Semantics corpus
            document-level graphs in JSON format
        """
        sentences_ext = splitext(basename(sentences_jsonfile if isinstance(sentences_jsonfile, str) else 'dummy.json'))[-1]
        documents_ext = splitext(basename(documents_jsonfile if isinstance(documents_jsonfile, str) else 'dummy.json'))[-1]
        sent_ids = cast(dict[str, str], cls._load_ud_ids(sentence_ids_only=True))

        # process sentence-level graphs
        if isinstance(sentences_jsonfile, str) and sentences_ext == '.json':
            with open(sentences_jsonfile) as infile:
                sentences_json = json.load(infile)

        elif isinstance(sentences_jsonfile, str):
            sentences_json = json.loads(sentences_jsonfile)

        else:
            sentences_json = json.load(sentences_jsonfile)

        sentences: dict[str, UDSSentenceGraph] = {
            name: cast(UDSSentenceGraph, UDSSentenceGraph.from_dict(g_json, name))
            for name, g_json in sentences_json['data'].items()
        }

        # process document-level graphs
        if isinstance(documents_jsonfile, str) and documents_ext == '.json':
            with open(documents_jsonfile) as infile:
                documents_json = json.load(infile)

        elif isinstance(documents_jsonfile, str):
            documents_json = json.loads(documents_jsonfile)

        else:
            documents_json = json.load(documents_jsonfile)

        documents = {name: UDSDocument.from_dict(d_json, sentences,
                                                 sent_ids, name)
                     for name, d_json in documents_json['data'].items()}

        corpus = cls(cast(PredPattCorpus | None, sentences), documents)

        metadata_dict = {'sentence_metadata': sentences_json['metadata'],
                         'document_metadata': documents_json['metadata']}
        metadata = UDSCorpusMetadata.from_dict(metadata_dict)
        corpus.add_corpus_metadata(metadata)

        return corpus

    def add_corpus_metadata(self, metadata: UDSCorpusMetadata) -> None:
        """Add metadata to the corpus.

        Parameters
        ----------
        metadata : UDSCorpusMetadata
            Metadata to merge with existing corpus metadata
        """
        self._metadata += metadata

    def add_annotation(self, sentence_annotation: UDSAnnotation | None = None,
                       document_annotation: UDSAnnotation | None = None) -> None:
        """Add annotations to UDS sentence and document graphs

        Parameters
        ----------
        sentence_annotation
            the annotations to add to the sentence graphs in the corpus
        document_annotation
            the annotations to add to the document graphs in the corpus
        """
        if sentence_annotation:
            self.add_sentence_annotation(sentence_annotation)

        if document_annotation:
            self.add_document_annotation(document_annotation)

    def add_sentence_annotation(self, annotation: UDSAnnotation) -> None:
        """Add annotations to UDS sentence graphs

        Parameters
        ----------
        annotation
            the annotations to add to the graphs in the corpus
        """
        self._metadata.add_sentence_metadata(annotation.metadata)

        for gname, (node_attrs, edge_attrs) in annotation.items():
            if gname in self._sentences:
                from typing import cast

                from .graph import EdgeAttributes, EdgeKey, NodeAttributes
                self._sentences[gname].add_annotation(
                    cast(dict[str, NodeAttributes], node_attrs),
                    cast(dict[EdgeKey, EdgeAttributes], edge_attrs)
                )

    def add_document_annotation(self, annotation: UDSAnnotation) -> None:
        """Add annotations to UDS documents

        Parameters
        ----------
        annotation
            the annotations to add to the documents in the corpus
        """
        self._metadata.add_document_metadata(annotation.metadata)

        for dname, (node_attrs, edge_attrs) in annotation.items():
            if dname in self._documents:
                from .graph import EdgeAttributes, EdgeKey, NodeAttributes
                self._documents[dname].add_annotation(
                    cast(dict[str, NodeAttributes], node_attrs),
                    cast(dict[EdgeKey, EdgeAttributes], edge_attrs)
                )

    @classmethod
    def _initialize_documents(cls, graphs: dict[str, UDSSentenceGraph]) -> dict[str, UDSDocument]:
        """Create document collection from sentence graphs.

        Groups sentence graphs by document ID and creates UDSDocument objects.

        Parameters
        ----------
        graphs : dict[str, UDSSentenceGraph]
            Sentence graphs to organize into documents

        Returns
        -------
        dict[str, UDSDocument]
            Documents keyed by document ID
        """
        # load the UD document and sentence IDs
        ud_ids = cast(dict[str, dict[str, str]], cls._load_ud_ids())

        # add each graph to the appropriate document
        documents: dict[str, UDSDocument] = {}
        for name, graph in graphs.items():
            doc_id = ud_ids[name]['document_id']
            sent_id = ud_ids[name]['sentence_id']
            graph.document_id = doc_id
            graph.sentence_id = sent_id

            # add the graph to an existing document
            if doc_id in documents:
                documents[doc_id].add_sentence_graphs({name: graph}, {name: sent_id})
            # create a new document
            else:
                genre = doc_id.split('-')[0]
                timestamp = UDSDocument._get_timestamp_from_document_name(doc_id)
                documents[doc_id] =\
                    UDSDocument({name: graph}, {name: sent_id}, doc_id, genre, timestamp)

        return documents

    def to_json(self,
                sentences_outfile: Location | None = None,
                documents_outfile: Location | None = None) -> str | None:
        """Serialize corpus to json

        Parameters
        ----------
        sentences_outfile
            file to serialize sentence-level graphs to
        documents_outfile
            file to serialize document-level graphs to
        """
        metadata_serializable = self._metadata.to_dict()

        # convert graphs to dictionaries
        sentences_serializable = {'metadata': metadata_serializable['sentence_metadata'],
                                  'data': {name: graph.to_dict()
                                           for name, graph
                                           in self._sentences.items()}}

        if sentences_outfile is None:
            return json.dumps(sentences_serializable)

        elif isinstance(sentences_outfile, str):
            with open(sentences_outfile, 'w') as out:
                json.dump(sentences_serializable, out)

        else:
            json.dump(sentences_serializable, sentences_outfile)

        # serialize documents (note: we serialize only the *graphs*
        # for each document, not the metadata, which is loaded by
        # other means when calling UDSDocument.from_dict)
        documents_serializable = {'metadata': metadata_serializable['document_metadata'],
                                  'data': {name: doc.document_graph.to_dict()
                                           for name, doc
                                           in self._documents.items()}}

        if documents_outfile is None:
            return json.dumps(documents_serializable)

        elif isinstance(documents_outfile, str):
            with open(documents_outfile, 'w') as out:
                json.dump(documents_serializable, out)

        else:
            json.dump(documents_serializable, documents_outfile)

        return None

    @lru_cache(maxsize=128)
    def query(self, query: str | Query,
              query_type: str | None = None,
              cache_query: bool = True,
              cache_rdf: bool = True) -> dict[str, Result | dict[str, NodeAttributes] | dict[EdgeKey, EdgeAttributes]]:
        """Query all graphs in the corpus using SPARQL 1.1

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
            whether to cache the query. This should usually be set to
            True. It should generally only be False when querying
            particular nodes or edges--e.g. as in precompiled queries.
        clear_rdf
            whether to delete the RDF constructed for querying
            against. This will slow down future queries but saves a
            lot of memory
        """
        return {str(gid): graph.query(query, query_type,
                                      cache_query, cache_rdf)
                for gid, graph in self.items()}

    @property
    def documents(self) -> dict[str, UDSDocument]:
        """The documents in the corpus.

        Returns
        -------
        dict[str, UDSDocument]
            Mapping from document IDs to UDSDocument objects
        """
        return self._documents

    @property
    def documentids(self) -> list[str]:
        """The document IDs in the corpus.

        Returns
        -------
        list[str]
            List of all document identifiers
        """
        return list(self._documents)

    @property
    def ndocuments(self) -> int:
        """The number of documents in the corpus.

        Returns
        -------
        int
            Total document count
        """
        return len(self._documents)

    def sample_documents(self, k: int) -> dict[str, UDSDocument]:
        """Sample k documents without replacement

        Parameters
        ----------
        k
            the number of documents to sample
        """
        return {doc_id: self._documents[doc_id]
                for doc_id
                in sample(list(self._documents.keys()), k=k)}

    @property
    def metadata(self) -> UDSCorpusMetadata:
        """The corpus metadata.

        Returns
        -------
        UDSCorpusMetadata
            Metadata for sentence and document annotations
        """
        return self._metadata

    @property
    def sentence_node_subspaces(self) -> set[str]:
        """The UDS sentence node subspaces in the corpus.

        Returns
        -------
        set[str]
            Set of subspace names for sentence nodes

        Raises
        ------
        NotImplementedError
            This property is not yet implemented
        """
        raise NotImplementedError

    @property
    def sentence_edge_subspaces(self) -> set[str]:
        """The UDS sentence edge subspaces in the corpus.

        Returns
        -------
        set[str]
            Set of subspace names for sentence edges

        Raises
        ------
        NotImplementedError
            This property is not yet implemented
        """
        raise NotImplementedError

    @property
    def sentence_subspaces(self) -> set[str]:
        """All UDS sentence subspaces (node and edge) in the corpus.

        Returns
        -------
        set[str]
            Union of sentence node and edge subspaces
        """
        return self.sentence_node_subspaces |\
               self.sentence_edge_subspaces

    @property
    def document_node_subspaces(self) -> set[str]:
        """The UDS document node subspaces in the corpus.

        Returns
        -------
        set[str]
            Set of subspace names for document nodes

        Raises
        ------
        NotImplementedError
            This property is not yet implemented
        """
        raise NotImplementedError

    @property
    def document_edge_subspaces(self) -> set[str]:
        """The UDS document edge subspaces in the corpus.

        Returns
        -------
        set[str]
            Set of subspace names for document edges
        """
        return self._metadata.document_edge_subspaces  # type: ignore[no-any-return,attr-defined]

    @property
    def document_subspaces(self) -> set[str]:
        """All UDS document subspaces (node and edge) in the corpus.

        Returns
        -------
        set[str]
            Union of document node and edge subspaces
        """
        return self.document_node_subspaces |\
               self.document_edge_subspaces

    def sentence_properties(self, subspace: str | None = None) -> set[str]:
        """The properties in a sentence subspace.

        Parameters
        ----------
        subspace : str | None, optional
            Subspace to query, or None for all properties

        Returns
        -------
        set[str]
            Property names in the subspace

        Raises
        ------
        NotImplementedError
            This method is not yet implemented
        """
        raise NotImplementedError

    def sentence_property_metadata(self, subspace: str,
                                   prop: str) -> UDSPropertyMetadata:
        """The metadata for a property in a sentence subspace

        Parameters
        ----------
        subspace
            The subspace the property is in
        prop
            The property in the subspace
        """
        raise NotImplementedError

    def document_properties(self, subspace: str | None = None) -> set[str]:
        """The properties in a document subspace.

        Parameters
        ----------
        subspace : str | None, optional
            Subspace to query, or None for all properties

        Returns
        -------
        set[str]
            Property names in the subspace

        Raises
        ------
        NotImplementedError
            This method is not yet implemented
        """
        raise NotImplementedError

    def document_property_metadata(self, subspace: str,
                                   prop: str) -> UDSPropertyMetadata:
        """The metadata for a property in a document subspace

        Parameters
        ----------
        subspace
            The subspace the property is in
        prop
            The property in the subspace
        """
        raise NotImplementedError
