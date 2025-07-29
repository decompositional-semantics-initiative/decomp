"""Metadata structures for Universal Decompositional Semantics (UDS) annotations.

This module defines the metadata infrastructure used to describe and validate
UDS semantic annotations across sentence and document graphs. It provides a
flexible type system that supports both categorical and continuous values
with optional bounds and ordering constraints.

Key Components
--------------
Type System
    - :data:`PrimitiveType`: Base types supported in UDS (str, int, bool, float)
    - :data:`UDSDataTypeDict`: Dictionary format for serializing data types
    - :class:`UDSDataType`: Wrapper for primitive types with categorical support

Property Metadata
    - :data:`PropertyMetadataDict`: Dictionary format for property metadata
    - :class:`UDSPropertyMetadata`: Metadata for individual semantic properties

Annotation Metadata
    - :data:`AnnotationMetadataDict`: Dictionary format for annotation metadata
    - :class:`UDSAnnotationMetadata`: Collection of properties organized by subspace
    - :class:`UDSCorpusMetadata`: Complete metadata for sentence and document graphs

The metadata system ensures consistency across UDS corpora by tracking:
- Property names and their expected data types
- Categorical values and their ordering
- Numeric bounds for continuous properties
- Confidence score types for uncertain annotations
- Subspace organization of semantic properties

See Also
--------
decomp.semantics.uds.annotation : Annotation classes that use this metadata
decomp.semantics.uds.corpus : Corpus classes that store metadata
"""

from collections import defaultdict
from typing import Literal, cast

from decomp.semantics.uds.types import UDSSubspace


# Type aliases for UDS metadata structures
type PrimitiveType = str | int | bool | float
"""Union of primitive types supported in UDS annotations: str, int, bool, float."""

type UDSDataTypeDict = dict[
    str,
    str | list[PrimitiveType] | bool | float
]
"""Dictionary representation of a UDS data type with optional categories and bounds."""

type PropertyMetadataDict = dict[
    str,
    set[str] | dict[str, UDSDataTypeDict]
]
"""Dictionary representation of property metadata including value/confidence types."""

type AnnotationMetadataDict = dict[
    str,
    dict[str, PropertyMetadataDict]
]
"""Dictionary mapping subspaces to their property metadata."""


