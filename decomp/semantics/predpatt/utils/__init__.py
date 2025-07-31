"""Utility functions for PredPatt processing and visualization.

This module provides utility functions for linearizing PredPatt structures
into flat representations, visualizing dependency trees, and formatting
output for display.

Functions
---------
linearize
    Convert PredPatt structures to linearized string format.
linearize_pprint
    Pretty-print linearized PredPatt structures.
construct_pred_from_flat
    Reconstruct predicate from linearized format.
linear_to_string
    Convert linearized structure to string representation.

Classes
-------
LinearizedPPOpts
    Options for controlling linearization output format.
"""

from .linearization import (
    LinearizedPPOpts,
    construct_pred_from_flat,
    linear_to_string,
    linearize,
)
from .linearization import (
    pprint as linearize_pprint,
)


__all__ = [
    'LinearizedPPOpts',
    'construct_pred_from_flat',
    'linear_to_string',
    'linearize',
    'linearize_pprint',
]
