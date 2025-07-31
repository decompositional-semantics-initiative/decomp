"""Decomp: A toolkit for decompositional semantics.

Decomp is a toolkit for working with the Universal Decompositional Semantics
(UDS) dataset, which is a collection of directed acyclic semantic graphs with
real-valued node and edge attributes pointing into Universal Dependencies
syntactic dependency trees.

The toolkit is built on top of NetworkX and RDFLib making it straightforward to:
  - read the UDS dataset from its native JSON format
  - query both the syntactic and semantic subgraphs of UDS (as well as
    pointers between them) using SPARQL 1.1 queries
  - serialize UDS graphs to many common formats, such as Notation3,
    N-Triples, turtle, and JSON-LD, as well as any other format
    supported by NetworkX

Basic usage:
    >>> from decomp import UDSCorpus
    >>> uds = UDSCorpus()
    >>> # Access a specific sentence graph
    >>> graph = uds["ewt-train-12"]
    >>> # Access a document
    >>> doc = uds.documents["reviews-112579"]

The toolkit was built by Aaron Steven White and is maintained by the
Decompositional Semantics Initiative. The UDS dataset was constructed from
annotations collected by the Decompositional Semantics Initiative.

If you use either UDS or Decomp in your research, please cite:
    White, Aaron Steven, et al. 2020. "The Universal Decompositional Semantics
    Dataset and Decomp Toolkit". Proceedings of The 12th Language Resources and
    Evaluation Conference, 5698-5707. Marseille, France: European Language
    Resources Association.

For more information, visit: http://decomp.io
"""

# standard library imports
import importlib.resources
import os
from logging import DEBUG, basicConfig

# local imports
from .semantics.uds import (
    NormalizedUDSAnnotation,
    RawUDSAnnotation,
    UDSCorpus,
)


# get the data directory using importlib.resources
DATA_DIR = str(importlib.resources.files('decomp') / 'data')
basicConfig(
    filename=os.path.join(DATA_DIR, 'build.log'),
    filemode='w',
    level=DEBUG,
)

__all__ = [
    'NormalizedUDSAnnotation',
    'RawUDSAnnotation',
    'UDSCorpus',
]
