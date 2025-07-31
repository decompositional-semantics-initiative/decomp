# Differential Testing for PredPatt

This directory contains differential tests that compare the modernized PredPatt implementation against the original external PredPatt library to ensure byte-for-byte identical output.

## Requirements

These tests require the external `predpatt` package to be installed. Due to PyPI restrictions on git dependencies, this package must be installed separately:

```bash
pip install git+https://github.com/hltcoe/PredPatt.git
```

Note: The tests will fail if the package is not available, as it's required for differential testing.

## Running the Tests

To run only the differential tests:

```bash
pytest tests/predpatt/differential/
```

To run with verbose output:

```bash
pytest tests/predpatt/differential/ -v
```

## Test Files

- `test_differential.py` - Comprehensive differential testing comparing outputs across various sentences and option configurations
- `test_compare_implementations.py` - Simple comparison test for basic functionality

## Purpose

These tests serve as a safety net during development to ensure that the modernized implementation produces exactly the same output as the original PredPatt library. This is critical for maintaining compatibility and correctness.

## Note

These tests are optional and primarily intended for developers working on the PredPatt implementation. Regular users do not need to install the external predpatt package unless they want to verify compatibility.