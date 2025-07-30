# Changelog

All notable changes to the Decomp project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-07-30

### Added
- **New PredPatt Integration**: Complete integration of PredPatt semantic role labeling functionality into `decomp.semantics.predpatt` module
- **Modern Python Support**: Full Python 3.12+ compatibility with updated type hints using union syntax (`|`) and built-in generics
- **Modern Packaging**: Migration from `setup.py` to `pyproject.toml` with modern build system

### Changed
- **Type System Modernization**: All type hints updated to Python 3.12+ conventions using `|` union syntax and built-in generics
- **Documentation**: Comprehensive documentation overhaul with detailed API references and usage examples
- **Code Quality**: Implementation of ruff and mypy for consistent code formatting and static type checking
- **Test Suite**: Complete pytest-based test suite with differential testing against original PredPatt implementation

### Technical Details
- **Module Structure**: New modular architecture with `core`, `extraction`, `parsing`, `rules`, `filters`, and `utils` submodules
- **Algorithm Fidelity**: Byte-for-byte identical output compatibility with original PredPatt implementation
- **Dependencies**: Updated to modern versions while maintaining backward compatibility

## [0.2.2] - 2022-06-08

### Fixed
- **Corpus Loading**: Fixed broken corpus load from JSON functionality
- **UDS Annotations**: Corrected error in raw UDS-EventStructure annotations processing

### Notes
- Final release of v0.2.x series before major modernization
- Maintained compatibility with Universal Decompositional Semantics v2.0 dataset

## [0.2.1] - 2021-04-05

### Fixed
- **Python 3.9 Compatibility**: Resolved compatibility issues with Python 3.9
- **Dependency Updates**: Updated dependencies to support newer Python versions

### Notes
- Part of Universal Decompositional Semantics v2.0 release series
- Improved cross-platform compatibility

## [0.2.0] - 2021-03-19

### Added
- **Universal Decompositional Semantics v2.0**: First release supporting UDS 2.0 dataset
- **Document-Level Graphs**: Support for document-level semantic graph structures
- **Raw Annotations**: Access to raw annotation data alongside normalized annotations
- **Advanced Metadata**: Enhanced metadata handling and processing capabilities
- **Visualization Module**: New `decomp.vis` module for graph visualization and analysis
- **Enhanced Graph Support**: Improved NetworkX and RDF graph representations

### Changed
- **Major Version Bump**: Significant architectural changes to support UDS v2.0
- **API Enhancements**: Extended API surface for document-level processing
- **Data Format**: Support for both sentence-level and document-level annotation formats

### Technical Details
- **Graph Structures**: Support for complex document-level semantic relationships
- **Annotation Pipeline**: Enhanced pipeline for processing raw and normalized annotations
- **Metadata Schema**: Advanced metadata schema for annotation provenance and confidence

## [0.1.3] - 2020-03-13

### Fixed
- **RDF Cache**: Fixed RDF cache clearing error that could cause memory issues
- **Document Attributes**: Added missing document and sentence ID attributes for better tracking

### Added
- **Improved Tracking**: Better document and sentence identification in corpus processing

### Notes
- Maintenance release improving stability and debugging capabilities
- Enhanced corpus navigation and identification features

## [0.1.2] - 2020-01-17

### Fixed
- **Corpus Construction**: Fixed corpus construction error when using split parameter
- **Data Splitting**: Resolved issues with train/dev/test split functionality

### Technical Details
- **Split Parameters**: Corrected handling of data split parameters in corpus initialization
- **Error Handling**: Improved error messages for corpus construction failures

## [0.1.1] - 2019-10-19

### Fixed
- **Genericity Annotations**: Fixed copular clause argument linking error in genericity annotations
- **Argument Linking**: Corrected semantic role assignment for copular constructions

### Technical Details
- **Linguistic Accuracy**: Improved handling of copular clause structures in semantic annotation
- **Annotation Quality**: Enhanced accuracy of genericity property assignments

## [0.1.0] - 2019-10-01

### Added
- **Initial Release**: First major release of the Decomp toolkit
- **Universal Decompositional Semantics v1.0**: Complete support for UDS v1.0 dataset
- **Core Framework**: Foundation classes for semantic graph processing
- **Syntax Integration**: Universal Dependencies syntax integration
- **Semantic Properties**: Support for multiple semantic annotation types:
  - Genericity annotations
  - Factuality annotations  
  - Protorole annotations
  - Temporal annotations
  - Word sense annotations
- **Graph Representations**: NetworkX and RDF graph format support
- **Corpus Management**: Tools for loading, processing, and managing UDS corpora
- **Documentation**: Comprehensive documentation and API reference

### Technical Foundation
- **Graph Infrastructure**: Core graph processing and manipulation capabilities
- **Annotation Framework**: Flexible annotation loading and processing system
- **Type System**: Initial type definitions for semantic structures
- **Testing Framework**: Basic test suite for core functionality

---

## Release Notes

### Dataset Compatibility
- **v0.1.x**: Universal Decompositional Semantics v1.0
- **v0.2.x**: Universal Decompositional Semantics v2.0
- **v0.3.x**: Universal Decompositional Semantics v2.0 + PredPatt integration

### Python Version Support
- **v0.1.x - v0.2.x**: Python 3.6+
- **v0.3.x**: Python 3.12+ (modern type hints and language features)

### Breaking Changes
- **v0.2.0**: API changes for document-level graph support
- **v0.3.0**: Modernized type system, requires Python 3.12+, integrated PredPatt functionality

For detailed technical documentation, see the [Decomp Documentation](https://decomp.readthedocs.io/en/latest/).
For issues and support, visit the [GitHub Repository](https://github.com/decompositional-semantics-initiative/decomp).