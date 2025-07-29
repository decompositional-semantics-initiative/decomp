"""Common type definitions for PredPatt modules.

This module contains shared protocols and type variables used across
the PredPatt system to avoid circular imports and ensure consistency.
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
UDSchema = type['DependencyRelationsV1'] | type['DependencyRelationsV2']
