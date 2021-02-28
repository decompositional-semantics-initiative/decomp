This directory contains the tests for the [Decomp
toolkit](https://github.com/decompositional-semantics-initiative/decomp). Theses
tests use the [`pytest` framework](https://docs.pytest.org/).

# Installation

To run the tests in this directory, ensure that both the toolkit and
`pytest` are installed.

```bash
pip install --user pytest==6.0.* git+git://github.com/decompositional-semantics-initiative/decomp.git
```

# Running the test suite

The entire test suite can be run from the root directory of the
toolkit installation using:

```bash
pytest
```
