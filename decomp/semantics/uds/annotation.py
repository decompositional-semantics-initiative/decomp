"""Module for representing UDS property annotations with support for raw and normalized formats.

This module provides classes for handling Universal Decompositional Semantics (UDS)
annotations in both raw (multi-annotator) and normalized (single-value) formats.
It includes:

- Type aliases for annotation data structures
- Helper functions for nested defaultdict handling
- UDSAnnotation: Abstract base class for all annotations
- NormalizedUDSAnnotation: Single-value annotations with confidence scores
- RawUDSAnnotation: Multi-annotator annotations with per-annotator values
"""

import json
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterator
from logging import warning
from os.path import basename, splitext
from typing import TextIO, TypeAlias, cast, overload

from overrides import overrides

from .metadata import PrimitiveType, UDSAnnotationMetadata, UDSPropertyMetadata
from .types import AnnotatorValue as TypedAnnotatorValue, UDSSubspace


# type aliases for annotation data structures
NodeAttributes: TypeAlias = dict[str, dict[str, dict[str, PrimitiveType]]]
"""Node attributes: node_id -> subspace -> property -> value."""

EdgeAttributes: TypeAlias = dict[tuple[str, ...], dict[str, dict[str, PrimitiveType]]]
"""Edge attributes: (source_id, target_id) -> subspace -> property -> value."""

GraphNodeAttributes: TypeAlias = dict[str, NodeAttributes]
"""Mapping from graph IDs to their node attributes."""

GraphEdgeAttributes: TypeAlias = dict[str, EdgeAttributes]
"""Mapping from graph IDs to their edge attributes."""

NormalizedData: TypeAlias = dict[str, dict[str, dict[str, PrimitiveType]]]
"""Normalized annotation data: subspace -> property -> {'value': val, 'confidence': conf}."""

# type for raw annotation property data: {"value": {annotator_id: val}, "confidence": {annotator_id: conf}}
RawPropertyData: TypeAlias = dict[str, dict[str, PrimitiveType]]
"""Raw property data with per-annotator values and confidences."""

RawData: TypeAlias = dict[str, dict[str, dict[str, RawPropertyData]]]
"""Raw annotation data: subspace -> property -> RawPropertyData."""

# raw attribute types (for RawUDSAnnotation)
RawNodeAttributes: TypeAlias = dict[str, dict[str, dict[str, RawPropertyData]]]
"""Raw node attributes with multi-annotator data."""

RawEdgeAttributes: TypeAlias = dict[tuple[str, ...], dict[str, dict[str, RawPropertyData]]]
"""Raw edge attributes with multi-annotator data."""

GraphRawNodeAttributes: TypeAlias = dict[str, RawNodeAttributes]
"""Mapping from graph IDs to their raw node attributes."""

GraphRawEdgeAttributes: TypeAlias = dict[str, RawEdgeAttributes]
"""Mapping from graph IDs to their raw edge attributes."""

# type for the nested defaultdict used by annotator (5 levels deep)
# annotator_id -> graph_id -> node/edge_id -> subspace -> property -> {confidence: val, value: val}

# use AnnotatorValue from types module for consistency
AnnotatorValue = TypedAnnotatorValue
NodeAnnotatorDict: TypeAlias = dict[str, dict[str, dict[str, dict[str, dict[str, AnnotatorValue]]]]]
"""Nested dict for node annotations by annotator: annotator -> graph -> node -> subspace -> property -> AnnotatorValue."""

EdgeAnnotatorDict: TypeAlias = dict[str, dict[str, dict[tuple[str, ...], dict[str, dict[str, AnnotatorValue]]]]]
"""Nested dict for edge annotations by annotator: annotator -> graph -> edge -> subspace -> property -> AnnotatorValue."""

# complex return types for items() methods
BaseItemsReturn: TypeAlias = Iterator[tuple[str, tuple[dict[str, NormalizedData | RawData], dict[tuple[str, ...], NormalizedData | RawData]]]]
"""Return type for base items() method yielding (graph_id, (node_attrs, edge_attrs))."""

# Raw items return type for annotator-specific items - more specific than base
# specific return types for different annotation access patterns
NodeItemsReturn: TypeAlias = Iterator[tuple[str, dict[str, dict[str, dict[str, AnnotatorValue]]]]]
EdgeItemsReturn: TypeAlias = Iterator[tuple[str, dict[tuple[str, ...], dict[str, dict[str, AnnotatorValue]]]]]

