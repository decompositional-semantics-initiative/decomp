`PredPatt`_ Semantic Graphs
===========================

.. _PredPatt: https://github.com/hltcoe/PredPatt

The semantic graphs that form the second layer of annotation in the
dataset are produced by the PredPatt_ system. PredPatt takes as input
a UD parse and produces a set of predicates and set of arguments of
each predicate. Both predicates and arguments are associated with a
single head token in the sentence as well as a set of tokens that make
up the predicate or argument (its span). Predicate or argument spans
may be trivial in only containinig the head token.

For example, given the dependency parse for the sentence *Chris gave
the book to Pat .*, PredPatt produces the following.

::
   
  ?a gave ?b to ?c
      ?a: Chris
      ?b: the book
      ?c: Pat

Assuming UD's 1-indexation, the single predicate in this sentence
(*gave...to*) has a head at position 2 and a span over positions {2,
5}. This predicate has three arguments, one headed by *Chris* at
position 1, with span over position {1}; one headed by *book* at
position 4, with span over positions {3, 4}; and one headed by *Pat*
at position 6, with span over position {6}.
      
See the `PredPatt documentation tests`_ for examples.

.. _PredPatt documentation tests: https://github.com/hltcoe/PredPatt/blob/master/doc/DOCTEST.md

Each predicate and argument produced by PredPatt is associated with a
node in a digraph with identifier
``ewt-SPLIT-SENTNUM-semantics-TYPE-HEADTOKNUM``, where ``TYPE`` is
always either ``pred`` or ``arg`` and ``HEADTOKNUM`` is the ordinal
position of the head token within the sentence (1-indexed, following
the convention in UD-EWT). At minimum, each such node has the
following attributes.

  - ``domain`` (``str``): the subgraph this node is part of (always ``semantics``)
  - ``type`` (``str``): the type of the object in the particular domain (either ``predicate`` or ``argument``)
  - ``frompredpatt`` (``bool``): whether this node is associated with a predicate or argument output by PredPatt (always ``True``)
    
Predicate and argument nodes produced by PredPatt furthermore always
have at least one outgoing *instance* edge that points to nodes in the
syntax domain that correspond to the associated span of the predicate
or argument. At minimum, each such edge has the following attributes.

  - ``domain`` (``str``): the subgraph this node is part of (always ``interface``)
  - ``type`` (``str``): the type of the object in the particular domain (either ``head`` or ``nonhead``)
  - ``frompredpatt`` (``bool``): whether this node is associated with a predicate or argument output by PredPatt (always ``True``)     

Because PredPatt produces a unique head for each predicate and
argument, there is always exactly one instance edge of type ``head``
from any particular node in the semantics domain. There may or may not
be instance edges of type ``nonhead``.

In addition to instance edges, predicate nodes always have exactly one
outgoing edge connecting them to each of the nodes corresponding to
their arguments. At minimum, each such edge has the following
attributes.

  - ``domain`` (``str``): the subgraph this node is part of (always ``semantics``)
  - ``type`` (``str``): the type of the object in the particular domain (always ``dependency``)
  - ``frompredpatt`` (``bool``): whether this node is associated with a predicate or argument output by PredPatt (always ``True``) 

There is one special case where an argument nodes has an outgoing edge
that points to a predicate node: clausal subordination.

For example, given the dependency parse for the sentence *Gene thought
that Chris gave the book to Pat .*, PredPatt produces the following.

::

  ?a thinks ?b
      ?a: Gene
      ?b: SOMETHING := that Chris gave the book to Pat
   
  ?a gave ?b to ?c
      ?a: Chris
      ?b: the book
      ?c: Pat

In this case, the second argument of the predicate headed by *thinks*
is the argument *that Chris gave the book to Pat*, which is headed by
*gave*. This argument is associated with a node of type ``argument``
with span over positions {3, 4, 5, 6, 7, 8, 9} and identifier
``ewt-SPLIT-SENTNUM-semantics-arg-5``. In addition, there is a
predicate headed by *gave*. This predicate is associated with a node
with span over positions {5, 8} and identifier
``ewt-SPLIT-SENTNUM-semantics-pred-5``. Node
``ewt-SPLIT-SENTNUM-semantics-arg-5`` then has an outgoing edge
pointing to ``ewt-SPLIT-SENTNUM-semantics-pred-5``. At minimum, each
such edge has the following attributes.

  - ``domain`` (``str``): the subgraph this node is part of (always ``semantics``)
  - ``type`` (``str``): the type of the object in the particular domain (always ``head``)
  - ``frompredpatt`` (``bool``): whether this node is associated with a predicate or argument output by PredPatt (always ``True``) 
     
The ``type`` attribute in this case has the same value as instance
edges, but crucially the ``domain`` attribute is distinct. In the case
of instance edges, it is ``interface`` and in the case of clausal
subordination, it is ``semantics``. This matters when making queries
against the graph.

If the ``frompredpatt`` attribute has value ``True``, it is guaranteed
that the only semantics edges of type ``head`` are ones that involve
clausal subordination like the above. This is not guaranteed for nodes
for which the ``frompredpatt`` attribute has value ``False``.

Every semantic graph contains at least four additional *performative*
nodes that are note produced by PredPatt (and thus, for which the
``frompredpatt`` attribute has value ``False``).

  - ``ewt-SPLIT-SENTNUM-semantics-arg-0``: an argument node representing the entire sentence in the same way complement clauses are represented
  - ``ewt-SPLIT-SENTNUM-semantics-pred-root``: a predicate node representing the author's production of the entire sentence directed at the addressee
  - ``ewt-SPLIT-SENTNUM-semantics-arg-speaker``: an argument node representing the author
  - ``ewt-SPLIT-SENTNUM-semantics-arg-addressee``: an argument node representing the addressee

All of these nodes have a ``domain`` attribute with value ``semantics``. Unlike nodes associated with PredPatt predicates and arguments, ``ewt-SPLIT-SENTNUM-semantics-pred-root``, ``ewt-SPLIT-SENTNUM-semantics-arg-speaker``, and ``ewt-SPLIT-SENTNUM-semantics-arg-addressee`` have no instance edges connecting them to syntactic nodes. In contrast, ``ewt-SPLIT-SENTNUM-semantics-arg-0`` has an instance head edge to ``ewt-SPLIT-SENTNUM-root-0``.

The ``ewt-SPLIT-SENTNUM-semantics-arg-0`` node has semantics head edges to each of the predicate nodes in the graph that are not dominated by any other semantics node. This node, in addition to ``ewt-SPLIT-SENTNUM-semantics-arg-speaker`` and ``ewt-SPLIT-SENTNUM-semantics-arg-addressee``, has a dependency edge to ``ewt-SPLIT-SENTNUM-semantics-pred-root``.

These nodes are included for purposes of forward compatibility. None of them currently have attributes, but future releases of decomp will include annotations on either them or their edges. 
