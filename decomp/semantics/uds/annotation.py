import json

from typing import Union, Any, Optional, TextIO
from typing import Dict, Set
from os.path import basename, splitext
from collections import defaultdict
from abc import ABC, abstractmethod
from overrides import overrides
from logging import warning

from .metadata import PrimitiveType
from .metadata import UDSAnnotationMetadata
from .metadata import UDSPropertyMetadata

NormalizedData = Dict[str, Dict[str, Dict[str, PrimitiveType]]]
RawData = Dict[str, Dict[str, Dict[str, Dict[str, PrimitiveType]]]]


def _nested_defaultdict(depth: int) -> Union[dict, defaultdict]:
    """Constructs a nested defaultdict

    The lowest nesting level is a normal dictionary

    Parameters
    ----------
    depth
        The depth of the nesting   
    """
    if depth < 0:
        raise ValueError('depth must be a nonnegative int')

    if not depth:
        return dict
    else:
        return defaultdict(lambda: _nested_defaultdict(depth-1))

def _freeze_nested_defaultdict(d: defaultdict) -> dict:
    d = dict(d)

    for k, v in d.items():
        if isinstance(v, defaultdict):
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
    CACHE = {}

    @abstractmethod
    def __init__(self, metadata: UDSAnnotationMetadata,
                 data: Dict[str, Dict[str, Any]]):
        self._process_metadata(metadata)
        self._process_data(data)

        self._validate()

    def _process_metadata(self, metadata):
        self._metadata = metadata

    def _process_data(self, data):
        self._process_node_data(data)
        self._process_edge_data(data)

        self._graphids = set(data)

    def _process_node_data(self, data):
        self._node_attributes = {gid: {node: a
                                       for node, a in attrs.items()
                                       if '%%' not in node}
                                 for gid, attrs in data.items()}

        # Some attributes are not property subspaces and are thus excluded
        excluded_attributes = {'subpredof', 'subargof', 'headof', 'span', 'head'}
        self._node_subspaces = {ss for gid, nodedict
                                in self._node_attributes.items()
                                for nid, subspaces in nodedict.items()
                                for ss in subspaces}
        self._node_subspaces = self._node_subspaces - excluded_attributes

    def _process_edge_data(self, data):
        self._edge_attributes = {gid: {tuple(edge.split('%%')): a
                                       for edge, a in attrs.items()
                                       if '%%' in edge}
                                 for gid, attrs in data.items()}

        self._edge_subspaces = {ss for gid, edgedict
                                in self._edge_attributes.items()
                                for eid, subspaces in edgedict.items()
                                for ss in subspaces}

    def _validate(self):
        node_graphids = set(self._node_attributes)
        edge_graphids = set(self._edge_attributes)

        if node_graphids != edge_graphids:
            errmsg = 'The graph IDs that nodes are specified for ' +\
                     'are not the same as those that the edges are.' +\
                     'UDSAnnotation and its stock subclasses assume ' +\
                     'that node and edge annotations are specified ' +\
                     'for the same set of graph IDs. Unless you have ' +\
                     'subclassed UDSAnnotation or its subclasses, ' +\
                     'there is likely something going wrong. If ' +\
                     'you have subclassed it and your subclass does ' +\
                     'not require this assumption. You should override ' +\
                     'UDSAnnotation._validate'
            raise ValueError(errmsg)


        subspaces = self._node_subspaces | self._edge_subspaces

        if self._metadata.subspaces - subspaces:
            for ss in self._metadata.subspaces - subspaces:
                warnmsg = 'The annotation metadata is specified for ' +\
                          'subspace {}, which is not in the data.'.format(ss)
                warning(warnmsg)

        if subspaces - self._metadata.subspaces:
            missing = subspaces - self._metadata.subspaces
            errmsg = 'The following subspaces do not have associated ' +\
                     'metadata: ' + ','.join(missing)
            raise ValueError(errmsg)

    def __getitem__(self, graphid: str):
        node_attrs = self._node_attributes[graphid]
        edge_attrs = self._edge_attributes[graphid]

        return node_attrs, edge_attrs

    @classmethod
    @abstractmethod
    def from_json(cls, jsonfile: Union[str, TextIO]) -> 'UDSAnnotation':
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

        if set(annotation) < {'metadata', 'data'}:
            errmsg = 'annotation JSON must specify both "metadata" and "data"'
            raise ValueError(errmsg)

        if set(annotation) > {'metadata', 'data'}:
            warnmsg = 'ignoring the following fields in annotation JSON:' +\
                      ', '.join(set(annotation) - {'metadata', 'data'})
            warning(warnmsg)

        metadata = UDSAnnotationMetadata.from_dict(annotation['metadata'])

        cls.CACHE[jsonfile] = cls(metadata,
                                  annotation['data'])

        return cls.CACHE[jsonfile]

    def items(self, annotation_type: Optional[str] = None):
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
    def node_attributes(self):
        """The node attributes"""
        return self._node_attributes

    @property
    def edge_attributes(self):
        """The edge attributes"""
        return self._edge_attributes

    @property
    def graphids(self) -> Set[str]:
        """The identifiers for graphs with either node or edge annotations"""
        return self._graphids

    @property
    def node_graphids(self) -> Set[str]:
        """The identifiers for graphs with node annotations"""
        return set(self.node_attributes)

    @property
    def edge_graphids(self) -> Set[str]:
        """The identifiers for graphs with edge annotations"""
        return set(self.edge_attributes)

    @property
    def metadata(self):
        """All metadata for this annotation"""
        return self._metadata

    @property
    def node_subspaces(self) -> Set[str]:
        """The subspaces for node annotations"""
        return self._node_subspaces

    @property
    def edge_subspaces(self) -> Set[str]:
        """The subspaces for edge annotations"""
        return self._edge_subspaces    
    
    @property
    def subspaces(self) -> Set[str]:
        """The subspaces for node and edge annotations"""
        return self.node_subspaces | self._edge_subspaces

    def properties(self, subspace: Optional[str] = None) -> Set[str]:
        """The properties in a subspace"""
        return self._metadata.properties(subspace)

    def property_metadata(self, subspace: str,
                          prop: str) -> UDSPropertyMetadata:
        """The metadata for a property in a subspace

        Parameters
        ----------
        subspace
            The subspace the property is in
        prop
            The property in the subspace
        """
        return self._metadata[subspace, prop]


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
                 data: Dict[str, Dict[str, NormalizedData]]):
        super().__init__(metadata, data)

    def _validate(self):
        super()._validate()

        if self._metadata.has_annotators():
            errmsg = 'metadata for NormalizedUDSAnnotation should ' +\
                     'not specify annotators'
            raise ValueError(errmsg)

    @classmethod
    @overrides
    def from_json(cls, jsonfile: Union[str, TextIO]) -> 'NormalizedUDSAnnotation':
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
        return super().from_json(jsonfile)


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
                 data: Dict[str, Dict[str, RawData]]):
        super().__init__(metadata, data)

    def _process_node_data(self, data: Dict[str, Dict[str, RawData]]):
        super()._process_node_data(data)

        self.node_attributes_by_annotator = _nested_defaultdict(5)

        for gid, attrs in self.node_attributes.items():
            for nid, subspaces in attrs.items():
                for subspace, properties in subspaces.items():                    
                    for prop, annotation in properties.items():
                        for annid, val in annotation['value'].items():
                            conf = annotation['confidence'][annid]
                            self.node_attributes_by_annotator[annid][gid][nid][subspace][prop] = \
                                {'confidence': conf, 'value': val}

        self.node_attributes_by_annotator =\
            _freeze_nested_defaultdict(self.node_attributes_by_annotator)

    def _process_edge_data(self, data: Dict[str, Dict[str, RawData]]):
        super()._process_edge_data(data)

        self.edge_attributes_by_annotator = _nested_defaultdict(5)

        for gid, attrs in self.edge_attributes.items():
            for nid, subspaces in attrs.items():
                for subspace, properties in subspaces.items():                    
                    for prop, annotation in properties.items():
                        for annid, val in annotation['value'].items():
                            conf = annotation['confidence'][annid]
                            self.edge_attributes_by_annotator[annid][gid][nid][subspace][prop] = \
                                {'confidence': conf, 'value': val}

        self.edge_attributes_by_annotator =\
            _freeze_nested_defaultdict(self.edge_attributes_by_annotator)


    @overrides
    def _validate(self):
        super()._validate()

        if not all(self._metadata.has_annotators(ss, p)
                   for ss in self._metadata.subspaces
                   for p in self._metadata.properties(ss)):
            errmsg = 'metadata for RawUDSAnnotation should ' +\
                     'specify annotators for all subspaces and properties'
            raise ValueError(errmsg)

    @classmethod
    @overrides
    def from_json(cls, jsonfile: Union[str, TextIO]) -> 'RawUDSAnnotation':
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
        return super().from_json(jsonfile)

    def annotators(self, subspace: Optional[str] = None,
                   prop: Optional[str] = None) -> Set[str]:
        """Annotator IDs for a subspace and property

        If neither subspace nor property are specified, all annotator
        IDs are returned. IF only the subspace is specified, all
        annotators IDs for the subspace are returned.

        Parameters
        ----------
        subspace
            The subspace to constrain to
        prop
            The property to constrain to 
        """
        return self._metadata.annotators(subspace, prop)

    def items(self, annotation_type: Optional[str] = None,
              annotator_id: Optional[str] = None):
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
            errmsg = 'annotation_type must be None, "node", or "edge"'
            raise ValueError(errmsg)

        if annotator_id is None:
            return super().items(annotation_type)

        elif annotation_type == "node":
            if annotator_id in self.node_attributes_by_annotator:
                for gid in self.graphids:
                    node_attrs = self.node_attributes_by_annotator[annotator_id][gid]

                    yield gid, node_attrs

            else:
                errmsg = '{} does not have associated '.format(annotator_id) +\
                         'node annotations'
                raise ValueError(errmsg)

        elif annotation_type == "edge":
            if annotator_id in self.edge_attributes_by_annotator:
                for gid in self.graphids:
                    edge_attrs = self.edge_attributes_by_annotator[annotator_id][gid]

                    yield gid, edge_attrs

            else:
                errmsg = '{} does not have associated '.format(annotator_id) +\
                         'edge annotations'
                raise ValueError(errmsg)

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

                yield gid, (node_attrs, edge_attrs)
