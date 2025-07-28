"""Extraction engine for PredPatt predicate-argument structures.

This module contains the main extraction engine and supporting components
for extracting predicate-argument structures from Universal Dependencies parses.
"""

from __future__ import annotations

from .engine import PredPattEngine


__all__ = ["PredPattEngine"]
