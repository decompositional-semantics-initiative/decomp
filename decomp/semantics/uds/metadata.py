"""Classes for representing UDS annotation metadata."""

from collections import defaultdict
from typing import TypeAlias, cast


PrimitiveType: TypeAlias = str | int | bool | float

UDSDataTypeDict: TypeAlias = dict[str, str | list[PrimitiveType] | bool | float]
PropertyMetadataDict: TypeAlias = dict[str,
                                       set[str] |
                                       dict[str, UDSDataTypeDict]]
AnnotationMetadataDict: TypeAlias = dict[str,
                                         dict[str, PropertyMetadataDict]]


def _dtype(name: str) -> type[PrimitiveType]:
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

    def __init__(self, datatype: type[PrimitiveType],
                 categories: list[PrimitiveType] | None = None,
                 ordered: bool | None = None,
                 lower_bound: float | None = None,
                 upper_bound: float | None = None):
        self._validate(datatype, categories, ordered,
                       lower_bound, upper_bound)

        self._datatype: type[PrimitiveType] = datatype
        self._categories: list[PrimitiveType] | set[PrimitiveType] | None = categories
        self._ordered: bool | None = ordered
        self._lower_bound: float | None = lower_bound
        self._upper_bound: float | None = upper_bound

        if ordered and categories is not None:
            if lower_bound is None:
                # for ordered categories, bounds should be numeric
                first_cat = categories[0]
                if isinstance(first_cat, (int, float)):
                    self._lower_bound = float(first_cat)

            if upper_bound is None:
                # for ordered categories, bounds should be numeric
                last_cat = categories[-1]
                if isinstance(last_cat, (int, float)):
                    self._upper_bound = float(last_cat)

        elif categories is not None:
            self._categories = set(categories)

        elif lower_bound is not None or upper_bound is not None:
            self._ordered = True

    def _validate(self, datatype: type[PrimitiveType],
                  categories: list[PrimitiveType] | None,
                  ordered: bool | None,
                  lower_bound: float | None,
                  upper_bound: float | None) -> None:
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UDSDataType):
            return NotImplemented
        self_dict = self.to_dict()
        other_dict = other.to_dict()

        return all(other_dict[k] == v for k, v in self_dict.items())

    @property
    def datatype(self) -> type[PrimitiveType]:
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
    def lower_bound(self) -> float | None:
        return self._lower_bound

    @property
    def upper_bound(self) -> float | None:
        return self._upper_bound

    @property
    def categories(self) -> set[PrimitiveType] | list[PrimitiveType] | None:
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
            datatype_value = datatype['datatype']
            if not isinstance(datatype_value, str):
                raise TypeError('datatype must be a string')
            typ = _dtype(datatype_value)

        else:
            errmsg = 'must specify "datatype" field'
            raise KeyError(errmsg)

        if 'categories' in datatype and\
           datatype['categories'] is not None:
            categories_value = datatype['categories']
            if not isinstance(categories_value, list):
                raise TypeError('categories must be a list')
            cats = [typ(c) for c in categories_value]

        else:
            cats = None

        ordered_value = datatype.get('ordered')
        ordered = bool(ordered_value) if ordered_value is not None else None

        lower_bound_value = datatype.get('lower_bound')
        if lower_bound_value is not None and isinstance(lower_bound_value, (int, float, str)):
            lower_bound = float(lower_bound_value)
        else:
            lower_bound = None

        upper_bound_value = datatype.get('upper_bound')
        if upper_bound_value is not None and isinstance(upper_bound_value, (int, float, str)):
            upper_bound = float(upper_bound_value)
        else:
            upper_bound = None

        return cls(typ, cats, ordered, lower_bound, upper_bound)

    def to_dict(self) -> UDSDataTypeDict:
        with_null: dict[str, str | list[PrimitiveType] | bool | float | None] = {
            'datatype': self._datatype.__name__,
            'categories': list(self._categories) if isinstance(self._categories, set) else self._categories,
            'ordered': self._ordered,
            'lower_bound': self._lower_bound,
            'upper_bound': self._upper_bound
        }

        # filter out None values and ensure types match UDSDataTypeDict
        result: UDSDataTypeDict = {}
        for k, v in with_null.items():
            if v is not None:
                result[k] = v
        return result

