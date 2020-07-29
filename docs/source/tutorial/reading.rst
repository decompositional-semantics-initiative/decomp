Reading the UDS dataset
=======================

The most straightforward way to read the Universal Decompositional
Semantics (UDS) dataset is to import it.

.. code-block:: python

   from decomp import UDSCorpus

   uds = UDSCorpus()

This loads a `UDSCorpus`_ object ``uds``, which contains all
graphs across all splits in the data.

.. _UDSCorpus: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSCorpus

As noted in :doc:`quick-start`, the first time you do read UDS, it
will take several minutes to complete while the dataset is built from
the `Universal Dependencies English Web Treebank`_ (UD-EWT), which is not
shipped with the package (but is downloaded automatically on import in
the background), and the `UDS annotations`_, which are shipped with
the package as package data. Normalized annotations are loaded by default.
To load raw annotations, specify ``"raw"`` as the argument to the UDSCorpus
``annotation_format`` keyword arugment as follows:

.. code-block:: python

   from decomp import UDSCorpus

   uds = UDSCorpus(annotation_format="raw")

(See `Adding annotations`_ below for more detail on annotation types.)
Subsequent uses of the corpus will be faster after the initial build,
since the built dataset is cached.

.. _Universal Dependencies English Web Treebank: https://github.com/UniversalDependencies/UD_English-EWT
.. _UDS annotations: http://decomp.io/data/

Standard splits
---------------

If you would rather read only the graphs in the training, development,
or test split, you can do that by specifying the ``split`` parameter
of ``UDSCorpus``.

.. code-block:: python

   from decomp import UDSCorpus

   # read the train split of the UDS corpus
   uds_train = UDSCorpus(split='train')

Adding annotations
------------------
   
Additional annotations beyond the standard UDS annotations can be
added using this method by passing a list of `UDSAnnotation`_
objects. These annotations can be added at two levels: the sentence level
and the document level. Sentence-level annotations contain attributes of
`UDSSentenceGraph`_ nodes or edges. Document-level annotations contain
attributes for `UDSDocumentGraph`_ nodes or edges. Document-level
edge annotations may relate nodes associated with different sentences 
in a document, although they are added as annotations only to the
the appropriate `UDSDocumentGraph`_.

.. _UDSSentenceGraph: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSSentenceGraph
.. _UDSDocumentGraph: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSDocumentGraph
.. _UDSAnnotation: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSAnnotation

Sentence-level and document-level annotations share the same two in-memory
representations: ``RawUDSDataset`` and ``NormalizedUDSDataset``. The former 
may have multiple annotations for the same node or edge attribute, while the
latter must have only a single annotation. Both are loaded from 
JSON-formatted files, but differ in the expected format (see the 
`from_json`_ methods of each class for formatting guidelines). For example,
if you have some additional *normalized* sentence-level annotations in a file
``new_annotations.json``, those can be added to the existing UDS annotations 
using:

.. _NormalizedUDSDataset: ../package/decomp.semantics.uds.html#decomp.semantics.uds.NormalizedUDSDataset
.. _from_json: ../package/decomp.semantics.uds.html#decomp.semantics.uds.NormalizedUDSDataset.from_json

.. code-block:: python

   from decomp import NormalizedUDSDataset
		
   # read annotations
   new_annotations = [NormalizedUDSDataset.from_json("new_annotations.json")]

   # read the train split of the UDS corpus and append new annotations
   uds_train_plus = UDSCorpus(split='train', sentence_annotations=new_annotations)

If instead you wished to add *raw* annotations (and supposing those
annotations were still in "new_annotations.json"), you would do the following:

.. code-block:: python

   from decomp import RawUDSDataset
		
   # read annotations
   new_annotations = [RawUDSDataset.from_json("new_annotations.json")]

   # read the train split of the UDS corpus and append new annotations
   uds_train_plus = UDSCorpus(split='train', sentence_annotations=new_annotations,
                              annotation_format="raw")

If ``new_annotations.json`` contained document-level annotations
you would pass ``new_annotations.json`` to the constructor keyword 
argument ``document_annotations`` instead of to ``sentence_annotations``.
Importantly, these annotations are added *in addition* to the existing
UDS annotations that ship with the toolkit. You do not need to add these
manually.

Finally, it should be noted that querying is currently **not** supported 
for document-level graphs or for sentence-level graphs containing raw
annotations.

Reading from an alternative location
------------------------------------

If you would like to read the dataset from an alternative
location—e.g. if you have serialized the dataset to JSON, using the
`to_json`_ instance method—this can be accomplished using
``UDSCorpus`` class methods (see :doc:`serializing` for more
information on serialization). For example, if you serialize
``uds_train`` to the files ``uds-ewt-sentences-train.json`` (for
sentences) and ``uds-ewt-documents-train.json`` (for the documents),
you can read it back into memory using:

.. _to_json: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSCorpus.to_json

.. code-block:: python

   # serialize uds_train to JSON
   uds_train.to_json("uds-ewt-sentences-train.json", "uds-ewt-documents-train.json")

   # read JSON serialized uds_train
   uds_train = UDSCorpus.from_json("uds-ewt-sentences-train.json", "uds-ewt-documents-train.json")   

Rebuilding the corpus
---------------------
   
If you would like to rebuild the corpus from the UD-EWT CoNLL files
and some set of JSON-formatted annotation files, you can use the
analogous `from_conll`_ class method. Importantly, unlike the
standard instance initialization described above, the UDS annotations
are *not* automatically added. For example, if ``en-ud-train.conllu``
is in the current working directory and you have already loaded
``new_annotations`` as above, a corpus containing only those
annotations (without the UDS annotations) can be loaded using:

.. _from_conll: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSCorpus.from_conll

.. code-block:: python

   # read the train split of the UD corpus and append new annotations
   uds_train_annotated = UDSCorpus.from_conll("en-ud-train.conllu", sentence_annotations=new_annotations)   

This also means that if you only want the semantic graphs as implied
by PredPatt (without annotations), you can use the ``from_conll``
class method to load them.

.. code-block:: python

   # read the train split of the UD corpus
   ud_train = UDSCorpus.from_conll("en-ud-train.conllu")   

Note that, because PredPatt is used for predicate-argument extraction,
only versions of UD-EWT that are compatible with PredPatt can be used
here. Version 1.2 is suggested.
   
Though other serialization formats are available (see
:doc:`serializing`), these formats are not yet supported for reading.
