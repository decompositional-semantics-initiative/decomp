"""Type definitions for the Universal Decompositional Semantics (UDS) annotation system.

This module provides comprehensive type definitions that mirror the structure of UDS
datasets, ensuring type safety throughout the decomp framework. The types are organized
hierarchically from primitive values through complex annotation structures.

Type Organization
-----------------
The module defines types in several categories:

1. **Primitive and Domain Types**: Basic building blocks like :data:`PrimitiveType`
   and domain classifications (:data:`DomainType`, :data:`NodeType`, :data:`EdgeType`).

2. **UDS Subspaces**: The six semantic annotation subspaces are enumerated in
   :data:`UDSSubspace`, with corresponding property types for each:

   - Factuality (:data:`FactualityProperty`)
   - Genericity (:data:`GenericityProperty`)
   - Time (:data:`TimePropertyNormalized`, :data:`TimePropertyRaw`, :data:`TimePropertyDocument`)
   - Wordsense (:data:`WordsenseProperty`)
   - Event Structure (:data:`EventStructurePropertyNormalized`, :data:`EventStructurePropertyRaw`)
   - Protoroles (:data:`ProtorolesProperty`)

3. **Annotation Values**: Types for storing annotation data in both normalized
   (:data:`NormalizedAnnotationValue`) and raw multi-annotator formats
   (:data:`RawAnnotationValue`).

4. **Graph Attributes**: Types for node and edge attributes at different levels,
   from basic attributes (:data:`BasicNodeAttrs`) to complete attributes with
   UDS annotations (:data:`NodeAttributes`, :data:`EdgeAttributes`).

5. **Visualization Types**: Specialized types for graph visualization with Plotly/Dash
   (:data:`PlotCoordinate`, :data:`SemanticNodeData`, :data:`DashChecklistOption`).

Classes
-------
AnnotatorValue
    TypedDict for individual annotator responses with confidence scores.

Notes
-----
All Literal types in this module correspond exactly to the property names used in
the UDS dataset JSON format, ensuring compatibility with data loading and serialization.
The type system supports both sentence-level and document-level annotations across
all UDS subspaces.
"""

from typing import Literal, TypedDict


# primitive types for annotation values
type PrimitiveType = str | int | bool | float

# domain types - only 4 possible values
type DomainType = Literal['syntax', 'semantics', 'document', 'interface']

# node types vary by domain
type NodeType = Literal['token', 'predicate', 'argument', 'root']

# edge types vary by domain
type EdgeType = Literal['head', 'nonhead', 'dependency']

# all possible UDS subspaces (complete enumeration)
type UDSSubspace = Literal[
    'factuality',       # sentence-level node: factual predicate judgments
    'genericity',       # sentence-level node: generic vs episodic distinctions
    'time',             # sentence + document: temporal relations and duration
    'wordsense',        # sentence-level node: entity type supersenses
    'event_structure',  # sentence + document: aspectual and mereological properties
    'protoroles'        # sentence-level edge: semantic proto-role properties
]

# factuality subspace
type FactualityProperty = Literal['factual']

# genericity subspace
type GenericityProperty = Literal[
    'arg-particular', 'arg-kind', 'arg-abstract',
    'pred-particular', 'pred-dynamic', 'pred-hypothetical'
]

# time subspace - normalized time properties (11 duration categories)
type TimePropertyNormalized = Literal[
    'dur-hours', 'dur-instant', 'dur-forever', 'dur-weeks', 'dur-days',
    'dur-months', 'dur-years', 'dur-centuries', 'dur-seconds',
    'dur-minutes', 'dur-decades'
]

# raw time properties
type TimePropertyRaw = Literal['duration']

# document-level time properties (only in raw format)
type TimePropertyDocument = Literal[
    'rel-start1', 'rel-start2', 'rel-end1', 'rel-end2'
]

# wordsense subspace (25 supersense categories)
type WordsenseProperty = Literal[
    'supersense-noun.shape', 'supersense-noun.process', 'supersense-noun.relation',
    'supersense-noun.communication', 'supersense-noun.time', 'supersense-noun.plant',
    'supersense-noun.phenomenon', 'supersense-noun.animal', 'supersense-noun.state',
    'supersense-noun.substance', 'supersense-noun.person', 'supersense-noun.possession',
    'supersense-noun.Tops', 'supersense-noun.object', 'supersense-noun.event',
    'supersense-noun.artifact', 'supersense-noun.act', 'supersense-noun.body',
    'supersense-noun.attribute', 'supersense-noun.quantity', 'supersense-noun.motive',
    'supersense-noun.location', 'supersense-noun.cognition', 'supersense-noun.group',
    'supersense-noun.food', 'supersense-noun.feeling'
]

