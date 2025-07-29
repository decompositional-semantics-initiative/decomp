"""Type definitions for UDS annotation system based on UDS dataset structure.

This module provides precise Literal types for all UDS subspaces, properties,
and annotation value structures to ensure type safety across the codebase.
"""

from typing import Literal, TypeAlias, TypedDict

# primitive types for annotation values
PrimitiveType: TypeAlias = str | int | bool | float

# domain types - only 4 possible values
DomainType: TypeAlias = Literal['syntax', 'semantics', 'document', 'interface']

# node types vary by domain
NodeType: TypeAlias = Literal['token', 'predicate', 'argument', 'root']

# edge types vary by domain  
EdgeType: TypeAlias = Literal['head', 'nonhead', 'dependency']

# all possible UDS subspaces (complete enumeration)
UDSSubspace: TypeAlias = Literal[
    'factuality',       # sentence-level node: factual predicate judgments
    'genericity',       # sentence-level node: generic vs episodic distinctions  
    'time',             # sentence + document: temporal relations and duration
    'wordsense',        # sentence-level node: entity type supersenses
    'event_structure',  # sentence + document: aspectual and mereological properties
    'protoroles'        # sentence-level edge: semantic proto-role properties
]

# factuality subspace
FactualityProperty: TypeAlias = Literal['factual']

# genericity subspace  
GenericityProperty: TypeAlias = Literal[
    'arg-particular', 'arg-kind', 'arg-abstract',
    'pred-particular', 'pred-dynamic', 'pred-hypothetical'
]

# time subspace - normalized time properties (11 duration categories)
TimePropertyNormalized: TypeAlias = Literal[
    'dur-hours', 'dur-instant', 'dur-forever', 'dur-weeks', 'dur-days',
    'dur-months', 'dur-years', 'dur-centuries', 'dur-seconds', 
    'dur-minutes', 'dur-decades'
]

# raw time properties
TimePropertyRaw: TypeAlias = Literal['duration']

# document-level time properties (only in raw format)
TimePropertyDocument: TypeAlias = Literal[
    'rel-start1', 'rel-start2', 'rel-end1', 'rel-end2'
]