# union type for RawUDSAnnotation.items() method
RawItemsReturn: TypeAlias = NodeItemsReturn | EdgeItemsReturn | BaseItemsReturn


def _nested_defaultdict(depth: int) -> type[dict] | defaultdict:
    """Construct a nested defaultdict of specified depth.

    The lowest nesting level (depth=0) is a normal dictionary.
    Higher levels are defaultdicts that create nested structures.

    Parameters
    ----------
    depth : int
        The depth of nesting. Must be non-negative.

    Returns
    -------
    type[dict[str, AnnotatorValue]] | Callable[[], dict[str, AnnotatorValue]]
        A dict constructor (depth=0) or defaultdict with nested structure

    Raises
    ------
    ValueError
        If depth is negative
    """
    if depth < 0:
        raise ValueError('depth must be a nonnegative int')

    if not depth:
        return dict
    else:
        return defaultdict(lambda: _nested_defaultdict(depth-1))

def _freeze_nested_defaultdict(d: dict | defaultdict) -> dict:
    """Convert nested defaultdict to regular dict recursively.

    Parameters
    ----------
    d : dict[str, NodeAnnotatorDict | EdgeAnnotatorDict | AnnotatorValue] | defaultdict[str, NodeAnnotatorDict | EdgeAnnotatorDict | AnnotatorValue]
        The nested defaultdict to freeze

    Returns
    -------
    dict[str, NodeAnnotatorDict | EdgeAnnotatorDict | AnnotatorValue]
        Regular dict with all defaultdicts converted
    """
    d = dict(d)

    for k, v in d.items():
        if isinstance(v, (dict, defaultdict)):
            d[k] = _freeze_nested_defaultdict(v)

    return d