def _dtype(name: str) -> type[PrimitiveType]:
    """Convert string representation to a primitive type class.

    Only ``str``, ``int``, ``bool``, and ``float`` are supported.

    Parameters
    ----------
    name : str
        A string representing the type ("str", "int", "bool", or "float").

    Returns
    -------
    type[PrimitiveType]
        The corresponding type class.

    Raises
    ------
    ValueError
        If name is not one of the supported type strings.
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
        raise ValueError(
            f'name must be "str", "int", "bool", or "float", not {name}'
        )


class UDSDataType:
    """A wrapper around builtin datatypes with support for categorical values.

    This class provides a minimal extension of basic builtin datatypes for
    representing categorical datatypes with optional ordering and bounds.
    It serves as a lightweight alternative to `pandas` categorical types.

    Parameters
    ----------
    datatype : type[PrimitiveType]
        A builtin datatype (str, int, bool, or float).
    categories : list[PrimitiveType] | None, optional
        The allowed values for categorical datatypes. Required if ordered is True.
    ordered : bool | None, optional
        Whether this categorical datatype has an ordering. Required if categories
        is specified.
    lower_bound : float | None, optional
        The lower bound value for numeric types. Can be specified independently
        of categories. If both categories and lower_bound are specified, the
        datatype must be ordered and bounds must match category bounds.
    upper_bound : float | None, optional
        The upper bound value for numeric types. Can be specified independently
        of categories. If both categories and upper_bound are specified, the
        datatype must be ordered and bounds must match category bounds.

    Attributes
    ----------
    datatype : type[PrimitiveType]
        The underlying primitive type.
    is_categorical : bool
        Whether this represents a categorical datatype.
    is_ordered_categorical : bool
        Whether this is an ordered categorical datatype.
    is_ordered_noncategorical : bool
        Whether this is ordered but not categorical (has bounds).
    lower_bound : float | None
        The lower bound if specified.
    upper_bound : float | None
        The upper bound if specified.
    categories : set[PrimitiveType] | list[PrimitiveType] | None
        The categories as a set (unordered) or list (ordered).
    """

    def __init__(
        self,
        datatype: type[PrimitiveType],
        categories: list[PrimitiveType] | None = None,
        ordered: bool | None = None,
        lower_bound: float | None = None,
        upper_bound: float | None = None
    ) -> None:
        self._validate(
            datatype,
            categories,
            ordered,
            lower_bound,
            upper_bound
        )

        self._datatype: type[PrimitiveType] = datatype
        self._categories: list[PrimitiveType] | set[PrimitiveType] | None = (
            categories
        )
        self._ordered: bool | None = ordered
        self._lower_bound: float | None = lower_bound
        self._upper_bound: float | None = upper_bound

        if ordered and categories is not None:
            if lower_bound is None:
                # for ordered categories, bounds should be numeric
                first_cat = categories[0]
                if isinstance(first_cat, int | float):
                    self._lower_bound = float(first_cat)

            if upper_bound is None:
                # for ordered categories, bounds should be numeric
                last_cat = categories[-1]
                if isinstance(last_cat, int | float):
                    self._upper_bound = float(last_cat)

        elif categories is not None:
            self._categories = set(categories)

        elif lower_bound is not None or upper_bound is not None:
            self._ordered = True

    def _validate(
        self,
        datatype: type[PrimitiveType],
        categories: list[PrimitiveType] | None,
        ordered: bool | None,
        lower_bound: float | None,
        upper_bound: float | None
    ) -> None:
        """Validate datatype parameters for consistency.

        Parameters
        ----------
        datatype : type[PrimitiveType]
            The primitive type.
        categories : list[PrimitiveType] | None
            Optional category values.
        ordered : bool | None
            Whether categories are ordered.
        lower_bound : float | None
            Optional lower bound.
        upper_bound : float | None
            Optional upper bound.

        Raises
        ------
        ValueError
            If the parameter combination is invalid.
        """
        if (
            ordered is not None
            and categories is None
            and lower_bound is None
            and upper_bound is None
        ):
            raise ValueError(
                'if ordered is specified either categories or '
                'lower_bound and/or upper_bound must be also'
            )

        if categories is not None and ordered is None:
            raise ValueError(
                'if categories is specified ordered must be specified also'
            )

        if categories is not None and datatype not in [str, int]:
            raise ValueError(
                'categorical variable must be str- or int-valued'
            )

        if lower_bound is not None or upper_bound is not None:
            if categories is not None and not ordered:
                raise ValueError(
                    'if categorical datatype is unordered, upper '
                    'and lower bounds should not be specified'
                )

            if (
                categories is not None
                and lower_bound is not None
                and lower_bound != categories[0]
            ):
                raise ValueError(
                    'lower bound does not match categories lower bound'
                )

            if (
                categories is not None
                and upper_bound is not None
                and upper_bound != categories[-1]
            ):
                raise ValueError(
                    'upper bound does not match categories upper bound'
                )

    def __eq__(self, other: object) -> bool:
        """Check equality based on dictionary representation.

        Parameters
        ----------
        other : object
            Object to compare with.

        Returns
        -------
        bool
            True if both objects have the same dictionary representation.
        """
        if not isinstance(other, UDSDataType):
            return NotImplemented
        self_dict = self.to_dict()
        other_dict = other.to_dict()

        return all(other_dict[k] == v for k, v in self_dict.items())

    @property
    def datatype(self) -> type[PrimitiveType]:
        """The underlying primitive type.

        Returns
        -------
        type[PrimitiveType]
            The primitive type (str, int, bool, or float).
        """
        return self._datatype

    @property
    def is_categorical(self) -> bool:
        """Whether this datatype has defined categories.

        Returns
        -------
        bool
            True if categories are defined.
        """
        return self._categories is not None

    @property
    def is_ordered_categorical(self) -> bool:
        """Whether this is a categorical datatype with ordering.

        Returns
        -------
        bool
            True if categorical and ordered.
        """
        return self.is_categorical and bool(self._ordered)

    @property
    def is_ordered_noncategorical(self) -> bool:
        """Whether this has ordering but no categories (bounded numeric).

        Returns
        -------
        bool
            True if ordered but not categorical.
        """
        return not self.is_categorical and bool(self._ordered)

    @property
    def lower_bound(self) -> float | None:
        """The lower bound value if specified.

        Returns
        -------
        float | None
            The lower bound or None.
        """
        return self._lower_bound

    @property
    def upper_bound(self) -> float | None:
        """The upper bound value if specified.

        Returns
        -------
        float | None
            The upper bound or None.
        """
        return self._upper_bound

    @property
    def categories(self) -> set[PrimitiveType] | list[PrimitiveType] | None:
        """The allowed category values.

        Returns a set if the datatype is unordered categorical and a list
        if it is ordered categorical.

        Returns
        -------
        set[PrimitiveType] | list[PrimitiveType] | None
            Categories as set (unordered), list (ordered), or None.

        Raises
        ------
        AttributeError
            If this is not a categorical datatype.
        """
        if self._categories is None:
            raise AttributeError('not a categorical dtype')

        return self._categories

    @classmethod
    def from_dict(cls, datatype: UDSDataTypeDict) -> 'UDSDataType':
        """Build a UDSDataType from a dictionary.

        Parameters
        ----------
        datatype
            A dictionary representing a datatype. This dictionary must
            at least have a ``"datatype"`` key. It may also have a
            ``"categorical"`` and an ``"ordered"`` key, in which case
            it must have both.
        """
        if any(
            k not in [
                'datatype',
                'categories',
                'ordered',
                'lower_bound',
                'upper_bound'
            ]
            for k in datatype
        ):
            raise KeyError(
                f'dictionary defining datatype has keys '
                f'{", ".join(f'"{k}"' for k in datatype)} '
                f'but it may only have "datatype", "categories", '
                f'"ordered", "lower_bound", and "upper_bound" as keys'
            )

        if 'datatype' in datatype:
            datatype_value = datatype['datatype']
            if not isinstance(datatype_value, str):
                raise TypeError('datatype must be a string')
            typ = _dtype(datatype_value)

        else:
            raise KeyError('must specify "datatype" field')

        if 'categories' in datatype and datatype['categories'] is not None:
            categories_value = datatype['categories']
            if not isinstance(categories_value, list):
                raise TypeError('categories must be a list')
            cats = [typ(c) for c in categories_value]

        else:
            cats = None

        ordered_value = datatype.get('ordered')
        ordered = bool(ordered_value) if ordered_value is not None else None

        lower_bound_value = datatype.get('lower_bound')

        if (
            lower_bound_value is not None
            and isinstance(lower_bound_value, int | float | str)
        ):
            lower_bound = float(lower_bound_value)

        else:
            lower_bound = None

        upper_bound_value = datatype.get('upper_bound')

        if (
            upper_bound_value is not None
            and isinstance(upper_bound_value, int | float | str)
        ):
            upper_bound = float(upper_bound_value)

        else:
            upper_bound = None

        return cls(typ, cats, ordered, lower_bound, upper_bound)

    def to_dict(self) -> UDSDataTypeDict:
        """Convert to dictionary representation.

        Returns
        -------
        UDSDataTypeDict
            Dictionary with datatype info, excluding None values.
        """
        with_null: dict[str, str | list[PrimitiveType] | bool | float | None] = {
            'datatype': self._datatype.__name__,
            'categories': (
                list(self._categories)
                if isinstance(self._categories, set)
                else self._categories
            ),
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
    """Metadata for a UDS property including value and confidence datatypes.

    This class encapsulates the metadata for a single UDS property, including
    the datatypes for both the property value and the confidence score, as well
    as optional annotator information.

    Parameters
    ----------
    value : UDSDataType
        The datatype for property values.
    confidence : UDSDataType
        The datatype for confidence scores.
    annotators : set[str] | None, optional
        Set of annotator identifiers who provided annotations for this property.

    Attributes
    ----------
    value : UDSDataType
        The value datatype.
    confidence : UDSDataType
        The confidence datatype.
    annotators : set[str] | None
        The annotator identifiers.
    """

    def __init__(
        self,
        value: UDSDataType,
        confidence: UDSDataType,
        annotators: set[str] | None = None
    ) -> None:
        self._value = value
        self._confidence = confidence
        self._annotators = annotators

    def __eq__(self, other: object) -> bool:
        """Whether the value and confidence datatypes match and annotators are equal.

        Parameters
        ----------
        other
            the other UDSDatatype.
        """
        if not isinstance(other, UDSPropertyMetadata):
            return NotImplemented
        return (
            self.value == other.value
            and self.confidence == other.confidence
            and self.annotators == other.annotators
        )

    def __add__(self, other: 'UDSPropertyMetadata') -> 'UDSPropertyMetadata':
        """Return a UDSPropertyMetadata with the union of annotators.

        If the value and confidence datatypes don't match, this raises
        an error.

        Parameters
        ----------
        other
            the other UDSDatatype.

        Raises
        ------
        ValueError
            Raised if the value and confidence datatypes don't match.
        """
        if self.value != other.value or self.confidence != other.confidence:
            raise ValueError(
                'Cannot add metadata whose value and confidence '
                'datatypes are not equal'
            )

        if self.annotators is None and other.annotators is None:
            return self

        elif self.annotators is None:
            return UDSPropertyMetadata(
                self.value, self.confidence, other.annotators
            )

        elif other.annotators is None:
            return UDSPropertyMetadata(
                self.value, self.confidence, self.annotators
            )

        else:
            return UDSPropertyMetadata(
                self.value, self.confidence, self.annotators | other.annotators
            )

    @property
    def value(self) -> UDSDataType:
        """The datatype for property values.

        Returns
        -------
        UDSDataType
            The value datatype.
        """
        return self._value

    @property
    def confidence(self) -> UDSDataType:
        """The datatype for confidence scores.

        Returns
        -------
        UDSDataType
            The confidence datatype.
        """
        return self._confidence

    @property
    def annotators(self) -> set[str] | None:
        """The set of annotator identifiers.

        Returns
        -------
        set[str] | None
            Annotator IDs or None if not tracked.
        """
        return self._annotators

    @classmethod
    def from_dict(
        cls, metadata: PropertyMetadataDict
    ) -> 'UDSPropertyMetadata':
        """Build UDSPropertyMetadata from a dictionary.

        Parameters
        ----------
        metadata : PropertyMetadataDict
            A mapping from ``"value"`` and ``"confidence"`` to
            datatype dictionaries. May optionally include ``"annotators"``
            mapping to a set of annotator identifiers.

        Returns
        -------
        UDSPropertyMetadata
            The constructed metadata object.

        Raises
        ------
        ValueError
            If required fields (value, confidence) are missing.
        TypeError
            If fields have incorrect types
        """
        required = {'value', 'confidence'}
        missing = required - set(metadata)

        if missing:
            raise ValueError(
                f'the following metadata fields are missing: {", ".join(missing)}'
            )

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
                return UDSPropertyMetadata(
                value, confidence, set(annotators_data)
            )

            except TypeError:
                raise TypeError('annotators must be a set or list') from None

    def to_dict(self) -> PropertyMetadataDict:
        """Convert to dictionary representation.

        Returns
        -------
        PropertyMetadataDict
            Dictionary with value, confidence, and optional annotators.
        """
        datatypes: dict[str, UDSDataTypeDict] = {
            'value': self._value.to_dict(),
            'confidence': self._confidence.to_dict()
        }

        if self._annotators is not None:
            # return type needs to match PropertyMetadataDict
            result: PropertyMetadataDict = {'annotators': self._annotators}

            # cast datatypes to the appropriate type for PropertyMetadataDict
            result.update(
                cast(PropertyMetadataDict, datatypes)
            )

            return result

        else:
            return cast(PropertyMetadataDict, datatypes)


class UDSAnnotationMetadata:
    """The metadata for UDS properties by subspace.

    Parameters
    ----------
    metadata
        A mapping from subspaces to properties to datatypes and
        possibly annotators.
    """

    def __init__(
        self, metadata: dict[UDSSubspace, dict[str, UDSPropertyMetadata]]
    ):
        self._metadata = metadata

    def __getitem__(
        self,
        k: UDSSubspace | tuple[UDSSubspace, str]
    ) -> dict[str, UDSPropertyMetadata] | UDSPropertyMetadata:
        """Get metadata by subspace or (subspace, property) tuple.

        Parameters
        ----------
        k : UDSSubspace | tuple[UDSSubspace, str]
            Either a subspace name or a (subspace, property) tuple.

        Returns
        -------
        dict[str, UDSPropertyMetadata] | UDSPropertyMetadata
            Property dict for subspace or specific property metadata.

        Raises
        ------
        TypeError
            If key is not a string or 2-tuple.
        KeyError
            If subspace or property not found.
        """
        if isinstance(k, str):
            return self._metadata[k]

        elif isinstance(k, tuple) and len(k) == 2:
            # for tuple access like metadata[subspace, property]
            subspace, prop = k

            return self._metadata[subspace][prop]

        else:
            raise TypeError("Key must be a string or 2-tuple")

    def __eq__(self, other: object) -> bool:
        """Check equality by comparing all subspaces and properties.

        Parameters
        ----------
        other : object
            Object to compare with.

        Returns
        -------
        bool
            True if all subspaces, properties, and metadata match.
        """
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

    def __add__(
        self,
        other: 'UDSAnnotationMetadata'
    ) -> 'UDSAnnotationMetadata':
        """Merge two metadata objects, combining annotators for shared properties.

        Parameters
        ----------
        other : UDSAnnotationMetadata
            Metadata to merge with this one.

        Returns
        -------
        UDSAnnotationMetadata
            New metadata with merged properties and annotators.
        """
        new_metadata = defaultdict(dict, self.metadata)

        for subspace, propdict in other.metadata.items():
            for prop, md in propdict.items():
                if prop in new_metadata[subspace]:
                    new_metadata[subspace][prop] += md
                else:
                    new_metadata[subspace][prop] = md

        return UDSAnnotationMetadata(new_metadata)

    @property
    def metadata(self) -> dict[UDSSubspace, dict[str, UDSPropertyMetadata]]:
        """The underlying metadata dictionary.

        Returns
        -------
        dict[UDSSubspace, dict[str, UDSPropertyMetadata]]
            Mapping from subspaces to properties to metadata.
        """
        return self._metadata

    @property
    def subspaces(self) -> set[UDSSubspace]:
        """Set of all subspace names.

        Returns
        -------
        set[UDSSubspace]
            The subspace identifiers.
        """
        return set(self._metadata.keys())

    def properties(self, subspace: UDSSubspace | None = None) -> set[str]:
        """Return the properties in a subspace.

        Parameters
        ----------
        subspace
            The subspace to get the properties of.
        """
        if subspace is None:
            return {prop for propdict in self._metadata.values()
                    for prop in propdict}

        else:
            return set(self._metadata[subspace])

    def annotators(
        self, subspace: UDSSubspace | None = None, prop: str | None = None
    ) -> set[str] | None:
        """Get annotator IDs for a subspace and/or property.

        Parameters
        ----------
        subspace : UDSSubspace | None, optional
            Subspace to filter by. If None, gets all annotators.
        prop : str | None, optional
            Property to filter by. Requires subspace if specified.

        Returns
        -------
        set[str] | None
            Union of annotator IDs, or None if no annotators found.

        Raises
        ------
        ValueError
            If prop is specified without subspace.
        """
        if subspace is None and prop is not None:
            errmsg = 'subspace must be specified if prop is specified'
            raise ValueError(errmsg)

        if subspace is None:
            annotators: list[set[str]] = [
                md.annotators
                for propdict in self._metadata.values()
                for md in propdict.values()
                if md.annotators is not None
            ]

        elif prop is None:
            annotators = [
                md.annotators
                for md in self._metadata[subspace].values()
                if md.annotators is not None
            ]

        elif self._metadata[subspace][prop].annotators is None:
            annotators = []

        else:
            ann_set = self._metadata[subspace][prop].annotators
            annotators = [ann_set] if ann_set is not None else []

        if not annotators:
            return None

        else:
            return {ann for part in annotators for ann in part}

    def has_annotators(
        self, subspace: UDSSubspace | None = None, prop: str | None = None
    ) -> bool:
        """Check if annotators exist for a subspace and/or property.

        Parameters
        ----------
        subspace : UDSSubspace | None, optional
            Subspace to check.
        prop : str | None, optional
            Property to check.

        Returns
        -------
        bool
            True if any annotators exist.
        """
        return bool(self.annotators(subspace, prop))

    @classmethod
    def from_dict(
        cls, metadata: AnnotationMetadataDict
    ) -> 'UDSAnnotationMetadata':
        """Build from nested dictionary structure.

        Parameters
        ----------
        metadata : AnnotationMetadataDict
            Nested dict mapping subspaces to properties to metadata dicts.

        Returns
        -------
        UDSAnnotationMetadata
            The constructed metadata object.
        """
        return cls({
            cast(UDSSubspace, subspace): {
                prop: UDSPropertyMetadata.from_dict(md)
                for prop, md
                in propdict.items()
            }
            for subspace, propdict in metadata.items()
        })

    def to_dict(self) -> AnnotationMetadataDict:
        """Convert to nested dictionary structure.

        Returns
        -------
        AnnotationMetadataDict
            Nested dict representation.
        """
        return {
            subspace: {
                prop: md.to_dict()
                for prop, md in propdict.items()
            }
            for subspace, propdict in self._metadata.items()
        }

class UDSCorpusMetadata:
    """The metadata for UDS properties by subspace.

    This is a thin wrapper around a pair of ``UDSAnnotationMetadata``
    objects: one for sentence annotations and one for document
    annotations.

    Parameters
    ----------
    sentence_metadata
        The metadata for sentence annotations.
    document_metadata
        The metadata for document_annotations.
    """

    def __init__(
        self,
        sentence_metadata: UDSAnnotationMetadata | None = None,
        document_metadata: UDSAnnotationMetadata | None = None
    ) -> None:
        self._sentence_metadata = (
            sentence_metadata if sentence_metadata is not None
            else UDSAnnotationMetadata({})
        )
        self._document_metadata = (
            document_metadata if document_metadata is not None
            else UDSAnnotationMetadata({})
        )

    @classmethod
    def from_dict(
        cls,
        metadata: dict[
            Literal['sentence_metadata', 'document_metadata'],
            AnnotationMetadataDict
        ]
    ) -> 'UDSCorpusMetadata':
        """Build from dictionary with sentence and document metadata.

        Parameters
        ----------
        metadata : dict[
            Literal['sentence_metadata', 'document_metadata'],
            AnnotationMetadataDict
        ]
            Dict with 'sentence_metadata' and 'document_metadata' keys.

        Returns
        -------
        UDSCorpusMetadata
            The constructed corpus metadata.
        """
        return cls(
            UDSAnnotationMetadata.from_dict(
                metadata['sentence_metadata']
            ),
            UDSAnnotationMetadata.from_dict(
                metadata['document_metadata']
            )
        )

    def to_dict(self) -> dict[
        Literal['sentence_metadata', 'document_metadata'],
        AnnotationMetadataDict
    ]:
        """Convert to dictionary with sentence and document metadata.

        Returns
        -------
        dict[Literal['sentence_metadata', 'document_metadata'], AnnotationMetadataDict]
            Dict with 'sentence_metadata' and 'document_metadata' keys.
        """
        return {
            'sentence_metadata': self._sentence_metadata.to_dict(),
            'document_metadata': self._document_metadata.to_dict()
        }

    def __add__(self, other: 'UDSCorpusMetadata') -> 'UDSCorpusMetadata':
        """Merge two corpus metadata objects.

        Parameters
        ----------
        other : UDSCorpusMetadata
            Metadata to merge.

        Returns
        -------
        UDSCorpusMetadata
            New metadata with merged sentence and document metadata.
        """
        new_sentence_metadata = self._sentence_metadata + other._sentence_metadata
        new_document_metadata = self._document_metadata + other._document_metadata

        return self.__class__(new_sentence_metadata, new_document_metadata)

    def add_sentence_metadata(self, metadata: UDSAnnotationMetadata) -> None:
        """Add sentence annotation metadata.

        Parameters
        ----------
        metadata : UDSAnnotationMetadata
            Metadata to merge with existing sentence metadata.
        """
        self._sentence_metadata += metadata

    def add_document_metadata(self, metadata: UDSAnnotationMetadata) -> None:
        """Add document annotation metadata.

        Parameters
        ----------
        metadata : UDSAnnotationMetadata
            Metadata to merge with existing document metadata.
        """
        self._document_metadata += metadata

    @property
    def sentence_metadata(self) -> UDSAnnotationMetadata:
        """The sentence-level annotation metadata.

        Returns
        -------
        UDSAnnotationMetadata
            Metadata for sentence annotations.
        """
        return self._sentence_metadata

    @property
    def document_metadata(self) -> UDSAnnotationMetadata:
        """The document-level annotation metadata.

        Returns
        -------
        UDSAnnotationMetadata
            Metadata for document annotations.
        """
        return self._document_metadata

    @property
    def sentence_subspaces(self) -> set[UDSSubspace]:
        """Set of sentence-level subspaces.

        Returns
        -------
        set[UDSSubspace]
            Sentence subspace identifiers.
        """
        return self._sentence_metadata.subspaces

    @property
    def document_subspaces(self) -> set[UDSSubspace]:
        """Set of document-level subspaces.

        Returns
        -------
        set[UDSSubspace]
            Document subspace identifiers.
        """
        return self._document_metadata.subspaces

    def sentence_properties(self, subspace: UDSSubspace | None = None) -> set[str]:
        """Return the properties in a sentence subspace.

        Parameters
        ----------
        subspace
            The subspace to get the properties of.
        """
        return self._sentence_metadata.properties(subspace)

    def document_properties(self, subspace: UDSSubspace | None = None) -> set[str]:
        """Return the properties in a document subspace.

        Parameters
        ----------
        subspace
            The subspace to get the properties of.
        """
        return self._document_metadata.properties(subspace)

    def sentence_annotators(
        self, subspace: UDSSubspace | None = None, prop: str | None = None
    ) -> set[str] | None:
        """Return the annotators for a property in a sentence subspace.

        Parameters
        ----------
        subspace
            The subspace to get the annotators of.
        prop
            The property to get the annotators of.
        """
        return self._sentence_metadata.annotators(subspace, prop)

    def document_annotators(
        self, subspace: UDSSubspace | None = None, prop: str | None = None
    ) -> set[str] | None:
        """Return the annotators for a property in a document subspace.

        Parameters
        ----------
        subspace
            The subspace to get the annotators of.
        prop
            The property to get the annotators of.
        """
        return self._document_metadata.annotators(subspace, prop)

    def has_sentence_annotators(
        self, subspace: UDSSubspace | None = None, prop: str | None = None
    ) -> bool:
        """Check if sentence-level annotators exist.

        Parameters
        ----------
        subspace : UDSSubspace | None, optional
            Subspace to check.
        prop : str | None, optional
            Property to check.

        Returns
        -------
        bool
            True if annotators exist.
        """
        return self._sentence_metadata.has_annotators(subspace, prop)

    def has_document_annotators(
        self, subspace: UDSSubspace | None = None, prop: str | None = None
    ) -> bool:
        """Check if document-level annotators exist.

        Parameters
        ----------
        subspace : UDSSubspace | None, optional
            Subspace to check.
        prop : str | None, optional
            Property to check.

        Returns
        -------
        bool
            True if annotators exist.
        """
        return self._document_metadata.has_annotators(subspace, prop)
