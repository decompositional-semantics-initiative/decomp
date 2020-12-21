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
    lower_bound
        The lower bound value. Neither ``categories`` nor ``ordered``
        need be specified for this to be specified, though if both
        ``categories`` and this are specified, the datatype must be
        ordered and the lower bound must match the lower bound of the
        categories.
    upper_bound
        The upper bound value. Neither ``categories`` nor ``ordered``
        need be specified for this to be specified, though if both
        ``categories`` and this are specified, the datatype must be
        ordered and the upper bound must match the upper bound of the
        categories.
    """

    def __init__(self, datatype: PrimitiveType,
                 categories: Optional[List[PrimitiveType]] = None,
                 ordered: Optional[bool] = None,
                 lower_bound: Optional[float] = None,
                 upper_bound: Optional[float] = None):
        self._validate(datatype, categories, ordered,
                       lower_bound, upper_bound)

        self._datatype = datatype
        self._categories = categories
        self._ordered = ordered
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

        if ordered and categories is not None:
            if lower_bound is None:
                self._lower_bound = self._categories[0]

            if upper_bound is None:
                self._upper_bound = self._categories[-1]

        elif categories is not None:
            self._categories = set(categories)

        elif lower_bound is not None or upper_bound is not None:
            self._ordered = True

    def _validate(self, datatype, categories, ordered,
                  lower_bound, upper_bound):
        if ordered is not None and\
           categories is None and\
           lower_bound is None and\
           upper_bound is None:
            errmsg = "if ordered is specified either categories or "\
                     "lower_bound and/or upper_bound must be also"
            raise ValueError(errmsg)

        if categories is not None and ordered is None:
            errmsg = "if categories is specified ordered must "\
                     "be specified also"
            raise ValueError(errmsg)

        if categories is not None and datatype not in [str, int]:
            errmsg = "categorical variable must be str- "\
                     "or int-valued"
            raise ValueError(errmsg)

        if lower_bound is not None or upper_bound is not None:
            if categories is not None and not ordered:
                errmsg = "if categorical datatype is unordered, upper "\
                         "and lower bounds should not be specified"
                raise ValueError(errmsg)

            if categories is not None and\
               lower_bound is not None and\
               lower_bound != categories[0]:
                errmsg = "lower bound does not match categories lower bound"
                raise ValueError(errmsg)

            if categories is not None and\
               upper_bound is not None and\
               upper_bound != categories[-1]:
                errmsg = "upper bound does not match categories upper bound"
                raise ValueError(errmsg)

    def __eq__(self, other: 'UDSDataType') -> bool:
        self_dict = self.to_dict()
        other_dict = other.to_dict()

        return all(other_dict[k] == v for k, v in self_dict.items())

    @property
    def datatype(self) -> Type:
        return self._datatype

    @property
    def is_categorical(self) -> bool:
        return self._categories is not None

    @property
    def is_ordered_categorical(self) -> bool:
        return self.is_categorical and bool(self._ordered)

    @property
    def is_ordered_noncategorical(self) -> bool:
        return not self.is_categorical and bool(self._ordered)

    @property
    def lower_bound(self) -> PrimitiveType:
        return self._lower_bound

    @property
    def upper_bound(self) -> PrimitiveType:
        return self._upper_bound

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
                         'ordered',
                         'lower_bound',
                         'upper_bound']
               for k in datatype):
            errmsg = 'dictionary defining datatype has keys ' +\
                     ', '.join('"' + k + '"' for k in datatype.keys()) +\
                     'but it may only have "datatype", "categories", ' +\
                     '"ordered", "lower_bound", and "upper_bound" as keys'

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

        if 'lower_bound' in datatype:
            lower_bound = datatype['lower_bound']

        else:
            lower_bound = None

        if 'upper_bound' in datatype:
            upper_bound = datatype['upper_bound']

        else:
            upper_bound = None

        return cls(typ, cats, ordered, lower_bound, upper_bound)

    def to_dict(self) -> UDSDataTypeDict:
        with_null = {'datatype': self._datatype.__name__,
                     'categories': self._categories,
                     'ordered': self._ordered,
                     'lower_bound': self._lower_bound,
                     'upper_bound': self._upper_bound}

        return {k: list(v) if isinstance(v, set) else v
                for k, v
                in with_null.items() if v is not None}

class UDSPropertyMetadata:
    """The metadata for a UDS property"""

    def __init__(self, value: UDSDataType,
                 confidence: UDSDataType,
                 annotators: Optional[Set[str]] = None):
        self._value = value
        self._confidence = confidence
        self._annotators = annotators

    def __eq__(self, other: 'UDSPropertyMetadata') -> bool:
        """Whether the value and confidence datatypes match and annotators are equal

        Parameters
        ----------
        other
            the other UDSDatatype
        """
        return self.value == other.value and\
            self.confidence == other.confidence and\
            self.annotators == other.annotators

    def __add__(self, other: 'UDSPropertyMetadata') -> 'UDSPropertyMetadata':
        """A UDSPropertyMetadata with the union of annotators

        If the value and confidence datatypes don't match, this raises
        an error

        Parameters
        ----------
        other
            the other UDSDatatype

        Raises
        ------
        ValueError
            Raised if the value and confidence datatypes don't match
        """
        if self.value != other.value or self.confidence != other.confidence:
            errmsg = 'Cannot add metadata whose value and confidence '\
                     'datatypes are not equal'
            raise ValueError(errmsg)

        if self.annotators is None and other.annotators is None:
            return self

        elif self.annotators is None:
            return UDSPropertyMetadata(self.value, self.confidence,
                                       other.annotators)

        elif other.annotators is None:
            return UDSPropertyMetadata(self.value, self.confidence,
                                       self.annotators)

        else:
            return UDSPropertyMetadata(self.value, self.confidence,
                                       self.annotators | other.annotators)

    @property
    def value(self) -> UDSDataType:
        return self._value

    @property
    def confidence(self) -> UDSDataType:
        return self._confidence

    @property
    def annotators(self) -> Optional[Set[str]]:
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

    def to_dict(self) -> PropertyMetadataDict:
        datatypes = {'value': self._value.to_dict(),
                     'confidence': self._confidence.to_dict()}

        if self._annotators is not None:
            return dict({'annotators': list(self._annotators)},
                        **datatypes)

        else:
            return datatypes


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

    def __eq__(self, other: 'UDSAnnotationMetadata') -> bool:
        if self.subspaces != other.subspaces:
            return False

        for ss in self.subspaces:
            if self.properties(ss) != other.properties(ss):
                return False

            for prop in self.properties(ss):
                if self[ss, prop] != other[ss, prop]:
                    return False

        return True

    def __add__(self,
                other: 'UDSAnnotationMetadata') -> 'UDSAnnotationMetadata':
        new_metadata = defaultdict(dict, self.metadata)

        for subspace, propdict in other.metadata.items():
            for prop, md in propdict.items():
                if prop in new_metadata[subspace]:
                    new_metadata[subspace][prop] += md
                else:
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
    def from_dict(cls, metadata: AnnotationMetadataDict) -> 'UDSAnnotationMetadata':
        return cls({subspace: {prop: UDSPropertyMetadata.from_dict(md)
                               for prop, md
                               in propdict.items()}
                    for subspace, propdict in metadata.items()})

    def to_dict(self) -> AnnotationMetadataDict:
        return {subspace: {prop: md.to_dict()
                           for prop, md
                           in propdict.items()}
                for subspace, propdict in self._metadata.items()}

class UDSCorpusMetadata:
    """The metadata for UDS properties by subspace

    This is a thin wrapper around a pair of ``UDSAnnotationMetadata``
    objects: one for sentence annotations and one for document
    annotations.

    Parameters
    ----------
    sentence_metadata
        The metadata for sentence annotations
    document_metadata
        The metadata for document_annotations
    """

    def __init__(self,
                 sentence_metadata: UDSAnnotationMetadata = UDSAnnotationMetadata({}),
                 document_metadata: UDSAnnotationMetadata = UDSAnnotationMetadata({})):
        self._sentence_metadata = sentence_metadata
        self._document_metadata = document_metadata

    @classmethod
    def from_dict(cls,
                  metadata: Dict[str, AnnotationMetadataDict]) -> 'UDSCorpusMetadata':
        return cls(UDSAnnotationMetadata.from_dict(metadata['sentence_metadata']),
                   UDSAnnotationMetadata.from_dict(metadata['document_metadata']))

    def to_dict(self) -> Dict[str, AnnotationMetadataDict]:
        return {'sentence_metadata': self._sentence_metadata.to_dict(),
                'document_metadata': self._document_metadata.to_dict()}

    def __add__(self, other: 'UDSCorpusMetadata') -> 'UDSCorpusMetadata':
        new_sentence_metadata = self._sentence_metadata + other._sentence_metadata
        new_document_metadata = self._document_metadata + other._document_metadata

        return self.__class__(new_sentence_metadata, new_document_metadata)

    def add_sentence_metadata(self, metadata: UDSAnnotationMetadata) -> None:
        self._sentence_metadata += metadata

    def add_document_metadata(self, metadata: UDSAnnotationMetadata) -> None:
        self._document_metadata += metadata

    @property
    def sentence_metadata(self) -> UDSAnnotationMetadata:
        return self._sentence_metadata   

    @property
    def document_metadata(self) -> UDSAnnotationMetadata:
        return self._document_metadata   

    @property
    def sentence_subspaces(self) -> Set[str]:
        return self._sentence_metadata.subspaces

    @property
    def document_subspaces(self) -> Set[str]:
        return self._document_metadata.subspaces

    def sentence_properties(self, subspace: Optional[str] = None) -> Set[str]:
        """The properties in a sentence subspace

        Parameters
        ----------
        subspace
            The subspace to get the properties of
        """
        return self._sentence_metadata.properties(subspace)

    def document_properties(self, subspace: Optional[str] = None) -> Set[str]:
        """The properties in a document subspace

        Parameters
        ----------
        subspace
            The subspace to get the properties of
        """
        return self._document_metadata.properties(subspace)

    def sentence_annotators(self, subspace: Optional[str] = None,
                            prop: Optional[str] = None) -> Set[str]:
        """The annotators for a property in a sentence subspace

        Parameters
        ----------
        subspace
            The subspace to get the annotators of
        prop
            The property to get the annotators of
        """
        return self._sentence_metadata.annotators(subspace, prop)

    def document_annotators(self, subspace: Optional[str] = None,
                            prop: Optional[str] = None) -> Set[str]:
        """The annotators for a property in a document subspace

        Parameters
        ----------
        subspace
            The subspace to get the annotators of
        prop
            The property to get the annotators of
        """
        return self._document_metadata.annotators(subspace, prop)

    def has_sentence_annotators(self, subspace: Optional[str] = None,
                                prop: Optional[str] = None) -> bool:
        return self._sentence_metadata.has_annotators(subspace, prop)

    def has_document_annotators(self, subspace: Optional[str] = None,
                                prop: Optional[str] = None) -> bool:
        return self._document_metadata.has_annotators(subspace, prop)