class UDSAnnotation(ABC):
    """A Universal Decompositional Semantics annotation

    This is an abstract base class. See its RawUDSAnnotation and
    NormalizedUDSAnnotation subclasses.

    The ``__init__`` method for this class is abstract to ensure that
    it cannot be initialized directly, even though it is used by the
    subclasses and has a valid default implementation. The
    ``from_json`` class method is abstract to force the subclass to
    define more specific constraints on its JSON inputs.

    Parameters
    ----------
    metadata
        The metadata for the annotations
    data
        A mapping from graph identifiers to node/edge identifiers to
        property subspaces to properties to annotations. Edge
        identifiers must be represented as NODEID1%%NODEID2, and node
        identifiers must not contain %%.
    """

    CACHE: dict[str, 'UDSAnnotation'] = {}

    @abstractmethod
    def __init__(self, metadata: UDSAnnotationMetadata,
                 data: dict[str, dict[str, NormalizedData | RawData]]):
        self._process_metadata(metadata)
        self._process_data(data)

        self._validate()

    def _process_metadata(self, metadata: UDSAnnotationMetadata) -> None:
        """Store annotation metadata.

        Parameters
        ----------
        metadata : UDSAnnotationMetadata
            The metadata to store
        """
        self._metadata = metadata

    def _process_data(self, data: dict[str, dict[str, NormalizedData | RawData]]) -> None:
        """Process annotation data into node and edge attributes.

        Parameters
        ----------
        data : dict[str, dict[str, NormalizedData | RawData]]
            Raw annotation data by graph ID
        """
        self._process_node_data(data)
        self._process_edge_data(data)

        self._graphids = set(data)

    def _process_node_data(self, data: dict[str, dict[str, NormalizedData | RawData]]) -> None:
        """Extract node attributes from annotation data.

        Node identifiers are those without '%%' separator.

        Parameters
        ----------
        data : dict[str, dict[str, NormalizedData | RawData]]
            Raw annotation data by graph ID
        """
        self._node_attributes: dict[str, dict[str, NormalizedData | RawData]] = {
            gid: {node: a
                  for node, a in attrs.items()
                  if '%%' not in node}
            for gid, attrs in data.items()}

        # Some attributes are not property subspaces and are thus excluded
        self._excluded_attributes = {'subpredof', 'subargof', 'headof', 'span', 'head'}
        self._node_subspaces: set[UDSSubspace] = {
            cast(UDSSubspace, ss) for gid, nodedict
            in self._node_attributes.items()
            for nid, subspaces in nodedict.items()
            for ss in subspaces
            if ss not in self._excluded_attributes
        }

    def _process_edge_data(self, data: dict[str, dict[str, NormalizedData | RawData]]) -> None:
        """Extract edge attributes from annotation data.

        Edge identifiers contain '%%' separator between source and target.

        Parameters
        ----------
        data : dict[str, dict[str, NormalizedData | RawData]]
            Raw annotation data by graph ID
        """
        self._edge_attributes: dict[str, dict[tuple[str, ...], NormalizedData | RawData]] = {
            gid: {tuple(edge.split('%%')): a
                  for edge, a in attrs.items()
                  if '%%' in edge}
            for gid, attrs in data.items()}

        self._edge_subspaces: set[UDSSubspace] = {
            cast(UDSSubspace, ss) for gid, edgedict
            in self._edge_attributes.items()
            for eid, subspaces in edgedict.items()
            for ss in subspaces
        }

    def _validate(self) -> None:
        """Validate annotation data consistency.

        Checks that:
        - Node and edge annotations have the same graph IDs
        - All data subspaces have associated metadata
        - Warns about metadata for missing subspaces

        Raises
        ------
        ValueError
            If validation fails
        """
        node_graphids = set(self._node_attributes)
        edge_graphids = set(self._edge_attributes)

        if node_graphids != edge_graphids:
            raise ValueError(
                'The graph IDs that nodes are specified for '
                'are not the same as those that the edges are.'
                'UDSAnnotation and its stock subclasses assume '
                'that node and edge annotations are specified '
                'for the same set of graph IDs. Unless you have '
                'subclassed UDSAnnotation or its subclasses, '
                'there is likely something going wrong. If '
                'you have subclassed it and your subclass does '
                'not require this assumption. You should override '
                'UDSAnnotation._validate'
            )


        subspaces = self._node_subspaces | self._edge_subspaces

        if self._metadata.subspaces - subspaces:
            for ss in self._metadata.subspaces - subspaces:
                warnmsg = 'The annotation metadata is specified for ' +\
                          f'subspace {ss}, which is not in the data.'
                warning(warnmsg)

        if subspaces - self._metadata.subspaces:
            missing = subspaces - self._metadata.subspaces
            errmsg = 'The following subspaces do not have associated ' +\
                     'metadata: ' + ','.join(missing)
            raise ValueError(errmsg)

    def __getitem__(self, graphid: str) -> tuple[dict[str, NormalizedData | RawData], dict[tuple[str, ...], NormalizedData | RawData]]:
        """Get node and edge attributes for a graph.

        Parameters
        ----------
        graphid : str
            The graph identifier

        Returns
        -------
        tuple[dict[str, NormalizedData | RawData], dict[tuple[str, ...], NormalizedData | RawData]]
            Tuple of (node_attributes, edge_attributes) for the graph

        Raises
        ------
        KeyError
            If graphid not found
        """
        node_attrs = self._node_attributes[graphid]
        edge_attrs = self._edge_attributes[graphid]

        return node_attrs, edge_attrs

    @classmethod
    @abstractmethod
    def from_json(cls, jsonfile: str | TextIO) -> 'UDSAnnotation':
        """Load Universal Decompositional Semantics dataset from JSON

        For node annotations, the format of the JSON passed to this
        class method must be:

        ::

            {GRAPHID_1: {NODEID_1_1: DATA,
                         ...},
             GRAPHID_2: {NODEID_2_1: DATA,
                         ...},
             ...
            }

        Edge annotations should be of the form:

        ::

            {GRAPHID_1: {NODEID_1_1%%NODEID_1_2: DATA,
                         ...},
             GRAPHID_2: {NODEID_2_1%%NODEID_2_2: DATA,
                         ...},
             ...
            }

        Graph and node identifiers must match the graph and node
        identifiers of the predpatt graphs to which the annotations
        will be added. The subclass determines the form of DATA in the
        above.

        Parameters
        ----------
        jsonfile
            (path to) file containing annotations as JSON
        """
        if isinstance(jsonfile, str) and jsonfile in cls.CACHE:
            return cls.CACHE[jsonfile]

        ext = splitext(basename(jsonfile if isinstance(jsonfile, str) else 'dummy.json'))[-1]

        if isinstance(jsonfile, str) and ext == '.json':
            with open(jsonfile) as infile:
                annotation = json.load(infile)

        elif isinstance(jsonfile, str):
            annotation = json.loads(jsonfile)

        else:
            annotation = json.load(jsonfile)

        if set(annotation) < {'metadata', 'data'}:
            errmsg = 'annotation JSON must specify both "metadata" and "data"'
            raise ValueError(errmsg)

        if set(annotation) > {'metadata', 'data'}:
            warnmsg = 'ignoring the following fields in annotation JSON:' +\
                      ', '.join(set(annotation) - {'metadata', 'data'})
            warning(warnmsg)

        metadata = UDSAnnotationMetadata.from_dict(annotation['metadata'])

        result = cls(metadata, annotation['data'])

        if isinstance(jsonfile, str):
            cls.CACHE[jsonfile] = result

        return result

    def items(self, annotation_type: str | None = None) -> BaseItemsReturn:
        """Dictionary-like items generator for attributes

        If annotation_type is specified as "node" or "edge", this
        generator yields a graph identifier and its node or edge
        attributes (respectively); otherwise, this generator yields a
        graph identifier and a tuple of its node and edge attributes.
        """
        if annotation_type is None:
            for gid in self.graphids:
                yield gid, self[gid]

    @property
    def node_attributes(self) -> dict[str, dict[str, NormalizedData | RawData]]:
        """All node attributes by graph ID.

        Returns
        -------
        dict[str, dict[str, NormalizedData | RawData]]
            Mapping from graph ID to node ID to annotation data
        """
        return self._node_attributes

    @property
    def edge_attributes(self) -> dict[str, dict[tuple[str, ...], NormalizedData | RawData]]:
        """All edge attributes by graph ID.

        Returns
        -------
        dict[str, dict[tuple[str, ...], NormalizedData | RawData]]
            Mapping from graph ID to edge tuple to annotation data
        """
        return self._edge_attributes

    @property
    def graphids(self) -> set[str]:
        """Set of all graph identifiers with annotations.

        Returns
        -------
        set[str]
            Graph IDs that have node or edge annotations
        """
        return self._graphids

    @property
    def node_graphids(self) -> set[str]:
        """Set of graph identifiers with node annotations.

        Returns
        -------
        set[str]
            Graph IDs that have node annotations
        """
        return set(self.node_attributes)

    @property
    def edge_graphids(self) -> set[str]:
        """Set of graph identifiers with edge annotations.

        Returns
        -------
        set[str]
            Graph IDs that have edge annotations
        """
        return set(self.edge_attributes)

    @property
    def metadata(self) -> UDSAnnotationMetadata:
        """The metadata for all annotations.

        Returns
        -------
        UDSAnnotationMetadata
            Metadata including subspaces, properties, and datatypes
        """
        return self._metadata

    @property
    def node_subspaces(self) -> set[UDSSubspace]:
        """Set of subspaces used in node annotations.

        Returns
        -------
        set[UDSSubspace]
            Subspace names excluding structural attributes
        """
        return self._node_subspaces

    @property
    def edge_subspaces(self) -> set[UDSSubspace]:
        """Set of subspaces used in edge annotations.

        Returns
        -------
        set[UDSSubspace]
            Subspace names for edges
        """
        return self._edge_subspaces

    @property
    def subspaces(self) -> set[UDSSubspace]:
        """Set of all subspaces (node and edge).

        Returns
        -------
        set[UDSSubspace]
            Union of node and edge subspaces
        """
        return self.node_subspaces | self._edge_subspaces

    def properties(self, subspace: UDSSubspace | None = None) -> set[str]:
        """Get properties for a subspace.

        Parameters
        ----------
        subspace : str | None, optional
            Subspace to get properties for. If None, returns all properties.

        Returns
        -------
        set[str]
            Property names in the subspace
        """
        return self._metadata.properties(subspace)

    def property_metadata(self, subspace: UDSSubspace,
                          prop: str) -> UDSPropertyMetadata:
        """Get metadata for a specific property.

        Parameters
        ----------
        subspace : str
            The subspace containing the property
        prop : str
            The property name

        Returns
        -------
        UDSPropertyMetadata
            Metadata including datatypes and annotators

        Raises
        ------
        KeyError
            If subspace or property not found
        """
        return cast(UDSPropertyMetadata, self._metadata[subspace, prop])


