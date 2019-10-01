`Universal Dependencies`_ Syntactic Graphs
==========================================

.. _Universal Dependencies: https://universaldependencies.org/

The syntactic graphs that form the first layer of annotation in the dataset come from gold UD dependency parses provided in the UD-EWT_ treebank, which contains sentences from the Linguistic Data Consortium's constituency parsed EWT_. UD-EWT has predefined training (``train``), development (``dev``), and test (``test``) data in corresponding files in `CoNLL-U format`_: ``en_ewt-ud-train.conllu``, ``en_ewt-ud-dev.conllu``, and ``en_ewt-ud-test.conllu``. Henceforth, ``SPLIT`` ranges over ``train``, ``dev``, and ``test``.

.. _UD-EWT: https://github.com/UniversalDependencies/UD_English-EWT
.. _EWT: https://catalog.ldc.upenn.edu/LDC2012T13
.. _CoNLL-U format: https://universaldependencies.org/format.html

In UDS, each dependency parsed sentence in UD-EWT is represented as a rooted_ `directed graph`_ (digraph). Each graph's identifier takes the form ``ewt-SPLIT-SENTNUM``, where ``SENTNUM`` is the ordinal position (1-indexed) of the sentence within ``en_ewt-ud-SPLIT.conllu``.

.. _rooted: https://en.wikipedia.org/wiki/Rooted_graph
.. _directed graph: https://en.wikipedia.org/wiki/Directed_graph

Each token in a sentence is associated with a node with identifier ``ewt-SPLIT-SENTNUM-syntax-TOKNUM``, where ``TOKNUM`` is the token's ordinal position within the sentence (1-indexed, following the convention in UD-EWT). At minimum, each node has the following attributes.

  - ``position`` (``int``): the ordinal position (``TOKNUM``) of that node as an integer (again, 1-indexed)
  - ``domain`` (``str``): the subgraph this node is part of (always ``syntax``)
  - ``type`` (``str``): the type of the object in the particular domain (always ``token``)
  - ``form`` (``str``): the actual token
  - ``lemma`` (``str``): the lemma corresponding to the actual token
  - ``upos`` (``str``): the UD part-of-speech tag
  - ``xpos`` (``str``): the Penn TreeBank part-of-speech tag
  - any attribute found in the features column of the CoNLL-U

For information about the values ``upos``, ``xpos``, and the attributes contained in the features column can take on, see the `UD Guidelines`_.

.. _UD Guidelines: https://universaldependencies.org/guidelines.html

Each graph also has a special root node with identifier ``ewt-SPLIT-SENTNUM-root-0``. This node always has a ``position`` attribute set to ``0`` and ``domain`` and ``type`` attributes set to ``root``.

Edges within the graph represent the grammatical relations (dependencies) annotated in UD-EWT. These dependencies are always represented as directed edges pointing from the head to the dependent. At minimum, each edge has the following attributes.

  - ``domain`` (``str``): the subgraph this node is part of (always ``syntax``)
  - ``type`` (``str``): the type of the object in the particular domain (always ``dependency``)
  - ``deprel`` (``str``): the UD dependency relation tag

For information about the values ``deprel`` can take on, see the `UD Guidelines`_.
