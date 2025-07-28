"""
Differential testing module for PredPatt.

This module contains tests that compare the modernized PredPatt implementation
against the original external PredPatt library to ensure byte-for-byte identical output.

NOTE: These tests require the external 'predpatt' package to be installed.
They will be automatically skipped if the package is not available.

To run these tests:
    pip install predpatt
    pytest tests/predpatt/differential/
"""