# event structure subspace - normalized event structure (50+ duration properties)
type EventStructurePropertyNormalized = Literal[
    'distributive', 'dynamic', 'natural_parts', 'part_similarity', 'telic',
    # duration bounds for average part duration (10 time units x 2 bounds)
    'avg_part_duration_lbound-centuries', 'avg_part_duration_ubound-centuries',
    'avg_part_duration_lbound-days', 'avg_part_duration_ubound-days',
    'avg_part_duration_lbound-decades', 'avg_part_duration_ubound-decades',
    'avg_part_duration_lbound-forever', 'avg_part_duration_ubound-forever',
    'avg_part_duration_lbound-fractions_of_a_second',
    'avg_part_duration_ubound-fractions_of_a_second',
    'avg_part_duration_lbound-hours', 'avg_part_duration_ubound-hours',
    'avg_part_duration_lbound-instant', 'avg_part_duration_ubound-instant',
    'avg_part_duration_lbound-minutes', 'avg_part_duration_ubound-minutes',
    'avg_part_duration_lbound-months', 'avg_part_duration_ubound-months',
    'avg_part_duration_lbound-seconds', 'avg_part_duration_ubound-seconds',
    'avg_part_duration_lbound-weeks', 'avg_part_duration_ubound-weeks',
    'avg_part_duration_lbound-years', 'avg_part_duration_ubound-years',
    # duration bounds for situation duration (10 time units x 2 bounds)
    'situation_duration_lbound-centuries', 'situation_duration_ubound-centuries',
    'situation_duration_lbound-days', 'situation_duration_ubound-days',
    'situation_duration_lbound-decades', 'situation_duration_ubound-decades',
    'situation_duration_lbound-forever', 'situation_duration_ubound-forever',
    'situation_duration_lbound-fractions_of_a_second',
    'situation_duration_ubound-fractions_of_a_second',
    'situation_duration_lbound-hours', 'situation_duration_ubound-hours',
    'situation_duration_lbound-instant', 'situation_duration_ubound-instant',
    'situation_duration_lbound-minutes', 'situation_duration_ubound-minutes',
    'situation_duration_lbound-months', 'situation_duration_ubound-months',
    'situation_duration_lbound-seconds', 'situation_duration_ubound-seconds',
    'situation_duration_lbound-weeks', 'situation_duration_ubound-weeks',
    'situation_duration_lbound-years', 'situation_duration_ubound-years'
]

# raw event structure (8 core properties)
type EventStructurePropertyRaw = Literal[
    'dynamic', 'natural_parts', 'part_similarity', 'telic',
    'avg_part_duration_lbound', 'avg_part_duration_ubound',
    'situation_duration_lbound', 'situation_duration_ubound'
]

# document-level event structure
type EventStructurePropertyDocument = Literal[
    'pred1_contains_pred2', 'pred2_contains_pred1'
]

# protoroles subspace (18 proto-role properties)
type ProtorolesProperty = Literal[
    'was_used', 'purpose', 'partitive', 'location', 'instigation',
    'existed_after', 'time', 'awareness', 'change_of_location', 'manner',
    'sentient', 'was_for_benefit', 'change_of_state_continuous', 'existed_during',
    'change_of_possession', 'existed_before', 'volition', 'change_of_state'
]

# basic annotation value (normalized format)
type NormalizedAnnotationValue = dict[Literal['value', 'confidence'], PrimitiveType]

# raw annotation value (multi-annotator format)
type RawAnnotationValue = dict[
    Literal['value', 'confidence'],
    dict[str, PrimitiveType]  # annotator_id -> value
]

# annotator-indexed value (for by-annotator access)
class AnnotatorValue(TypedDict):
    """Individual annotator response with confidence score."""

    confidence: PrimitiveType
    value: PrimitiveType

# properties within a subspace
type NormalizedSubspaceProperties = dict[str, NormalizedAnnotationValue]
type RawSubspaceProperties = dict[str, RawAnnotationValue]

# complete subspace data
type NormalizedSubspaceData = dict[UDSSubspace, NormalizedSubspaceProperties]
type RawSubspaceData = dict[UDSSubspace, RawSubspaceProperties]

# basic graph attributes (no UDS annotations)
type BasicNodeAttrs = dict[str, str | int | bool]  # domain, type, position, form, etc.
type BasicEdgeAttrs = dict[str, str | int | bool]  # domain, type, deprel, etc.

# basic graph element attributes by domain
# position, domain, type, form, lemma, upos, xpos
type SyntaxNodeAttrs = dict[str, str | int | bool]
type SemanticsNodeAttrs = dict[str, str | int | bool]  # domain, type, frompredpatt
type DocumentNodeAttrs = dict[str, str | int | bool | dict[str, str]]  # includes semantics pointer

# complete attributes (basic + UDS annotations)
type NodeAttributes = (
    SyntaxNodeAttrs | SemanticsNodeAttrs | DocumentNodeAttrs |
    NormalizedSubspaceData | RawSubspaceData
)

type EdgeAttributes = (
    dict[str, str | int | bool] |  # basic edge attrs
    NormalizedSubspaceData | RawSubspaceData
)

# networkX adjacency format (for to_dict() methods)
type NetworkXNodeData = dict[str, str | int | bool | dict[str, str]]
type NetworkXGraphData = dict[str, dict[str, NetworkXNodeData]]

# dash-specific type aliases for visualization
type DashChecklistOption = dict[Literal['label', 'value'], str]
type DashMarkerStyle = dict[str, str | int | float]

# visualization data types
type PlotCoordinate = float | None
type PlotDataSeries = list[PlotCoordinate]
type SemanticNodeData = dict[Literal['x', 'y', 'text', 'hovertext'], PlotDataSeries]

# edge key type for graph operations
type EdgeKey = tuple[str, ...]

# attributeValue type for visualization compatibility
type AttributeValue = (
    str | int | bool | float | dict[str, str] |
    dict[str, dict[str, dict[str, str | int | bool | float]]]
)
