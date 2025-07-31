.. _install:

============
Installation
============

.. tab-set::

    .. tab-item:: Docker

        The most painless way to get started quickly is to use the included
        Dockerfile based on jupyter/datascience-notebook with Python 3.12.
        
        To build the image and start a Jupyter Lab server:

        .. code-block:: bash

            git clone git://github.com/decompositional-semantics-initiative/decomp.git
            cd decomp
            docker build -t decomp .
            docker run -it -p 8888:8888 decomp
           
        This will start a Jupyter Lab server accessible at http://localhost:8888
        (with authentication disabled for convenience).
        
        To start a Python interactive prompt instead:
        
        .. code-block:: bash
        
            docker run -it decomp python

    .. tab-item:: pip

        Decomp can be installed from GitHub using ``pip``:

        .. code-block:: bash

            pip install git+https://github.com/decompositional-semantics-initiative/decomp.git

        **Requirements**: Python 3.12 or higher is required.

    .. tab-item:: From Source

        To install from source, clone the repository and use ``pip``:

        .. code-block:: bash

            git clone https://github.com/decompositional-semantics-initiative/decomp.git
            cd decomp
            pip install .

        This will automatically install all dependencies specified in ``pyproject.toml``.

    .. tab-item:: Development

        For development, install the package in editable mode with development dependencies:

        .. code-block:: bash

            git clone https://github.com/decompositional-semantics-initiative/decomp.git
            cd decomp
            pip install -e ".[dev]"

        This installs:
        
        - The package in editable mode (changes to source code take effect immediately)
        - Development tools: ``pytest``, ``ruff``, ``mypy``, and ``ipython``
        - All runtime dependencies

        .. note::
           
           For running the full test suite including differential tests, you'll also need to
           install ``predpatt`` separately (due to PyPI restrictions on git dependencies):
           
           .. code-block:: bash
           
               pip install git+https://github.com/hltcoe/PredPatt.git

        To run tests:

        .. code-block:: bash

            pytest              # Run fast tests only
            pytest --runslow    # Run all tests including slow tests
