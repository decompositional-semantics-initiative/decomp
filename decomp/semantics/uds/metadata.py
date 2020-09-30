"""Classes for representing annotation metadata"""

from typing import Union, Optional, Type
from typing import Dict, List, Tuple, Set
from collections import defaultdict


PrimitiveType = Union[str, int, bool, float]

UDSDataTypeDict = Dict[str, Union[str, List[PrimitiveType], bool]]
PropertyMetadataDict = Dict[str,
                            Union[Set[str],
                                  Dict[str, UDSDataTypeDict]]]
AnnotationMetadataDict = Dict[str,
                              Dict[str, PropertyMetadataDict]]

def _dtype(name: str) -> Type:
    """Convert string to a type

    Only ``str``, ``int``, ``bool``, and ``float`` are supported. 

    Parameters
    ----------
    name
        A string representing the type
    """

    if name == 'str':
        return str
    elif name == 'int':
        return int
    elif name == 'bool':
        return bool
    elif name == 'float':
        return float
    else:
        errmsg = 'name must be "str", "int",' +\
                 ' "bool", or "float"'        
        raise ValueError(errmsg)


class UDSDataType:
    """A thin wrapper around builtin datatypes

    This class is mainly intended to provide a minimal extension of
    basic builtin datatypes for representing categorical
    datatypes. ``pandas`` provides a more fully featured version of
    such a categorical datatype but would add an additional dependency
    that is heavyweight and otherwise unnecessary.

    Parameters
    ----------
    datatype
        A builtin datatype
    categories
        The values the datatype can take on (if applicable)
    ordered
        If this is a categorical datatype, whether it is ordered
    """

    def __init__(self, datatype: PrimitiveType,
                 categories: Optional[List[PrimitiveType]] = None,
                 ordered: Optional[bool] = None):
        self._datatype = datatype

        if ordered:
            self._categories = categories

        elif categories is not None:
            self._categories = set(categories)

        else:
            self._categories = None

        self._ordered = ordered

        self._validate()

    def _validate(self):
        if self._categories is None and\
           self._ordered is not None:
            errmsg = "both categories and ordered must "\
                     "be specified"
            raise ValueError(errmsg)

        if self._categories is not None and\
           self._ordered is None:
            errmsg = "both categories and ordered must "\
                     "be specified"
            raise ValueError(errmsg)

        if self._categories is not None and\
           self._datatype not in [str, int]:
            errmsg = "categorical variable must be numpy.str "\
                     "or numpy.int valued"
            raise ValueError(errmsg)

    @property
    def datatype(self) -> Type:
        return self._datatype

    @property
    def is_categorical(self) -> bool:
        return self._categories is not None

    @property
    def is_ordered_categorical(self) -> bool:
        return bool(self._ordered)

    @property
    def categories(self) -> Union[Set[PrimitiveType],
                                  List[PrimitiveType]]:
        """The categories

        A set of the datatype is unordered and a list if it is ordered

        Raises
        ------
        ValueError
            If this is not a categorical datatype, an error is raised
        """
        if self._categories is None:
            errmsg = "not a categorical dtype"
            raise AttributeError(errmsg)

        return self._categories

    @classmethod
    def from_dict(cls, datatype: UDSDataTypeDict) -> 'UDSDataType':
        """Build a UDSDataType from a dictionary

        Parameters
        ----------
        datatype
            A dictionary representing a datatype. This dictionary must
            at least have a ``"datatype"`` key. It may also have a
            ``"categorical"`` and an ``"ordered"`` key, in which case
            it must have both.
        """
        if any(k not in ['datatype',
                         'categories',
                         'ordered']
               for k in datatype):
            errmsg = 'dictionary defining datatype has keys ' +\
                     ', '.join('"' + k + '"' for k in datatype.keys()) +\
                     'but it may only have "datatype", "categories", and ' +\
                     '"ordered" as keys'

            raise KeyError(errmsg)

        if 'datatype' in datatype:
            typ = _dtype(datatype['datatype'])

        else:
            errmsg = 'must specify "datatype" field'
            raise KeyError(errmsg)

        if 'categories' in datatype and\
           datatype['categories'] is not None:
            cats = [typ(c) for c in datatype['categories']]

        else:
            cats = None

        ordered = datatype['ordered'] if 'ordered' in datatype else None

        return cls(typ, cats, ordered)

