Serializing the UDS dataset
===========================

The canonical serialization format for the Universal Decompositional
Semantics (UDS) dataset is JSON. Sentence- and document-level graphs
are serialized separately. For example, if you wanted to serialize
the entire UDS dataset to the files ``uds-sentence.json`` (for
sentences) and ``uds-document.json`` (for documents), you would use:

.. code-block:: python

   from decomp import uds

   uds.to_json("uds-sentence.json", "uds-document.json")

The particular format is based directly on the :py:func:`~networkx.readwrite.json_graph.adjacency_data`
method implemented in NetworkX.

For the sentence-level graphs only, in addition to this JSON format, 
any serialization format supported by RDFLib can also be used by
accessing the ``rdf`` attribute of each :py:class:`~decomp.semantics.uds.UDSSentenceGraph` object.
This attribute exposes an :py:class:`rdflib.graph.Graph` object, which implements
a :py:meth:`~rdflib.graph.Graph.serialize` method. By default, this method outputs rdf/xml. The 
``format`` parameter can also be set to ``'n3'``, ``'turtle'``, 
``'nt'``, ``'pretty-xml'``, ``'trix'``, ``'trig'``, or ``'nquads'``;
and additional formats, such as JSON-LD, can be supported by installing
plugins for RDFLib.

Before considering serialization to such a format, be aware that only
the JSON format mentioned above can be read by the
toolkit. Additionally, note that if your aim is to query the graphs in
the corpus, this can be done using the :py:meth:`~decomp.semantics.uds.UDSSentenceGraph.query` instance method in
``UDSSentenceGraph``. See :doc:`querying` for details.
