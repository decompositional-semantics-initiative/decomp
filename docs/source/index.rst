Decomp: A toolkit for decompositional semantics
===============================================

Decomp_ is a toolkit for working with the `Universal Decompositional
Semantics (UDS) dataset`_, which is a collection of directed acyclic
semantic graphs with real-valued node and edge attributes pointing
into `Universal Dependencies`_ syntactic dependency trees.

The toolkit is built on top of NetworkX_ and RDFLib_ making it
straightforward to:

  - read the UDS dataset from its native JSON format
  - query both the syntactic and semantic subgraphs of UDS (as well as
    pointers between them) using SPARQL 1.1 queries
  - serialize UDS graphs to many common formats, such as Notation3_,
    N-Triples_, turtle_, and JSON-LD_, as well as any other format
    supported by NetworkX

The toolkit was built by `Aaron Steven White`_ and is maintained by
the `Decompositional Semantics Initiative`_. The UDS dataset was
constructed from annotations collected by the `Decompositional
Semantics Initiative`_.

If you use either UDS or Decomp in your research, we ask that you cite the following paper:

  White, Aaron Steven, Elias Stengel-Eskin, Siddharth Vashishtha, Venkata Subrahmanyan Govindarajan, Dee Ann Reisinger, Tim Vieira, Keisuke Sakaguchi, et al. 2020. `The Universal Decompositional Semantics Dataset and Decomp Toolkit`_. *Proceedings of The 12th Language Resources and Evaluation Conference*, 5698–5707. Marseille, France: European Language Resources Association.

.. code-block:: latex

  @inproceedings{white-etal-2020-universal,
      title = "The Universal Decompositional Semantics Dataset and Decomp Toolkit",
      author = "White, Aaron Steven  and
        Stengel-Eskin, Elias  and
        Vashishtha, Siddharth  and
        Govindarajan, Venkata Subrahmanyan  and
        Reisinger, Dee Ann  and
        Vieira, Tim  and
        Sakaguchi, Keisuke  and
        Zhang, Sheng  and
        Ferraro, Francis  and
        Rudinger, Rachel  and
        Rawlins, Kyle  and
        Van Durme, Benjamin",
      booktitle = "Proceedings of The 12th Language Resources and Evaluation Conference",
      month = may,
      year = "2020",
      address = "Marseille, France",
      publisher = "European Language Resources Association",
      url = "https://www.aclweb.org/anthology/2020.lrec-1.699",
      pages = "5698--5707",
      ISBN = "979-10-95546-34-4",
  }


.. _Decomp: https://github.com/decompositional-semantics-initiative/decomp
.. _Universal Decompositional Semantics (UDS) dataset: http://decomp.io
.. _Universal Dependencies: https://universaldependencies.org/
.. _NetworkX: https://github.com/networkx/networkx
.. _RDFLib: https://github.com/RDFLib/rdflib
.. _matplotlib: https://matplotlib.org/
.. _D3: https://d3js.org/
.. _Notation3: https://www.w3.org/TeamSubmission/n3/
.. _N-Triples: https://www.w3.org/TR/n-triples/
.. _turtle: https://www.w3.org/TeamSubmission/turtle/
.. _JSON-LD: https://json-ld.org/
.. _Aaron Steven White: http://aaronstevenwhite.io/
.. _Decompositional Semantics Initiative: http://decomp.io/
.. _The Universal Decompositional Semantics Dataset and Decomp Toolkit: https://www.aclweb.org/anthology/2020.lrec-1.699/

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   tutorial/index
   data/index
   package/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