class NormalizedUDSAnnotation(UDSAnnotation):
    """A normalized Universal Decompositional Semantics annotation

    Properties in a NormalizedUDSAnnotation may have only a single
    ``str``, ``int``, or ``float`` value and a single ``str``,
    ``int``, or ``float`` confidence.

    Parameters
    ----------
    metadata
        The metadata for the annotations
    data
        A mapping from graph identifiers to node/edge identifiers to
        property subspaces to property to value and confidence. Edge
        identifiers must be represented as NODEID1%%NODEID2, and node
        identifiers must not contain %%.
    """

    @overrides
    def __init__(self, metadata: UDSAnnotationMetadata,
                 data: dict[str, dict[str, dict[str, dict[str, PrimitiveType]]]]):
        # cast to parent's expected type (NormalizedData is a subtype)
        data_cast: dict[str, dict[str, NormalizedData | RawData]] = cast(dict[str, dict[str, NormalizedData | RawData]], data)
        super().__init__(metadata, data_cast)

    def _validate(self) -> None:
        """Validate that normalized annotations don't have annotators.

        Raises
        ------
        ValueError
            If metadata specifies annotators
        """
        super()._validate()

        if self._metadata.has_annotators():
            raise ValueError(
                'metadata for NormalizedUDSAnnotation should '
                'not specify annotators'
            )

    @classmethod
    @overrides
    def from_json(cls, jsonfile: str | TextIO) -> 'NormalizedUDSAnnotation':
        """Generates a dataset of normalized annotations from a JSON file

        For node annotations, the format of the JSON passed to this
        class method must be:

        ::

            {GRAPHID_1: {NODEID_1_1: DATA,
                         ...},
             GRAPHID_2: {NODEID_2_1: DATA,
                         ...},
             ...
            }

        Edge annotations should be of the form:

        ::

            {GRAPHID_1: {NODEID_1_1%%NODEID_1_2: DATA,
                         ...},
             GRAPHID_2: {NODEID_2_1%%NODEID_2_2: DATA,
                         ...},
             ...
            }

        Graph and node identifiers must match the graph and node
        identifiers of the predpatt graphs to which the annotations
        will be added.

        DATA in the above is assumed to have the following
        structure:

        ::

            {SUBSPACE_1: {PROP_1_1: {'value': VALUE,
                                    'confidence': VALUE},
                         ...},
             SUBSPACE_2: {PROP_2_1: {'value': VALUE,
                                     'confidence': VALUE},
                         ...},
            }

        VALUE in the above is assumed to be unstructured.
        """
        return cast('NormalizedUDSAnnotation', super().from_json(jsonfile))


