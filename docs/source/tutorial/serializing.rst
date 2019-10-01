Serializing the UDS dataset
===========================

The canonical serialization format for the Universal Decompositional
Semantics (UDS) dataset is JSON. For examples, if you would like to
serialize the entire UDS dataset to a file ``uds-ewt.json``, you can
use:

.. code-block:: python

   from decomp import uds

   uds.to_json("uds-ewt.json")

The particular format is based directly on the `adjacency_data`_
method implemented in `NetworkX`_

.. _adjacency_data: https://networkx.github.io/documentation/stable/reference/readwrite/generated/networkx.readwrite.json_graph.adjacency_data.html#networkx.readwrite.json_graph.adjacency_data
.. _NetworkX: https://github.com/networkx/networkx

In addition to this JSON format, any serialization format supported by
`RDFLib`_ can also be used by accessing the `rdf`_ attribute of each
`UDSGraph`_ object. This attribute exposes an `rdflib.graph.Graph`_
object, which implements a `serialize`_ method. By default, this
method outputs rdf/xml. The ``format`` parameter can also be set to
``'n3'``, ``'turtle'``, ``'nt'``, ``'pretty-xml'``, ``'trix'``,
``'trig'``, or ``'nquads'``; and additional formats, such as JSON-LD,
can be supported by installing plugins for RDFLib.

.. _serialize: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.graph.Graph.serialize
.. _rdf: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSGraph.rdf
.. _UDSGraph: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSGraph
.. _rdflib.graph.Graph: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#graph-module

Before considering serialization to such a format, be aware that only
the JSON format mentioned above can be read by the
toolkit. Additionally, note that if your aim is to query the graphs in
the corpus, this can be done using the `query`_ instance method in
``UDSGraph``. See :doc:`querying` for details.

.. _RDFLib: https://github.com/RDFLib/rdflib
.. _query: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSGraph.query
