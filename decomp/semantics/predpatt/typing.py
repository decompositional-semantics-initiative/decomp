"""Type definitions and protocols for the PredPatt semantic extraction system.

This module provides shared type definitions to support static type checking
across the PredPatt framework. It defines protocols and type variables that
are used throughout the system to avoid circular imports while maintaining
type safety.

Classes
-------
HasPosition
    Protocol defining objects with a position attribute, used for tokens,
    predicates, and arguments that have positions in text.

Type Variables
--------------
T
    Type variable bounded by HasPosition protocol for generic functions
    that operate on positioned objects.

Type Aliases
------------
UDSchema
    Type alias for Universal Dependencies schema classes, supporting both
    v1 and v2 dependency relation definitions.
"""

from typing import TYPE_CHECKING, Protocol, TypeVar


if TYPE_CHECKING:
    from .utils.ud_schema import DependencyRelationsV1, DependencyRelationsV2


class HasPosition(Protocol):
    """Protocol for objects that have a position attribute."""

    position: int


# type variable for objects with position
T = TypeVar('T', bound=HasPosition)

# type alias for UD schema modules
type UDSchema = type['DependencyRelationsV1'] | type['DependencyRelationsV2']