class RawUDSAnnotation(UDSAnnotation):
    """A raw Universal Decompositional Semantics dataset

    Unlike :class:`decomp.semantics.uds.NormalizedUDSAnnotation`,
    objects of this class may have multiple annotations for a
    particular attribute. Each annotation is associated with an
    annotator ID, and different annotators may have annotated
    different numbers of items.

    Parameters
    ----------
    annotation
        A mapping from graph identifiers to node/edge identifiers to
        property subspaces to property to value and confidence for
        each annotator. Edge identifiers must be represented as
        NODEID1%%NODEID2, and node identifiers must not contain %%.
    """

    @overrides
    def __init__(self, metadata: UDSAnnotationMetadata,
                 data: dict[str, dict[str, RawData]]):
        # cast to parent's expected type (RawData is a subtype)
        data_cast: dict[str, dict[str, NormalizedData | RawData]] = cast(dict[str, dict[str, NormalizedData | RawData]], data)
        super().__init__(metadata, data_cast)

    def _process_node_data(self, data: dict[str, dict[str, NormalizedData | RawData]]) -> None:
        # process raw node data differently than normalized
        self._node_attributes = {gid: {node: a
                                       for node, a in attrs.items()
                                       if '%%' not in node}
                                 for gid, attrs in data.items()}

        # some attributes are not property subspaces and are thus excluded
        self._excluded_attributes = {'subpredof', 'subargof', 'headof', 'span', 'head'}
        self._node_subspaces: set[UDSSubspace] = {
            cast(UDSSubspace, ss) for gid, nodedict
            in self._node_attributes.items()
            for nid, subspaces in nodedict.items()
            for ss in subspaces
            if ss not in self._excluded_attributes
        }

        # initialize as nested defaultdict, will be frozen to regular dict later
        # the actual type is a nested defaultdict but we'll treat it as the final dict type
        self.node_attributes_by_annotator = cast(NodeAnnotatorDict, _nested_defaultdict(5))

        for gid, attrs in self._node_attributes.items():
            for nid, subspaces in attrs.items():
                for subspace, properties in subspaces.items():
                    if subspace in self._excluded_attributes:
                        continue
                    for prop, annotation in properties.items():
                        if prop in self._excluded_attributes:
                            continue
                        # in RawData, annotation is RawPropertyData which has 'value' and 'confidence' keys
                        if isinstance(annotation, dict) and 'value' in annotation and 'confidence' in annotation:
                            value_dict = annotation.get('value')
                            conf_dict = annotation.get('confidence')
                            if isinstance(value_dict, dict) and isinstance(conf_dict, dict):
                                for annid, val in value_dict.items():
                                    conf = conf_dict.get(annid)
                                    if conf is not None:
                                        # both conf and val come from dicts with PrimitiveType values
                                        # cast to satisfy mypy
                                        self.node_attributes_by_annotator[annid][gid][nid][subspace][prop] = \
                                            AnnotatorValue(confidence=cast(PrimitiveType, conf), value=cast(PrimitiveType, val))

        # freeze to regular dict and cast to proper type
        self.node_attributes_by_annotator = cast(NodeAnnotatorDict,
            _freeze_nested_defaultdict(self.node_attributes_by_annotator))

    def _process_edge_data(self, data: dict[str, dict[str, NormalizedData | RawData]]) -> None:
        # process raw edge data differently than normalized
        self._edge_attributes = {gid: {tuple(edge.split('%%')): a
                                       for edge, a in attrs.items()
                                       if '%%' in edge}
                                 for gid, attrs in data.items()}

        self._edge_subspaces: set[UDSSubspace] = {
            cast(UDSSubspace, ss) for gid, edgedict
            in self._edge_attributes.items()
            for eid, subspaces in edgedict.items()
            for ss in subspaces
        }

        # initialize as nested defaultdict, will be frozen to regular dict later
        # the actual type is a nested defaultdict but we'll treat it as the final dict type
        self.edge_attributes_by_annotator = cast(EdgeAnnotatorDict, _nested_defaultdict(5))

        for gid, attrs in self.edge_attributes.items():
            for nid, subspaces in attrs.items():
                for subspace, properties in subspaces.items():
                    for prop, annotation in properties.items():
                        # In raw data, annotation is actually a dict with 'value' and 'confidence' keys
                        if isinstance(annotation, dict) and 'value' in annotation and 'confidence' in annotation:
                            value_dict = annotation.get('value')
                            conf_dict = annotation.get('confidence')
                            if isinstance(value_dict, dict) and isinstance(conf_dict, dict):
                                for annid, val in value_dict.items():
                                    conf = conf_dict.get(annid)
                                    if conf is not None:
                                        # both conf and val come from dicts with PrimitiveType values
                                        # cast to satisfy mypy
                                        self.edge_attributes_by_annotator[annid][gid][nid][subspace][prop] = \
                                            AnnotatorValue(confidence=cast(PrimitiveType, conf), value=cast(PrimitiveType, val))

        # freeze to regular dict and cast to proper type
        self.edge_attributes_by_annotator = cast(EdgeAnnotatorDict,
            _freeze_nested_defaultdict(self.edge_attributes_by_annotator))


    @overrides
    def _validate(self) -> None:
        """Validate that raw annotations have annotators for all properties.

        Raises
        ------
        ValueError
            If any property lacks annotator metadata
        """
        super()._validate()

        if not all(self._metadata.has_annotators(ss, p)
                   for ss in self._metadata.subspaces
                   for p in self._metadata.properties(ss)):
            raise ValueError(
                'metadata for RawUDSAnnotation should '
                'specify annotators for all subspaces and properties'
            )

    @classmethod
    @overrides
    def from_json(cls, jsonfile: str | TextIO) -> 'RawUDSAnnotation':
        """Generates a dataset for raw annotations from a JSON file

        For node annotations, the format of the JSON passed to this
        class method must be:

        ::

            {GRAPHID_1: {NODEID_1_1: DATA,
                         ...},
             GRAPHID_2: {NODEID_2_1: DATA,
                         ...},
             ...
            }

        Edge annotations should be of the form:

        ::

            {GRAPHID_1: {NODEID_1_1%%NODEID_1_2: DATA,
                         ...},
             GRAPHID_2: {NODEID_2_1%%NODEID_2_2: DATA,
                         ...},
             ...
            }

        Graph and node identifiers must match the graph and node
        identifiers of the predpatt graphs to which the annotations
        will be added.

        DATA in the above is assumed to have the following
        structure:

        ::

            {SUBSPACE_1: {PROP_1_1: {'value': {
                                        ANNOTATOR1: VALUE1, 
                                        ANNOTATOR2: VALUE2,
                                        ...
                                              },
                                     'confidence': {
                                        ANNOTATOR1: CONF1,
                                        ANNOTATOR2: CONF2,
                                        ...
                                                   }
                                    },
                          PROP_1_2: {'value': {
                                        ANNOTATOR1: VALUE1,
                                        ANNOTATOR2: VALUE2,
                                        ...
                                              },
                                     'confidence': {
                                        ANNOTATOR1: CONF1,
                                        ANNOTATOR2: CONF2,
                                        ...
                                                   }
                                    },
                          ...},
             SUBSPACE_2: {PROP_2_1: {'value': {
                                        ANNOTATOR3: VALUE1,
                                        ANNOTATOR4: VALUE2,
                                        ...
                                              },
                                     'confidence': {
                                        ANNOTATOR3: CONF1,
                                        ANNOTATOR4: CONF2,
                                        ...
                                                   }
                                    },
                         ...},
            ...}

        VALUEi and CONFi are assumed to be unstructured.
        """
        return cast('RawUDSAnnotation', super().from_json(jsonfile))

    def annotators(self, subspace: UDSSubspace | None = None,
                   prop: str | None = None) -> set[str] | None:
        """Get annotator IDs for a subspace and property.

        If neither subspace nor property are specified, all annotator
        IDs are returned. If only the subspace is specified, all
        annotator IDs for the subspace are returned.

        Parameters
        ----------
        subspace : str | None, optional
            The subspace to filter by
        prop : str | None, optional
            The property to filter by

        Returns
        -------
        set[str] | None
            Set of annotator IDs or None if no annotators found
        """
        return self._metadata.annotators(subspace, prop)

    @overload
    def items(self, annotation_type: str | None = None) -> BaseItemsReturn: ...
    
    @overload  
    def items(self, annotation_type: str | None = None,
              annotator_id: str | None = None) -> RawItemsReturn: ...
    
    def items(self, annotation_type: str | None = None,
              annotator_id: str | None = None) -> RawItemsReturn:
        """Dictionary-like items generator for attributes

        This method behaves exactly like UDSAnnotation.items, except
        that, if an annotator ID is passed, it generates only items
        annotated by the specified annotator.

        Parameters
        ----------
        annotation_type
            Whether to return node annotations, edge annotations, or
            both (default)
        annotator_id
            The annotator whose annotations will be returned by the
            generator (defaults to all annotators)

        Raises
        ------
        ValueError
            If both annotation_type and annotator_id are passed and
            the relevant annotator gives no annotations of the
            relevant type, and exception is raised
        """
        if annotation_type not in [None, "node", "edge"]:
            raise ValueError('annotation_type must be None, "node", or "edge"')

        if annotator_id is None:
            # call parent class method when no annotator_id specified
            yield from super().items(annotation_type)

        elif annotation_type == "node":
            if annotator_id in self.node_attributes_by_annotator:
                for gid in self.graphids:
                    node_attrs = self.node_attributes_by_annotator[annotator_id][gid]
                    # when annotation_type is "node", yield only node_attrs (not a tuple)
                    yield gid, node_attrs

            else:
                errmsg = f'{annotator_id} does not have associated ' +\
                         'node annotations'
                raise ValueError(errmsg)

        elif annotation_type == "edge":
            if annotator_id in self.edge_attributes_by_annotator:
                for gid in self.graphids:
                    edge_attrs = self.edge_attributes_by_annotator[annotator_id][gid]
                    # when annotation_type is "edge", yield only edge_attrs (not a tuple)
                    yield gid, edge_attrs

            else:
                raise ValueError(
                    f'{annotator_id} does not have associated '
                    'edge annotations'
                )

        else:
            for gid in self.graphids:
                if annotator_id in self.node_attributes_by_annotator:
                    node_attrs = self.node_attributes_by_annotator[annotator_id][gid]

                else:
                    node_attrs = {}

                if annotator_id in self.edge_attributes_by_annotator:
                    edge_attrs = self.edge_attributes_by_annotator[annotator_id][gid]

                else:
                    edge_attrs = {}

                yield gid, (cast(dict[str, NormalizedData | RawData], node_attrs),
                           cast(dict[tuple[str, ...], NormalizedData | RawData], edge_attrs))
