Querying UDS Graphs
===================

Decomp provides a rich array of methods for querying UDS graphs: both
pre-compiled and user-specified. Arbitrary user-specified graph
queries can be performed using the `UDSGraph.query`_ instance
method. This method accepts arbitrary SPARQL 1.1 queries, either as
strings or as precompiled `Query`_ objects built using RDFlib's
`prepareQuery`_.

.. _UDSGraph.query: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSGraph.query
.. _Query: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.plugins.sparql.html#rdflib.plugins.sparql.sparql.Query
.. _prepareQuery: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.plugins.sparql.html?highlight=preparequery#rdflib.plugins.sparql.processor.prepareQuery

Pre-compiled queries
--------------------

For many use cases, the various instance attributes and methods for
accessing nodes, edges, and their attributes in the UDS graphs will
likely be sufficient; there is no need to use ``query``. For
example, to get a dictionary mapping identifiers for syntax nodes in
the UDS graph to their attributes, you can use:
 
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

Custom queries
--------------

Where the above methods generally turn out to be insufficient is in
selecting nodes and edges on the basis of (combinations of their
attributes). This is where having the full power of SPARQL comes in
handy. This power comes with substantial slow downs in the speed of
queries, however, so if you can do a query without using SPARQL you
should try to.

For example, if you were interested in extracting only predicates
referring to events that likely happened and likely lasted for
minutes, you could use:

.. code-block:: python

   querystr = """
              SELECT ?pred
              WHERE { ?pred <domain> <semantics> ;
                            <type> <predicate> ;
	                    <factual> ?factual ;
		            <dur-minutes> ?duration
	                    FILTER ( ?factual > 0 && ?duration > 0 )
                    }
              """

   results = {gid: graph.query(querystr, query_type='node', cache_rdf=False)
              for gid, graph in uds.items()}

Or more tersely (but equivalently):

.. code-block:: python

   results = uds.query(querystr, query_type='node', cache_rdf=False)
	      
Note that the ``query_type`` parameter is set to ``'node'``. This
setting means that a dictionary mapping node identifiers to node
attribute values will be returned. If no such query type is passed, an
RDFLib `Result`_ object will be returned, which you will need to
postprocess yourself. This is necessary if, for instance, you are
making a ``CONSTRUCT``, ``ASK``, or ``DESCRIBE`` query.

Also, note that the ``cache_rdf`` parameter is set to ``False``. This is a
memory-saving measure, as ``UDSGraph.query`` implicitly builds an RDF
graph on the backend, and these graphs can be quite large. Leaving
``cache_rdf`` at its defaults of ``True`` will substantially speed up
later queries at the expense of sometimes substantial memory costs.

.. _Result: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.query.Result
   
Constraints can also make reference to node and edge attributes of
other nodes. For instance, if you were interested in extracting all
predicates referring to events that are likely spatiotemporally
delimited and have at least one spatiotemporally delimited participant
that was volitional in the event, you could use:

.. code-block:: python

   querystr = """
              SELECT DISTINCT ?node
              WHERE { ?node ?edge ?arg ;
                            <domain> <semantics> ;
                            <type>   <predicate> ;
                            <pred-particular> ?predparticular
			    FILTER ( ?predparticular > 0 ) .
                      ?arg  <domain> <semantics> ;
		            <type>   <argument>  ;
			    <arg-particular> ?argparticular
			    FILTER ( ?argparticular > 0 ) .
                      ?edge <volition> ?volition
		            FILTER ( ?volition > 0 ) .    
                    }
              """

   results = uds.query(querystr, query_type='node', cache_rdf=False)
		
Disjunctive constraints are also possible. For instance, for the last
query, if you were interested in either volitional or sentient
arguments, you could use:

.. code-block:: python

   querystr = """
              SELECT DISTINCT ?node
              WHERE { ?node ?edge ?arg ;
                            <domain> <semantics> ;
                            <type>   <predicate> ;
                            <pred-particular> ?predparticular
			    FILTER ( ?predparticular > 0 ) .
                      ?arg  <domain> <semantics> ;
		            <type>   <argument>  ;
			    <arg-particular> ?argparticular
			    FILTER ( ?argparticular > 0 ) .
                      { ?edge <volition> ?volition
		              FILTER ( ?volition > 0 )
	              } UNION
		      { ?edge <sentient> ?sentient
		              FILTER ( ?sentient > 0 )
	              }
                    }
              """

   results = uds.query(querystr, query_type='node', cache_rdf=False)
  
Beyond returning node attributes based on complex constraints, you can
also return edge attributes. For instance, for the last query, if you
were interested in all the attributes of edges connecting predicates
and arguments satisfying the constraints of the last query, you could
simply change which variable is bound by ``SELECT`` and set
``query_type`` to ``'edge'``.

.. code-block:: python

   querystr = """
              SELECT ?edge
              WHERE { ?node ?edge ?arg ;
                            <domain> <semantics> ;
                            <type>   <predicate> ;
                            <pred-particular> ?predparticular
			    FILTER ( ?predparticular > 0 ) .
                      ?arg  <domain> <semantics> ;
		            <type>   <argument>  ;
			    <arg-particular> ?argparticular
			    FILTER ( ?argparticular > 0 ) .
                      { ?edge <volition> ?volition
		              FILTER ( ?volition > 0 )
	              } UNION
		      { ?edge <sentient> ?sentient
		              FILTER ( ?sentient > 0 )
	              }
                    }
              """

   results = uds.query(querystr, query_type='edge', cache_rdf=False)