# wordsense subspace (25 supersense categories)
WordsenseProperty: TypeAlias = Literal[
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
EventStructurePropertyNormalized: TypeAlias = Literal[
    'distributive', 'dynamic', 'natural_parts', 'part_similarity', 'telic',
    # duration bounds for average part duration (10 time units × 2 bounds)
    'avg_part_duration_lbound-centuries', 'avg_part_duration_ubound-centuries',
    'avg_part_duration_lbound-days', 'avg_part_duration_ubound-days',
    'avg_part_duration_lbound-decades', 'avg_part_duration_ubound-decades',
    'avg_part_duration_lbound-forever', 'avg_part_duration_ubound-forever',
    'avg_part_duration_lbound-fractions_of_a_second', 'avg_part_duration_ubound-fractions_of_a_second',
    'avg_part_duration_lbound-hours', 'avg_part_duration_ubound-hours',
    'avg_part_duration_lbound-instant', 'avg_part_duration_ubound-instant',
    'avg_part_duration_lbound-minutes', 'avg_part_duration_ubound-minutes',
    'avg_part_duration_lbound-months', 'avg_part_duration_ubound-months',
    'avg_part_duration_lbound-seconds', 'avg_part_duration_ubound-seconds',
    'avg_part_duration_lbound-weeks', 'avg_part_duration_ubound-weeks',
    'avg_part_duration_lbound-years', 'avg_part_duration_ubound-years',
    # duration bounds for situation duration (10 time units × 2 bounds)  
    'situation_duration_lbound-centuries', 'situation_duration_ubound-centuries',
    'situation_duration_lbound-days', 'situation_duration_ubound-days',
    'situation_duration_lbound-decades', 'situation_duration_ubound-decades',
    'situation_duration_lbound-forever', 'situation_duration_ubound-forever',
    'situation_duration_lbound-fractions_of_a_second', 'situation_duration_ubound-fractions_of_a_second',
    'situation_duration_lbound-hours', 'situation_duration_ubound-hours',
    'situation_duration_lbound-instant', 'situation_duration_ubound-instant',
    'situation_duration_lbound-minutes', 'situation_duration_ubound-minutes',
    'situation_duration_lbound-months', 'situation_duration_ubound-months',
    'situation_duration_lbound-seconds', 'situation_duration_ubound-seconds',
    'situation_duration_lbound-weeks', 'situation_duration_ubound-weeks',
    'situation_duration_lbound-years', 'situation_duration_ubound-years'
]

# raw event structure (8 core properties)
EventStructurePropertyRaw: TypeAlias = Literal[
    'dynamic', 'natural_parts', 'part_similarity', 'telic',
    'avg_part_duration_lbound', 'avg_part_duration_ubound',
    'situation_duration_lbound', 'situation_duration_ubound'
]

# document-level event structure
EventStructurePropertyDocument: TypeAlias = Literal[
    'pred1_contains_pred2', 'pred2_contains_pred1'
]

# protoroles subspace (18 proto-role properties)
ProtorolesProperty: TypeAlias = Literal[
    'was_used', 'purpose', 'partitive', 'location', 'instigation',
    'existed_after', 'time', 'awareness', 'change_of_location', 'manner',
    'sentient', 'was_for_benefit', 'change_of_state_continuous', 'existed_during',
    'change_of_possession', 'existed_before', 'volition', 'change_of_state'
]

# basic annotation value (normalized format)
NormalizedAnnotationValue: TypeAlias = dict[Literal['value', 'confidence'], PrimitiveType]

# raw annotation value (multi-annotator format)  
RawAnnotationValue: TypeAlias = dict[
    Literal['value', 'confidence'], 
    dict[str, PrimitiveType]  # annotator_id -> value
]

# annotator-indexed value (for by-annotator access)
class AnnotatorValue(TypedDict):
    confidence: PrimitiveType
    value: PrimitiveType

# properties within a subspace
NormalizedSubspaceProperties: TypeAlias = dict[str, NormalizedAnnotationValue]
RawSubspaceProperties: TypeAlias = dict[str, RawAnnotationValue]

# complete subspace data  
NormalizedSubspaceData: TypeAlias = dict[UDSSubspace, NormalizedSubspaceProperties]
RawSubspaceData: TypeAlias = dict[UDSSubspace, RawSubspaceProperties]

# basic graph attributes (no UDS annotations)
BasicNodeAttrs: TypeAlias = dict[str, str | int | bool]  # domain, type, position, form, etc.
BasicEdgeAttrs: TypeAlias = dict[str, str | int | bool]  # domain, type, deprel, etc.

# basic graph element attributes by domain
SyntaxNodeAttrs: TypeAlias = dict[str, str | int | bool]  # position, domain, type, form, lemma, upos, xpos
SemanticsNodeAttrs: TypeAlias = dict[str, str | int | bool]  # domain, type, frompredpatt  
DocumentNodeAttrs: TypeAlias = dict[str, str | int | bool | dict[str, str]]  # includes semantics pointer

# complete attributes (basic + UDS annotations)
NodeAttributes: TypeAlias = (SyntaxNodeAttrs | SemanticsNodeAttrs | DocumentNodeAttrs | 
                           NormalizedSubspaceData | RawSubspaceData)

EdgeAttributes: TypeAlias = (dict[str, str | int | bool] |  # basic edge attrs
                           NormalizedSubspaceData | RawSubspaceData)

# networkX adjacency format (for to_dict() methods)
NetworkXNodeData: TypeAlias = dict[str, str | int | bool | dict[str, str]]
NetworkXGraphData: TypeAlias = dict[str, dict[str, NetworkXNodeData]]

# dash-specific type aliases for visualization
DashChecklistOption: TypeAlias = dict[Literal['label', 'value'], str]
DashMarkerStyle: TypeAlias = dict[str, str | int | float]

# visualization data types  
PlotCoordinate: TypeAlias = float | None
PlotDataSeries: TypeAlias = list[PlotCoordinate]
SemanticNodeData: TypeAlias = dict[Literal['x', 'y', 'text', 'hovertext'], PlotDataSeries]

# edge key type for graph operations
EdgeKey: TypeAlias = tuple[str, ...]

# attributeValue type for visualization compatibility
AttributeValue: TypeAlias = str | int | bool | float | dict[str, str] | dict[str, dict[str, dict[str, str | int | bool | float]]]