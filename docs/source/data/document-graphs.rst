Universal Decompositional Document Graphs
=========================================

The semantic graphs that form the third layer of annotation represent
document-level relations. These graphs contain a node for each node in
the document's constituent sentence-level graphs along with a pointer
from the document-level node to the sentence-level node. Unlike the
sentence-level graphs, they are not produced by PredPatt, so whether
any two nodes in a document-level graph are joined by an edge is
determined by whether the relation between the two nodes is annotated
in some UDS dataset.

At minimum, each of these nodes has the following attributes:

.. _UDSDocumentGraph: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSDocumentGraph

   - ``domain`` (``str``): the subgraph this node is part of (always ``document``)
   - ``type`` (``str``): the type of object corresponding to this node in the ``semantics`` domain (either ``predicate`` or ``argument``)
   - ``frompredpatt`` (``bool``): whether this node is associated with a predicate or argument output by PredPatt (always ``False``, although the corresponding ``semantics`` node will have this set as ``True``)
   - ``semantics`` (``dict``): a two-item dictionary containing information about the corresponding ``semantics`` node. The first item, ``graph``, indicates the sentence-level graph that the semantics node comes from. The second item, ``node``, contains the name of the node.

Document graphs are initialized without edges, which are created dynamically
when edge attribute annotations are added. These edges may span nodes
associated with different sentences within a document and may connect not
only predicates to arguments, but predicates to predicates and arguments to
arguments. Any annotations that are provided that cross document boundaries
will be automatically filtered out. Finally, beyond the attributes provided 
by annotations, each edge will also contain all but the last of the core
set of node attributes listed above.

The `UDSDocumentGraph`_ object is wrapped by a `UDSDocument`_, which
holds additional metadata associated with the document, data relating
to its constituent sentences (and their graphs), and methods for
interacting with it. Finally, it should be noted that querying on
document graphs is not currently supported.

.. _UDSDocument: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSDocument
