Release Notes
=============

This page documents all releases of the Decomp toolkit, including major features, bug fixes, and breaking changes.

Version 0.3.0 (2025-07-30)
---------------------------

**PredPatt Integration and Python 3.12+ Modernization**

This release represents a significant modernization of the Decomp toolkit with full integration of PredPatt predicate-argument structure extraction functionality and comprehensive Python 3.12+ compatibility.

Key Features
~~~~~~~~~~~~

**PredPatt Integration**
   Complete integration of `PredPatt <https://github.com/hltcoe/PredPatt>`_ into ``decomp.semantics.predpatt`` module:
   
   - ``core``: Core data structures (Token, Predicate, Argument, PredPattOpts)
   - ``extraction``: Main extraction engine and orchestration
   - ``parsing``: Universal Dependencies parsing utilities
   - ``rules``: Linguistic rules for predicate and argument identification
   - ``filters``: Configurable filtering system
   - ``utils``: Visualization and debugging utilities

**Modern Python Support**
   Full Python 3.12+ compatibility with modernized codebase:
   
   - Updated type hints using union syntax (``|``) and built-in generics
   - Migration from ``setup.py`` to ``pyproject.toml`` for modern packaging
   - `ruff <https://github.com/astral-sh/ruff>`_ and `mypy <https://github.com/python/mypy>`_ integration for code quality assurance
   - Comprehensive pytest-based test suite


Usage Example
~~~~~~~~~~~~~

.. code-block:: python

   from decomp.semantics.predpatt import PredPatt, load_conllu
   
   # load dependency parses
   sentences = load_conllu('example.conllu')
   
   # extract predicates and arguments
   pp = PredPatt(sentences[0])
   
   # access extracted structures
   for predicate in pp.predicates:
       print(f"Predicate: {predicate}")
       for arg in predicate.arguments:
           print(f"  Argument: {arg}")

Technical Details
~~~~~~~~~~~~~~~~~

- **Algorithm Fidelity**: Maintains byte-for-byte identical output with standalone PredPatt (v1.0.1)
- **Testing**: Comprehensive differential testing ensures compatibility
- **Documentation**: Complete API documentation

Version 0.2.2 (2022-06-08)
---------------------------

**Maintenance Release**

Bug Fixes
~~~~~~~~~

- Fixed broken corpus load from JSON functionality
- Corrected error in raw UDS-EventStructure annotations processing

This release maintains compatibility with Universal Decompositional Semantics v2.0 dataset and provides important stability improvements.

Version 0.2.1 (2021-04-05)
---------------------------

**Python 3.9 Compatibility**

Bug Fixes
~~~~~~~~~

- Resolved compatibility issues with Python 3.9
- Updated dependencies to support newer Python versions

This release is part of the Universal Decompositional Semantics v2.0 series with improved cross-platform compatibility.

Version 0.2.0 (2021-03-19)
---------------------------

**Universal Decompositional Semantics v2.0**

This release introduces support for UDS v2.0 with significant architectural enhancements.

Major Features
~~~~~~~~~~~~~~

**Document-Level Support**
   - Document-level semantic graph structures
   - Enhanced graph representations for complex relationships
   - Support for multi-sentence semantic analysis

**Raw Annotations**
   - Access to raw annotation data alongside normalized annotations
   - Enhanced annotation provenance and metadata
   - Improved debugging and analysis capabilities

**Visualization Module**
   - New :py:mod:`decomp.vis` module for graph visualization
   - Interactive graph exploration and analysis tools
   - Enhanced debugging capabilities for semantic structures

**Advanced Metadata**
   - Annotation metadata handling and processing
   - Annotation confidence and provenance tracking

Technical Changes
~~~~~~~~~~~~~~~~~

- **API Extensions**: Expanded API surface for document-level processing
- **Graph Infrastructure**: Enhanced NetworkX and RDF graph support
- **Data Pipeline**: Improved processing pipeline for complex annotation types

