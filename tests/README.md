This directory contains the tests for the [Decomp
toolkit](https://github.com/decompositional-semantics-initiative/decomp). Theses
tests use the [`pytest` framework](https://docs.pytest.org/).

# Installation

To run the tests in this directory, install the toolkit with development dependencies:

```bash
pip install -e ".[dev]"
```

This will install the toolkit in editable mode along with all testing dependencies including pytest.

# Running the test suite

The entire test suite can be run from the root directory of the
toolkit installation using:

```bash
pytest
```