class UDSPropertyMetadata:
    """The metadata for a UDS property

    """

    def __init__(self, value: UDSDataType,
                 confidence: UDSDataType,
                 annotators: Optional[Set[str]] = None):
        self._value = value
        self._confidence = confidence
        self._annotators = annotators

    @property
    def value(self):
        return self._value

    @property
    def confidence(self):
        return self._confidence

    @property
    def annotators(self):
        return self._annotators

    @classmethod
    def from_dict(cls,
                  metadata: PropertyMetadataDict) -> 'UDSPropertyMetadata':
        """
        Parameters
        ----------
        metadata
            A mapping from ``"value"`` and ``"confidence"`` to
            :class:`decomp.semantics.uds.metadata.UDSDataType`s. This
            mapping may optionally specify a mapping from
            ``"annotators"`` to a set of annotator identifiers
        """
        required = {'value', 'confidence'}
        missing = required - set(metadata)

        if missing:
            errmsg = 'the following metadata fields are missing: ' +\
                     ', '.join(missing)
            raise ValueError(missing)

        value = UDSDataType.from_dict(metadata['value'])
        confidence = UDSDataType.from_dict(metadata['confidence'])

        if 'annotators' not in metadata or metadata['annotators'] is None:
            return UDSPropertyMetadata(value, confidence)

        else:
            annotators = set(metadata['annotators'])
            return UDSPropertyMetadata(value, confidence, annotators)


class UDSAnnotationMetadata:
    """The metadata for UDS properties by subspace

    Parameters
    ----------
    metadata
        A mapping from subspaces to properties to datatypes and
        possibly annotators
    """

    def __init__(self, metadata: Dict[str, Dict[str, UDSPropertyMetadata]]):
        self._metadata = metadata

    def __getitem__(self,
                    k: Union[str, Tuple[str]]) -> Dict:
        if isinstance(k, str):
            return self._metadata[k]
        elif isinstance(k, tuple):
            out = self._metadata[k[0]]

            for i in k[1:]:
                out = out[i]

            return out

    def __add__(self,
                other: 'UDSAnnotationMetadata') -> 'UDSAnnotationMetadata':
        new_metadata = defaultdict(dict, self.metadata)

        for subspace, propdict in other.metadata.items():
            for prop, md in propdict.items():
                if prop in new_metadata[subspace]:
                    errmsg = 'both instances of UDSAnnotationMetadata are ' +\
                             'specified for property {} '.format(prop) +\
                             'in subspace {}'.format(subspace)
                    raise ValueError(errmsg)

                new_metadata[subspace][prop] = md

        return UDSAnnotationMetadata(new_metadata)

    @property
    def metadata(self):
        return self._metadata   

    @property
    def subspaces(self) -> Set[str]:
        return set(self._metadata.keys())

    def properties(self, subspace: Optional[str] = None) -> Set[str]:
        """The properties in a subspace

        Parameters
        ----------
        subspace
            The subspace to get the properties of
        """
        if subspace is None:
            return {prop for propdict in self._metadata.values()
                    for prop in propdict}

        else:
            return set(self._metadata[subspace])

    def annotators(self, subspace: Optional[str] = None,
                   prop: Optional[str] = None) -> Set[str]:
        if subspace is None and prop is not None:
            errmsg = 'subspace must be specified if prop is specified'
            raise ValueError(errmsg)

        if subspace is None:
            annotators = [md.annotators
                          for propdict in self._metadata.values()
                          for md in propdict.values()
                          if md.annotators is not None]

        elif prop is None:
            annotators = [md.annotators
                          for md in self._metadata[subspace].values()
                          if md.annotators is not None]

        elif self._metadata[subspace][prop].annotators is None:
            annotators = []

        else:
            annotators = [self._metadata[subspace][prop].annotators]

        if not annotators:
            return None

        else:
            return {ann for part in annotators for ann in part}

    def has_annotators(self, subspace: Optional[str] = None,
                       prop: Optional[str] = None) -> bool:
        return bool(self.annotators(subspace, prop))

    @classmethod
    def from_dict(cls, metadata: AnnotationMetadataDict):
        return cls({subspace: {prop: UDSPropertyMetadata.from_dict(md)
                               for prop, md
                               in propdict.items()}
                    for subspace, propdict in metadata.items()})
