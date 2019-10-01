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
the package as package data. Subsequent uses will be faster, since the
built dataset is cached.

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
added using this method by passing a list of `UDSDataset`_
objects. ``UDSDataset`` objects are loaded from JSON-formatted
files (see `from_json`_ for formatting guidelines). For example, if
you have some additional annotations in a file
``new_annotations.json``, those can be added to the existing UDS
annotations using:

.. _UDSDataset: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSDataset
.. _from_json: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSDataset.from_json

.. code-block:: python

   from decomp import UDSDataset
		
   # read annotations
   new_annotations = [UDSDataset.from_json("new_annotations.json")]

   # read the train split of the UDS corpus and append new annotations
   uds_train_plus = UDSCorpus(split='train', annotations=new_annotations)

Importantly, these annotations are added *in addition* to the existing
UDS annotations that ship with the toolkit. You do not need to add
these manually.

Reading from an alternative location
------------------------------------

If you would like to read the dataset from an alternative
location—e.g. if you have serialized the dataset to JSON, using the
`to_json`_ instance method—this can be accomplished using
``UDSCorpus`` class methods (see :doc:`serializing` for more
information on serialization). For example, if you serialize
``uds_train`` to a file ``uds-ewt-train.json``, you can read it back
into memory using:

.. _to_json: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSCorpus.to_json

.. code-block:: python

   # serialize uds_train to JSON
   uds_train.to_json("uds-ewt-train.json")

   # read JSON serialized uds_train
   uds_train = UDSCorpus.from_json("uds-ewt-train.json")   

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
   ud_train_annotated = UDSCorpus.from_conll("en-ud-train.conllu", new_annotations)   

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
