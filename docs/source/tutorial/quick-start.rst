Quick Start
===========

To read the Universal Decompositional Semantics (UDS) dataset, use:

.. code-block:: python

   from decomp import UDSCorpus

   uds = UDSCorpus()

This imports a :py:class:`~decomp.semantics.uds.UDSCorpus` object ``uds``, which contains all
graphs across all splits in the data. If you would like a corpus,
e.g., containing only a particular split, see other loading options in
:doc:`reading`.

The first time you read UDS, it will take several minutes to
complete while the dataset is built from the `Universal Dependencies
English Web Treebank`_, which is not shipped with the package (but is
downloaded automatically when first creating a corpus instance), and the `UDS
annotations`_, which are shipped with the package. Subsequent uses
will be faster, since the dataset is cached on build.

.. _Universal Dependencies English Web Treebank: https://github.com/UniversalDependencies/UD_English-EWT
.. _UDS annotations: http://decomp.io/data/

:py:class:`~decomp.semantics.uds.UDSSentenceGraph` objects in the corpus can be accessed using standard
dictionary getters or iteration. For instance, to get the UDS graph
corresponding to the 12th sentence in ``en-ud-train.conllu``, you can
use:

.. code-block:: python

   uds["ewt-train-12"]

To access documents (:py:class:`~decomp.semantics.uds.UDSDocument` objects, each of which has an associated
:py:class:`~decomp.semantics.uds.UDSDocumentGraph`), you can use:

.. code-block:: python

   uds.documents["reviews-112579"]


To get the associated document graph, use:

.. code-block:: python

   uds.documents["reviews-112579"].document_graph


More generally, ``UDSCorpus`` objects behave like dictionaries. For
example, to print all the sentence-level graph identifiers in the corpus
(e.g. ``"ewt-train-12"``), you can use:

.. code-block:: python
   
   for graphid in uds:
       print(graphid)


To print all the document identifiers in the corpus, which correspond
directly to English Web Treebank file IDs (e.g. ``"reviews-112579"``), you 
can use:

.. code-block:: python

   for documentid in uds.documents:
       print(documentid)


Similarly, to print all the sentence-level graph identifiers in the corpus
(e.g. ``"ewt-train-12"``) along with the corresponding sentence, you can use:

.. code-block:: python

   for graphid, graph in uds.items():
       print(graphid)
       print(graph.sentence)
       

Likewise, the following will print all document identifiers, along with each
document's entire text:

.. code-block:: python

   for documentid, document in uds.documents.items():
       print(documentid)
       print(document.text)


A list of sentence-level graph identifiers can also be accessed via the 
``graphids`` attribute of the UDSCorpus. A mapping from these identifiers 
and the corresponding graph can be accessed via the ``graphs`` attribute.

.. code-block:: python

   # a list of the sentence-level graph identifiers in the corpus
   uds.graphids

   # a dictionary mapping the sentence-level 
   # graph identifiers to the corresponding graph
   uds.graphs


A list of document identifiers can also be accessed via the ``documentids``
attribute of the UDSCorpus:

.. code-block:: python

   uds.documentids


For sentence-level graphs, there are various instance attributes and 
methods for accessing nodes, edges, and their attributes in the UDS
sentence-level graphs. For example, to get a dictionary mapping identifiers for syntax nodes in a sentence-level graph to their attributes, you can use:
 
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

More complicated queries of a sentence-level UDS graph can be performed 
using the ``query`` method, which accepts arbitrary SPARQL 1.1 queries. See
:doc:`querying` for details.

Queries on document-level graphs are not currently supported. However, each
:py:class:`~decomp.semantics.uds.UDSDocument` does contain a number of useful attributes, including its ``genre``
(corresponding to the English Web Treebank subcorpus); its ``text`` (as
demonstrated above); its ``timestamp``; the ``sentence_ids`` of its 
constituent sentences; and the sentence-level graphs (``sentence_graphs``) 
associated with those sentences. Additionally, one can also look up the
semantics node associated with a particular node in the document graph via
the :py:meth:`~decomp.semantics.uds.UDSDocument.semantics_node` instance method.

Lastly, iterables for the nodes and edges of a document-level graph may be
accessed as follows:


.. code-block:: python

   uds.documents["reviews-112579"].document_graph.nodes
   uds.documents["reviews-112579"].document_graph.edges


Unlike the nodes and edges in a sentence-level graph, the ones in a document-
level graph all share a common (``document``) domain. By default, document
graphs are initialized without edges and with one node for each semantics node
in the sentence-level graphs associated with the constituent sentences. Edges
may be added by supplying annotations (see :doc:`reading`).