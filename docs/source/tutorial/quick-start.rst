Quick Start
===========

To read the Universal Decompositional Semantics (UDS) dataset, use:

.. code-block:: python

   from decomp import UDSCorpus

   uds = UDSCorpus()

This imports a `UDSCorpus`_ object ``uds``, which contains all
graphs across all splits in the data. If you would like a corpus,
e.g., containing only a particular split, see other loading options in
:doc:`reading`.

.. _UDSCorpus: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSCorpus

The first time you read UDS, it will take several minutes to
complete while the dataset is built from the `Universal Dependencies
English Web Treebank`_, which is not shipped with the package (but is
downloaded automatically on import in the background), and the `UDS
annotations`_, which are shipped with the package. Subsequent uses
will be faster, since the dataset is cached on build.

.. _Universal Dependencies English Web Treebank: https://github.com/UniversalDependencies/UD_English-EWT
.. _UDS annotations: http://decomp.io/data/

`UDSGraph`_ objects in the corpus can be accessed using standard
dictionary getters or iteration. For instance, to get the UDS graph
corresponding to the 12th sentence in ``en-ud-train.conllu``, you can
use:

.. _UDSGraph: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSGraph

.. code-block:: python

   uds["ewt-train-12"]


More generally, ``UDSCorpus`` objects behave like dictionaries. For
example, to print all the graph identifiers in the corpus
(e.g. ``"ewt-train-12"``), you can use:

.. code-block:: python
   
   for graphid in uds:
       print(graphid)


Similarly, to print all the graph identifiers in the corpus
(e.g. "ewt-in-12") along with the corresponding sentence, you can use:

.. code-block:: python

   for graphid, graph in uds.items():
       print(graphid)
       print(graph.sentence)
       
A list of graph identifiers can also be accessed via the ``graphids``
attribute of the UDSCorpus. A mapping from these identifiers and the
corresponding graph can be accessed via the ``graphs`` attribute.

.. code-block:: python

   # a list of the graph identifiers in the corpus
   uds.graphids

   # a dictionary mapping the graph identifiers to the
   # corresponding graph
   uds.graphs

There are various instance attributes and methods for accessing nodes,
edges, and their attributes in the UDS graphs. For example, to get a
dictionary mapping identifiers for syntax nodes in the UDS graph to
their attributes, you can use:
 
.. code-block:: python

   uds["ewt-train-12"].syntax_nodes

To get a dictionary mapping identifiers for semantics nodes in the UDS
graph to their attributes, you can use:
   
.. code-block:: python
   
   uds["ewt-train-12"].semantics_nodes   

To get a dictionary mapping identifiers for semantics edges (tuples of
node identifiers) in the UDS graph to their attributes, you can use:
  
.. code-block:: python
   
   uds["ewt-train-12"].semantics_edges()

To get a dictionary mapping identifiers for semantics edges (tuples of
node identifiers) in the UDS graph involving the predicate headed by
the 7th token to their attributes, you can use:
   
.. code-block:: python  
   
   uds["ewt-train-12"].semantics_edges('ewt-train-12-semantics-pred-7')

To get a dictionary mapping identifiers for syntax edges (tuples of
node identifiers) in the UDS graph to their attributes, you can use:
   
.. code-block:: python  
   
   uds["ewt-train-12"].syntax_edges()

And to get a dictionary mapping identifiers for syntax edges (tuples
of node identifiers) in the UDS graph involving the node for the 7th
token to their attributes, you can use:
   
.. code-block:: python  
   
   uds["ewt-train-12"].syntax_edges('ewt-train-12-syntax-7')
		

There are also methods for accessing relationships between semantics
and syntax nodes. For example, you can get a tuple of the ordinal
position for the head syntax node in the UDS graph that maps of the
predicate headed by the 7th token in the corresponding sentence to a
list of the form and lemma attributes for that token, you can use:

.. code-block:: python

   uds["ewt-train-12"].head('ewt-train-12-semantics-pred-7', ['form', 'lemma'])

And if you want the same information for every token in the span, you
can use:
   
.. code-block:: python
   
   uds["ewt-train-12"].span('ewt-train-12-semantics-pred-7', ['form', 'lemma'])

This will return a dictionary mapping ordinal position for syntax
nodes in the UDS graph that make of the predicate headed by the 7th
token in the corresponding sentence to a list of the form and lemma
attributes for the corresponding tokens.

More complicated queries of the UDS graph can be performed using the
``query`` method, which accepts arbitrary SPARQL 1.1 queries. See
:doc:`querying` for details.
