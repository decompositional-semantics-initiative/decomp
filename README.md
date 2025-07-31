# Overview

[![GitHub](https://img.shields.io/badge/github-decomp-blue?logo=github)](https://github.com/decompositional-semantics-initiative/decomp)
[![CI](https://github.com/decompositional-semantics-initiative/decomp/actions/workflows/ci.yml/badge.svg)](https://github.com/decompositional-semantics-initiative/decomp/actions/workflows/ci.yml)
[![Documentation](https://readthedocs.org/projects/decomp/badge/?version=latest)](https://decomp.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Decomp](https://github.com/decompositional-semantics-initiative/decomp)
is a toolkit for working with the [Universal Decompositional Semantics
(UDS) dataset](http://decomp.io), which is a collection of directed
acyclic semantic graphs with real-valued node and edge attributes
pointing into [Universal
Dependencies](https://universaldependencies.org/) syntactic dependency
trees.

![UDS graph example](https://github.com/decompositional-semantics-initiative/decomp/raw/master/uds-graph.png)

The toolkit is built on top of
[NetworkX](https://github.com/networkx/networkx) and
[RDFLib](https://github.com/RDFLib/rdflib) making it straightforward to:

   - read the UDS dataset from its native JSON format
   - query both the syntactic and semantic subgraphs of UDS (as well as
     pointers between them) using SPARQL 1.1 queries
   - serialize UDS graphs to many common formats, such as
     [Notation3](https://www.w3.org/TeamSubmission/n3/),
     [N-Triples](https://www.w3.org/TR/n-triples/),
     [turtle](https://www.w3.org/TeamSubmission/turtle/), and
     [JSON-LD](https://json-ld.org/), as well as any other format
     supported by NetworkX

The toolkit was built by [Aaron Steven
White](http://aaronstevenwhite.io/) and is maintained by the
[Decompositional Semantics Initiative](http://decomp.io/). The UDS
dataset was constructed from annotations collected by the
[Decompositional Semantics Initiative](http://decomp.io/).

# Documentation

The [full documentation for the
package](https://decomp.readthedocs.io/en/latest/index.html) is hosted
at [Read the Docs](https://readthedocs.org/).
	
# Citation

If you make use of the dataset and/or toolkit in your research, we ask
that you please cite the following paper in addition to the paper that
introduces the underlying dataset(s) on which UDS is based.

> White, Aaron Steven, Elias Stengel-Eskin, Siddharth Vashishtha, Venkata Subrahmanyan Govindarajan, Dee Ann Reisinger, Tim Vieira, Keisuke Sakaguchi, et al. 2020. [The Universal Decompositional Semantics Dataset and Decomp Toolkit](https://www.aclweb.org/anthology/2020.lrec-1.699/). In Proceedings of The 12th Language Resources and Evaluation Conference, 5698–5707. Marseille, France: European Language Resources Association.

```latex
@inproceedings{white-etal-2020-universal,
    title = "The Universal Decompositional Semantics Dataset and Decomp Toolkit",
    author = "White, Aaron Steven  and
      Stengel-Eskin, Elias  and
      Vashishtha, Siddharth  and
      Govindarajan, Venkata Subrahmanyan  and
      Reisinger, Dee Ann  and
      Vieira, Tim  and
      Sakaguchi, Keisuke  and
      Zhang, Sheng  and
      Ferraro, Francis  and
      Rudinger, Rachel  and
      Rawlins, Kyle  and
      Van Durme, Benjamin",
    booktitle = "Proceedings of The 12th Language Resources and Evaluation Conference",
    month = may,
    year = "2020",
    address = "Marseille, France",
    publisher = "European Language Resources Association",
    url = "https://www.aclweb.org/anthology/2020.lrec-1.699",
    pages = "5698--5707",
    ISBN = "979-10-95546-34-4",
}
```

# License

Everything besides the contents of `decomp/data` are covered by the
MIT License contained at the same directory level as this README. All
contents of `decomp/data` are covered by the CC-BY-SA 4.0 license
contained in that directory.

# Installation

The most painless way to get started quickly is to use the included
Dockerfile based on jupyter/datascience-notebook with Python 3.12. 
To build the image and start a Jupyter Lab server:

```bash
git clone git://github.com/decompositional-semantics-initiative/decomp.git
cd decomp
docker build -t decomp .
docker run -it -p 8888:8888 decomp
```

This will start a Jupyter Lab server accessible at http://localhost:8888.
To start a Python interactive prompt instead:

```bash
docker run -it decomp python
```

If you prefer to install directly to your local environment, you can
use `pip` to install from GitHub:

```bash
pip install git+https://github.com/decompositional-semantics-initiative/decomp.git
```

**Requirements**: Python 3.12 or higher is required.

You can also clone the repository and install from source:

```bash
git clone https://github.com/decompositional-semantics-initiative/decomp.git
cd decomp
pip install .
```

For development, install the package in editable mode with development dependencies:

```bash
git clone https://github.com/decompositional-semantics-initiative/decomp.git
cd decomp
pip install -e ".[dev]"
```

This installs the package in editable mode along with development tools
including `pytest`, `ruff`, `mypy`, and `ipython`.

**Note for developers**: The development dependencies include most testing requirements,
but `predpatt` (used for differential testing) must be installed separately due to
PyPI restrictions on git dependencies:

```bash
pip install git+https://github.com/hltcoe/PredPatt.git
```

# Quick Start

The UDS corpus can be read by directly importing it.

```python
from decomp import UDSCorpus

uds = UDSCorpus()
```

This imports a `UDSCorpus` object `uds`, which contains all graphs
across all splits in the data.  If you would like a corpus, e.g.,
containing only a particular split, see other loading options in [the
tutorial on reading the
corpus](https://decomp.readthedocs.io/en/latest/tutorial/reading.html)
for details.

The first time you read UDS, it will take several minutes to complete
while the dataset is built from the [Universal Dependencies English Web
Treebank](https://github.com/UniversalDependencies/UD_English-EWT),
which is not shipped with the package (but is downloaded automatically
when first creating a corpus instance), and the [UDS
annotations](http://decomp.io/data/), which are shipped with the
package. Subsequent uses will be faster, since the dataset is cached on
build.

`UDSGraph` objects in the corpus can be accessed using standard
dictionary getters or iteration. For instance, to get the UDS graph
corresponding to the 12th sentence in `en-ud-train.conllu`, you can
use:

``` python
uds["ewt-train-12"]
```

More generally, `UDSCorpus` objects behave like dictionaries. For
example, to print all the graph identifiers in the corpus (e.g.
`"ewt-train-12"`), you can use:

``` python
for graphid in uds:
    print(graphid)
```

Similarly, to print all the graph identifiers in the corpus (e.g.
"ewt-in-12") along with the corresponding sentence, you can use:

``` python
for graphid, graph in uds.items():
    print(graphid)
    print(graph.sentence)
```

A list of graph identifiers can also be accessed via the `graphids`
attribute of the UDSCorpus. A mapping from these identifiers and the
corresponding graph can be accessed via the `graphs` attribute.

``` python
# a list of the graph identifiers in the corpus
uds.graphids

# a dictionary mapping the graph identifiers to the
# corresponding graph
uds.graphs
```

There are various instance attributes and methods for accessing nodes,
edges, and their attributes in the UDS graphs. For example, to get a
dictionary mapping identifiers for syntax nodes in the UDS graph to
their attributes, you can use:

``` python
uds["ewt-train-12"].syntax_nodes
```

To get a dictionary mapping identifiers for semantics nodes in the UDS
graph to their attributes, you can use:

``` python
uds["ewt-train-12"].semantics_nodes   
```

To get a dictionary mapping identifiers for semantics edges (tuples of
node identifiers) in the UDS graph to their attributes, you can use:

``` python
uds["ewt-train-12"].semantics_edges()
```

To get a dictionary mapping identifiers for semantics edges (tuples of
node identifiers) in the UDS graph involving the predicate headed by the
7th token to their attributes, you can use:

``` python
uds["ewt-train-12"].semantics_edges('ewt-train-12-semantics-pred-7')
```

To get a dictionary mapping identifiers for syntax edges (tuples of node
identifiers) in the UDS graph to their attributes, you can use:

``` python
uds["ewt-train-12"].syntax_edges()
```

And to get a dictionary mapping identifiers for syntax edges (tuples of
node identifiers) in the UDS graph involving the node for the 7th token
to their attributes, you can use:

``` python
uds["ewt-train-12"].syntax_edges('ewt-train-12-syntax-7')
```

There are also methods for accessing relationships between semantics and
syntax nodes. For example, you can get a tuple of the ordinal position
for the head syntax node in the UDS graph that maps of the predicate
headed by the 7th token in the corresponding sentence to a list of the
form and lemma attributes for that token, you can use:

``` python
uds["ewt-train-12"].head('ewt-train-12-semantics-pred-7', ['form', 'lemma'])
```

And if you want the same information for every token in the span, you
can use:

``` python
uds["ewt-train-12"].span('ewt-train-12-semantics-pred-7', ['form', 'lemma'])
```

This will return a dictionary mapping ordinal position for syntax nodes
in the UDS graph that make of the predicate headed by the 7th token in
the corresponding sentence to a list of the form and lemma attributes
for the corresponding tokens.

More complicated queries of the UDS graph can be performed using the
`query` method, which accepts arbitrary SPARQL 1.1 queries. See [the
tutorial on querying the
corpus](https://decomp.readthedocs.io/en/latest/tutorial/querying.html)
for details.