Breaking Changes
~~~~~~~~~~~~~~~~

- API changes required for document-level graph support
- Some method signatures updated for enhanced functionality
- Migration guide available for updating existing code

Version 0.1.3 (2020-03-13)
---------------------------

**Stability Improvements**

Bug Fixes
~~~~~~~~~

- Fixed RDF cache clearing error preventing memory issues
- Added missing document and sentence ID attributes for improved tracking

Features
~~~~~~~~

- Enhanced corpus navigation and identification
- Improved debugging capabilities

Version 0.1.2 (2020-01-17)
---------------------------

**Corpus Construction Fixes**

Bug Fixes
~~~~~~~~~

- Fixed corpus construction error when using split parameter
- Resolved issues with train/dev/test split functionality
- Improved error handling and messaging for corpus operations

Version 0.1.1 (2019-10-19)
---------------------------

**Linguistic Accuracy Improvements**

Bug Fixes
~~~~~~~~~

- Fixed copular clause argument linking error in genericity annotations
- Improved handling of copular constructions in semantic role assignment
- Enhanced accuracy of genericity property assignments

Version 0.1.0 (2019-10-01)
---------------------------

**Initial Release**

This is the first release of the Decomp toolkit, providing comprehensive support for the Universal Decompositional Semantics v1.0 dataset.

Core Features
~~~~~~~~~~~~~

**Semantic Graph Processing**
   - Foundation classes for semantic graph manipulation
   - NetworkX and RDF graph format support
   - Flexible annotation loading and processing system

**Universal Dependencies Integration**
   - Complete syntax integration with Universal Dependencies
   - Robust parsing and processing capabilities
   - Cross-linguistic support

**Semantic Annotation Types**
   Full support for UDS v1.0 annotation types:
   
   - **Genericity**: Entity and event genericity annotations
   - **Factuality**: Event factuality and certainty annotations
   - **Protoroles**: Semantic role properties and proto-role annotations
   - **Temporal**: Temporal relationship and ordering annotations
   - **Word Sense**: Lexical semantic annotations

**Corpus Management**
   - Comprehensive corpus loading and processing tools
   - Flexible data splitting and organization
   - Efficient memory management for large datasets

**Documentation and Testing**
   - Complete API documentation
   - Comprehensive example usage
   - Basic test suite for core functionality

Technical Foundation
~~~~~~~~~~~~~~~~~~~~

- **Graph Infrastructure**: Robust graph processing and manipulation
- **Type System**: Well-defined type hierarchy for semantic structures  
- **Extensible Architecture**: Plugin-friendly design for custom annotations
- **Performance Optimization**: Efficient processing for large-scale corpora

Migration and Compatibility
---------------------------

Python Version Support
~~~~~~~~~~~~~~~~~~~~~~

- **v0.1.x - v0.2.x**: Python 3.6+
- **v0.3.x**: Python 3.12+ (requires modern Python features)

Dataset Compatibility
~~~~~~~~~~~~~~~~~~~~~

- **v0.1.x**: Universal Decompositional Semantics v1.0
- **v0.2.x - v0.3.x**: Universal Decompositional Semantics v2.0

Breaking Changes Summary
~~~~~~~~~~~~~~~~~~~~~~~~

**v0.2.0 Breaking Changes**
   - API modifications for document-level graph support
   - Some method signatures updated
   - Enhanced metadata requirements

**v0.3.0 Breaking Changes**
   - Python 3.12+ requirement
   - Modernized type system using new union syntax
   - Updated import paths for PredPatt functionality
   - Enhanced API with new PredPatt integration

Support and Resources
---------------------

- **Documentation**: https://decomp.readthedocs.io/
- **Source Code**: https://github.com/decompositional-semantics-initiative/decomp
- **Issue Tracker**: https://github.com/decompositional-semantics-initiative/decomp/issues