class UDSPropertyMetadata:
    """The metadata for a UDS property"""

    def __init__(self, value: UDSDataType,
                 confidence: UDSDataType,
                 annotators: set[str] | None = None):
        self._value = value
        self._confidence = confidence
        self._annotators = annotators

    def __eq__(self, other: object) -> bool:
        """Whether the value and confidence datatypes match and annotators are equal

        Parameters
        ----------
        other
            the other UDSDatatype
        """
        if not isinstance(other, UDSPropertyMetadata):
            return NotImplemented
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
    def annotators(self) -> set[str] | None:
        return self._annotators

    @classmethod
    def from_dict(cls,
                  metadata: PropertyMetadataDict) -> 'UDSPropertyMetadata':
        """
        Parameters
        ----------
        metadata
            A mapping from ``"value"`` and ``"confidence"`` to
            :class:`decomp.semantics.uds.metadata.UDSDataType`. This
            mapping may optionally specify a mapping from
            ``"annotators"`` to a set of annotator identifiers.
        """
        required = {'value', 'confidence'}
        missing = required - set(metadata)

        if missing:
            errmsg = 'the following metadata fields are missing: ' +\
                     ', '.join(missing)
            raise ValueError(errmsg)

        value_data_raw = metadata['value']
        confidence_data_raw = metadata['confidence']

        if not isinstance(value_data_raw, dict):
            raise TypeError('value must be a dictionary')
        if not isinstance(confidence_data_raw, dict):
            raise TypeError('confidence must be a dictionary')

        # these should be UDSDataTypeDict, not nested dicts
        value_data = cast(UDSDataTypeDict, value_data_raw)
        confidence_data = cast(UDSDataTypeDict, confidence_data_raw)

        value = UDSDataType.from_dict(value_data)
        confidence = UDSDataType.from_dict(confidence_data)

        if 'annotators' not in metadata or metadata['annotators'] is None:
            return UDSPropertyMetadata(value, confidence)

        else:
            annotators_data = metadata['annotators']
            # handle various types - annotators can be set or list
            if isinstance(annotators_data, set):
                return UDSPropertyMetadata(value, confidence, annotators_data)
            # check if it's a list and convert to set
            # mypy has trouble with type narrowing here
            try:
                return UDSPropertyMetadata(value, confidence, set(annotators_data))
            except TypeError:
                raise TypeError('annotators must be a set or list')

    def to_dict(self) -> PropertyMetadataDict:
        datatypes: dict[str, UDSDataTypeDict] = {
            'value': self._value.to_dict(),
            'confidence': self._confidence.to_dict()
        }

        if self._annotators is not None:
            # return type needs to match PropertyMetadataDict
            result: PropertyMetadataDict = {'annotators': self._annotators}
            # Cast datatypes to the appropriate type for PropertyMetadataDict
            result.update(cast(PropertyMetadataDict, datatypes))
            return result
        else:
            return cast(PropertyMetadataDict, datatypes)


class UDSAnnotationMetadata:
    """The metadata for UDS properties by subspace

    Parameters
    ----------
    metadata
        A mapping from subspaces to properties to datatypes and
        possibly annotators
    """

    def __init__(self, metadata: dict[str, dict[str, UDSPropertyMetadata]]):
        self._metadata = metadata

    def __getitem__(self,
                    k: str | tuple[str, str]) -> dict[str, UDSPropertyMetadata] | UDSPropertyMetadata:
        if isinstance(k, str):
            return self._metadata[k]
        elif isinstance(k, tuple) and len(k) == 2:
            # for tuple access like metadata[subspace, property]
            subspace, prop = k
            return self._metadata[subspace][prop]
        else:
            raise TypeError("Key must be a string or 2-tuple")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UDSAnnotationMetadata):
            return NotImplemented

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
    def metadata(self) -> dict[str, dict[str, UDSPropertyMetadata]]:
        """The metadata dictionary"""
        return self._metadata

    @property
    def subspaces(self) -> set[str]:
        """The subspaces in the metadata"""
        return set(self._metadata.keys())

    def properties(self, subspace: str | None = None) -> set[str]:
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

    def annotators(self, subspace: str | None = None,
                   prop: str | None = None) -> set[str] | None:
        if subspace is None and prop is not None:
            errmsg = 'subspace must be specified if prop is specified'
            raise ValueError(errmsg)

        if subspace is None:
            annotators: list[set[str]] = [md.annotators
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
            ann_set = self._metadata[subspace][prop].annotators
            annotators = [ann_set] if ann_set is not None else []

        if not annotators:
            return None

        else:
            return {ann for part in annotators for ann in part}

    def has_annotators(self, subspace: str | None = None,
                       prop: str | None = None) -> bool:
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
                  metadata: dict[str, AnnotationMetadataDict]) -> 'UDSCorpusMetadata':
        return cls(UDSAnnotationMetadata.from_dict(metadata['sentence_metadata']),
                   UDSAnnotationMetadata.from_dict(metadata['document_metadata']))

    def to_dict(self) -> dict[str, AnnotationMetadataDict]:
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
    def sentence_subspaces(self) -> set[str]:
        return self._sentence_metadata.subspaces

    @property
    def document_subspaces(self) -> set[str]:
        return self._document_metadata.subspaces

    def sentence_properties(self, subspace: str | None = None) -> set[str]:
        """The properties in a sentence subspace

        Parameters
        ----------
        subspace
            The subspace to get the properties of
        """
        return self._sentence_metadata.properties(subspace)

    def document_properties(self, subspace: str | None = None) -> set[str]:
        """The properties in a document subspace

        Parameters
        ----------
        subspace
            The subspace to get the properties of
        """
        return self._document_metadata.properties(subspace)

    def sentence_annotators(self, subspace: str | None = None,
                            prop: str | None = None) -> set[str] | None:
        """The annotators for a property in a sentence subspace

        Parameters
        ----------
        subspace
            The subspace to get the annotators of
        prop
            The property to get the annotators of
        """
        return self._sentence_metadata.annotators(subspace, prop)

    def document_annotators(self, subspace: str | None = None,
                            prop: str | None = None) -> set[str] | None:
        """The annotators for a property in a document subspace

        Parameters
        ----------
        subspace
            The subspace to get the annotators of
        prop
            The property to get the annotators of
        """
        return self._document_metadata.annotators(subspace, prop)

    def has_sentence_annotators(self, subspace: str | None = None,
                                prop: str | None = None) -> bool:
        return self._sentence_metadata.has_annotators(subspace, prop)

    def has_document_annotators(self, subspace: str | None = None,
                                prop: str | None = None) -> bool:
        return self._document_metadata.has_annotators(subspace, prop)
