decomp.semantics.predpatt
=========================

PredPatt semantic role labeling module for extracting predicate-argument structures from Universal Dependencies parses.

This module provides functionality for identifying verbal predicates and their arguments through linguistic rules applied to dependency parse trees. The extracted semantic structures can be integrated with the Universal Decompositional Semantics (UDS) framework for further annotation.

Overview
--------

The PredPatt system consists of several key components:

- **Core data structures** (:mod:`~decomp.semantics.predpatt.core`) for representing tokens, predicates, and arguments
- **Parsing utilities** (:mod:`~decomp.semantics.predpatt.parsing`) for loading and processing Universal Dependencies parses
- **Extraction engine** (:mod:`~decomp.semantics.predpatt.extraction`) that orchestrates the rule application process
- **Linguistic rules** (:mod:`~decomp.semantics.predpatt.rules`) for identifying predicates and their arguments
- **Filtering system** (:mod:`~decomp.semantics.predpatt.filters`) for refining extractions based on linguistic criteria
- **Integration utilities** (:mod:`~decomp.semantics.predpatt.corpus`, :mod:`~decomp.semantics.predpatt.graph`) for working with UDS corpora
- **Support utilities** (:mod:`~decomp.semantics.predpatt.utils`) for visualization and debugging

Usage Example
-------------

.. tab-set::

    .. tab-item:: Basic Usage

        .. code-block:: python

            from decomp.semantics.predpatt import PredPatt, load_conllu
            
            # Load a dependency parse
            sentences = load_conllu('example.conllu')
            
            # Extract predicates and arguments
            pp = PredPatt(sentences[0])
            
            # Access extracted predicates
            for predicate in pp.predicates:
                print(f"Predicate: {predicate}")
                for arg in predicate.arguments:
                    print(f"  Argument: {arg}")

    .. tab-item:: With Options

        .. code-block:: python

            from decomp.semantics.predpatt import PredPatt, PredPattOpts, load_conllu
            
            # Configure extraction options
            opts = PredPattOpts(
                resolve_relcl=True,      # Resolve relative clauses
                resolve_conj=True,       # Resolve conjunctions
                cut=True,                # Apply cutting rules
                simple=False             # Include all predicates
            )
            
            # Load and process
            sentences = load_conllu('example.conllu')
            pp = PredPatt(sentences[0], opts=opts)

    .. tab-item:: Integration with UDS

        .. code-block:: python

            from decomp.semantics.predpatt import PredPattCorpus
            from decomp.semantics.uds import UDSCorpus
            
            # Load UDS corpus
            uds = UDSCorpus()
            
            # Create PredPatt corpus
            predpatt_corpus = PredPattCorpus.from_ud(
                uds.syntax_graphs()
            )
            
            # Access predicate-argument structures
            for graph_id, predpatt in predpatt_corpus:
                for pred in predpatt.predicates:
                    print(f"{pred.root.text}: {[arg.phrase() for arg in pred.arguments]}")

.. note::

   The code examples above include **copy buttons** for easy copying. The modern documentation
   also features:
   
   - Enhanced type hint rendering with :py:class:`~typing.Union` and modern Python 3.12+ syntax
   - Cross-references to Python standard library (e.g., :py:class:`list`, :py:class:`dict`)
   - Links to dependency projects via intersphinx (e.g., :py:class:`networkx.DiGraph`)

.. automodule:: decomp.semantics.predpatt
    :members:
    :undoc-members:
    :show-inheritance:

Submodules
----------

.. toctree::
   :maxdepth: 2

   decomp.semantics.predpatt.core
   decomp.semantics.predpatt.extraction
   decomp.semantics.predpatt.parsing
   decomp.semantics.predpatt.rules
   decomp.semantics.predpatt.filters
   decomp.semantics.predpatt.corpus
   decomp.semantics.predpatt.graph
   decomp.semantics.predpatt.utils
   decomp.semantics.predpatt.typing
