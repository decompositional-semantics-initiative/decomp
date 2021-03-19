`Universal Decompositional Semantic`_ Types
===========================================

.. _Universal Decompositional Semantic: http://decomp.io/

PredPatt makes very coarse-grained typing distinctions—between
predicate and argument nodes, on the one hand, and between dependency
and head edges, on the other. UDS provides ultra fine-grained typing
distinctions, represented as collections of real-valued
attributes. The union of all node and edge attributes defined in UDS
determines the *UDS type space*; any proper subset determines a *UDS
type subspace*.

UDS attributes are derived from crowd-sourced annotations of the heads
or spans corresponding to predicates and/or arguments and are
represented in the dataset as node and/or edge attributes. It is
important to note that, though all nodes and edges in the semantics
domain have a ``type`` attribute, UDS does not afford any special
status to these types. That is, the only thing that UDS "sees" are the
nodes and edges in the semantics domain. The set of nodes and edges
visible to UDS is a superset of those associated with PredPatt
predicates and their arguments.

There are currently four node type subspaces annotated on
nodes in sentence-level graphs.

  - `Factuality`_ (``factuality``)
  - `Genericity`_ (``genericity``)
  - `Time`_ (``time``)
  - `Entity type`_ (``wordsense``)
  - `Event structure`_ (``event_structure``)

There is currently one edge type subspace annotated on
edges in sentence-level graphs.

  - `Semantic Proto-Roles`_ (``protoroles``)
  - `Event structure`_ (``event_structure``)    

There is currently (starting in UDS2.0) one edge type subspace
annotated on edges in document-level graphs.

  - `Time`_ (``time``)
  - `Event structure`_ (``event_structure``)    
    
Each subspace key lies at the same level as the ``type`` attribute and
maps to a dictionary value. This dictionary maps from attribute keys
(see *Attributes* in each section below) to dictionaries that always
have two keys ``value`` and ``confidence``. See the below paper for
information on how the these are derived from the underlying dataset.

Two versions of these annotations are currently available: one
containing the raw annotator data (``"raw"``) and the other containing
normalized data (``"normalized"``). In the former case, both the
``value`` and ``confidence`` fields described above map to
dictionaries keyed on (anonymized) annotator IDs, where the
corresponding value contains that annotator's response (for the
``value`` dictionary) or confidence (for the ``confidence``
dictionary). In the latter case, the ``value`` and ``confidence``
fields map to single, normalized value and confidence scores,
respectively.

For more information on the normalization used to produce the
normalized annotations, see:

  White, Aaron Steven, Elias Stengel-Eskin, Siddharth Vashishtha, Venkata Subrahmanyan Govindarajan, Dee Ann Reisinger, Tim Vieira, Keisuke Sakaguchi, et al. 2020. `The Universal Decompositional Semantics Dataset and Decomp Toolkit`_. *Proceedings of The 12th Language Resources and Evaluation Conference*, 5698–5707. Marseille, France: European Language Resources Association.


.. _The Universal Decompositional Semantics Dataset and Decomp Toolkit: https://www.aclweb.org/anthology/2020.lrec-1.699/
  
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


Information about each subspace can be found below. Unless otherwise
specified the properties in a particular subspace remain constant
across the raw and normalized formats.
  
Factuality
----------

**Project page**

`<http://decomp.io/projects/factuality/>`_

**Sentence-level attributes**

``factual``

**First UDS version**

1.0

**References**

  White, A.S., D. Reisinger, K. Sakaguchi, T. Vieira, S. Zhang, R. Rudinger, K. Rawlins, & B. Van Durme. 2016. `Universal Decompositional Semantics on Universal Dependencies`_. *Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing*, pages 1713–1723, Austin, Texas, November 1-5, 2016.


  Rudinger, R., White, A.S., & B. Van Durme. 2018. `Neural models of factuality`_. *Proceedings of the 2018 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long Papers)*, pages 731–744. New Orleans, Louisiana, June 1-6, 2018.

.. _Neural models of factuality: https://www.aclweb.org/anthology/N18-1067  
.. _Universal Decompositional Semantics on Universal Dependencies: https://www.aclweb.org/anthology/D16-1177
  
.. code-block:: latex

  @inproceedings{white-etal-2016-universal,
      title = "Universal Decompositional Semantics on {U}niversal {D}ependencies",
      author = "White, Aaron Steven  and
        Reisinger, Dee Ann  and
        Sakaguchi, Keisuke  and
        Vieira, Tim  and
        Zhang, Sheng  and
        Rudinger, Rachel  and
        Rawlins, Kyle  and
        Van Durme, Benjamin",
      booktitle = "Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing",
      month = nov,
      year = "2016",
      address = "Austin, Texas",
      publisher = "Association for Computational Linguistics",
      url = "https://www.aclweb.org/anthology/D16-1177",
      doi = "10.18653/v1/D16-1177",
      pages = "1713--1723",
  }
  
  @inproceedings{rudinger-etal-2018-neural-models,
      title = "Neural Models of Factuality",
      author = "Rudinger, Rachel  and
        White, Aaron Steven  and
        Van Durme, Benjamin",
      booktitle = "Proceedings of the 2018 Conference of the North {A}merican Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long Papers)",
      month = jun,
      year = "2018",
      address = "New Orleans, Louisiana",
      publisher = "Association for Computational Linguistics",
      url = "https://www.aclweb.org/anthology/N18-1067",
      doi = "10.18653/v1/N18-1067",
      pages = "731--744",
  }


Genericity
----------

**Project page**

`<http://decomp.io/projects/genericity/>`_

**Sentence-level attributes**

``arg-particular``, ``arg-kind``, ``arg-abstract``, ``pred-particular``, ``pred-dynamic``, ``pred-hypothetical``

**First UDS version**

1.0

**References**

  Govindarajan, V.S., B. Van Durme, & A.S. White. 2019. `Decomposing Generalization: Models of Generic, Habitual, and Episodic Statements`_. Transactions of the Association for Computational Linguistics.

.. _Decomposing Generalization\: Models of Generic, Habitual, and Episodic Statements: https://www.aclweb.org/anthology/Q19-1035
  
.. code-block:: latex

  @article{govindarajan-etal-2019-decomposing,
      title = "Decomposing Generalization: Models of Generic, Habitual, and Episodic Statements",
      author = "Govindarajan, Venkata  and
        Van Durme, Benjamin  and
        White, Aaron Steven",
      journal = "Transactions of the Association for Computational Linguistics",
      volume = "7",
      month = mar,
      year = "2019",
      url = "https://www.aclweb.org/anthology/Q19-1035",
      doi = "10.1162/tacl_a_00285",
      pages = "501--517"
  }


Time
----

**Project page**

`<http://decomp.io/projects/time/>`_

**Sentence-level attributes**

*normalized*

``dur-hours``, ``dur-instant``, ``dur-forever``, ``dur-weeks``, ``dur-days``, ``dur-months``, ``dur-years``, ``dur-centuries``, ``dur-seconds``, ``dur-minutes``, ``dur-decades``

*raw*

``duration``


**Document-level attributes**

*raw*

``rel-start1``, ``rel-start2``, ``rel-end1``, ``rel-end2``

**First UDS version**

1.0 (sentence-level), 2.0 (document-level)

**References**

  Vashishtha, S., B. Van Durme, & A.S. White. 2019. `Fine-Grained Temporal Relation Extraction`_. *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics (ACL 2019)*, 2906—2919. Florence, Italy, July 29-31, 2019.


.. _Fine-Grained Temporal Relation Extraction: https://www.aclweb.org/anthology/P19-1280
  
.. code-block:: latex
		
  @inproceedings{vashishtha-etal-2019-fine,
      title = "Fine-Grained Temporal Relation Extraction",
      author = "Vashishtha, Siddharth  and
        Van Durme, Benjamin  and
        White, Aaron Steven",
      booktitle = "Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics",
      month = jul,
      year = "2019",
      address = "Florence, Italy",
      publisher = "Association for Computational Linguistics",
      url = "https://www.aclweb.org/anthology/P19-1280",
      doi = "10.18653/v1/P19-1280",
      pages = "2906--2919"
  }


**Notes**

1. The Time dataset has different formats for raw and normalized annotations. The duration attributes from the normalized version are each assigned an ordinal value in the raw version (in ascending order of duration), which is assigned to the single attribute ``duration``.
2. The document-level relation annotations are *only* available in the raw format and only starting in UDS2.0.

Entity type
-----------

**Project page**

`<http://decomp.io/projects/word-sense/>`_

**Sentence-level attributes**

``supersense-noun.shape``, ``supersense-noun.process``, ``supersense-noun.relation``, ``supersense-noun.communication``, ``supersense-noun.time``, ``supersense-noun.plant``, ``supersense-noun.phenomenon``, ``supersense-noun.animal``, ``supersense-noun.state``, ``supersense-noun.substance``, ``supersense-noun.person``, ``supersense-noun.possession``, ``supersense-noun.Tops``, ``supersense-noun.object``, ``supersense-noun.event``, ``supersense-noun.artifact``, ``supersense-noun.act``, ``supersense-noun.body``, ``supersense-noun.attribute``, ``supersense-noun.quantity``, ``supersense-noun.motive``, ``supersense-noun.location``, ``supersense-noun.cognition``, ``supersense-noun.group``, ``supersense-noun.food``, ``supersense-noun.feeling``

**First UDS version**

1.0

**Notes**

1. The key is called ``wordsense`` because the normalized annotations come from UDS-Word Sense (v1.0).

**References**

  White, A.S., D. Reisinger, K. Sakaguchi, T. Vieira, S. Zhang, R. Rudinger, K. Rawlins, & B. Van Durme. 2016. `Universal Decompositional Semantics on Universal Dependencies`_. *Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing*, pages 1713–1723, Austin, Texas, November 1-5, 2016.

.. code-block:: latex

  @inproceedings{white-etal-2016-universal,
      title = "Universal Decompositional Semantics on {U}niversal {D}ependencies",
      author = "White, Aaron Steven  and
        Reisinger, Dee Ann  and
        Sakaguchi, Keisuke  and
        Vieira, Tim  and
        Zhang, Sheng  and
        Rudinger, Rachel  and
        Rawlins, Kyle  and
        Van Durme, Benjamin",
      booktitle = "Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing",
      month = nov,
      year = "2016",
      address = "Austin, Texas",
      publisher = "Association for Computational Linguistics",
      url = "https://www.aclweb.org/anthology/D16-1177",
      doi = "10.18653/v1/D16-1177",
      pages = "1713--1723",
  }


Semantic Proto-Roles
--------------------

**Project page**

`<http://decomp.io/projects/semantic-proto-roles/>`_

**Sentence-level attributes**

``was_used``, ``purpose``, ``partitive``, ``location``, ``instigation``, ``existed_after``, ``time``, ``awareness``, ``change_of_location``, ``manner``, ``sentient``, ``was_for_benefit``, ``change_of_state_continuous``, ``existed_during``, ``change_of_possession``, ``existed_before``, ``volition``, ``change_of_state``

**References**

  Reisinger, D., R. Rudinger, F. Ferraro, C. Harman, K. Rawlins, & B. Van Durme. (2015). `Semantic Proto-Roles`_. *Transactions of the Association for Computational Linguistics 3*:475–488.

  White, A.S., D. Reisinger, K. Sakaguchi, T. Vieira, S. Zhang, R. Rudinger, K. Rawlins, & B. Van Durme. 2016. `Universal Decompositional Semantics on Universal Dependencies`_. *Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing*, pages 1713–1723, Austin, Texas, November 1-5, 2016.

.. _Semantic Proto-Roles: https://www.aclweb.org/anthology/Q15-1034
  
.. code-block:: latex

  @article{reisinger-etal-2015-semantic,
      title = "Semantic Proto-Roles",
      author = "Reisinger, Dee Ann  and
        Rudinger, Rachel  and
        Ferraro, Francis  and
        Harman, Craig  and
        Rawlins, Kyle  and
        Van Durme, Benjamin",
      journal = "Transactions of the Association for Computational Linguistics",
      volume = "3",
      year = "2015",
      url = "https://www.aclweb.org/anthology/Q15-1034",
      doi = "10.1162/tacl_a_00152",
      pages = "475--488",
  }
		
  @inproceedings{white-etal-2016-universal,
      title = "Universal Decompositional Semantics on {U}niversal {D}ependencies",
      author = "White, Aaron Steven  and
        Reisinger, Dee Ann  and
        Sakaguchi, Keisuke  and
        Vieira, Tim  and
        Zhang, Sheng  and
        Rudinger, Rachel  and
        Rawlins, Kyle  and
        Van Durme, Benjamin",
      booktitle = "Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing",
      month = nov,
      year = "2016",
      address = "Austin, Texas",
      publisher = "Association for Computational Linguistics",
      url = "https://www.aclweb.org/anthology/D16-1177",
      doi = "10.18653/v1/D16-1177",
      pages = "1713--1723",
  }


Event structure
---------------

**Project page**

`<http://decomp.io/projects/event-structure/>`_

**Sentence-level attributes**

*normalized*


``distributive``, ``dynamic``, ``natural_parts``, ``part_similarity``, ``telic``, ``avg_part_duration_lbound-centuries``, ``avg_part_duration_ubound-centuries``, ``situation_duration_lbound-centuries``, ``situation_duration_ubound-centuries``, ``avg_part_duration_lbound-days``, ``avg_part_duration_ubound-days``, ``situation_duration_lbound-days``, ``situation_duration_ubound-days``, ``avg_part_duration_lbound-decades``, ``avg_part_duration_ubound-decades``, ``situation_duration_lbound-decades``, ``situation_duration_ubound-decades``, ``avg_part_duration_lbound-forever``, ``avg_part_duration_ubound-forever``, ``situation_duration_lbound-forever``, ``situation_duration_ubound-forever``, ``avg_part_duration_lbound-fractions_of_a_second``, ``avg_part_duration_ubound-fractions_of_a_second``, ``situation_duration_lbound-fractions_of_a_second``, ``situation_duration_ubound-fractions_of_a_second``, ``avg_part_duration_lbound-hours``, ``avg_part_duration_ubound-hours``, ``situation_duration_lbound-hours``, ``situation_duration_ubound-hours``, ``avg_part_duration_lbound-instant``, ``avg_part_duration_ubound-instant``, ``situation_duration_lbound-instant``, ``situation_duration_ubound-instant``, ``avg_part_duration_lbound-minutes``, ``avg_part_duration_ubound-minutes``, ``situation_duration_lbound-minutes``, ``situation_duration_ubound-minutes``, ``avg_part_duration_lbound-months``, ``avg_part_duration_ubound-months``, ``situation_duration_lbound-months``, ``situation_duration_ubound-months``, ``avg_part_duration_lbound-seconds``, ``avg_part_duration_ubound-seconds``, ``situation_duration_lbound-seconds``, ``situation_duration_ubound-seconds``, ``avg_part_duration_lbound-weeks``, ``avg_part_duration_ubound-weeks``, ``situation_duration_lbound-weeks``, ``situation_duration_ubound-weeks``, ``avg_part_duration_lbound-years``, ``avg_part_duration_ubound-years``, ``situation_duration_lbound-years``, ``situation_duration_ubound-years``

*raw*

``dynamic``, ``natural_parts``, ``part_similarity``, ``telic``, ``avg_part_duration_lbound``, ``avg_part_duration_ubound``, ``situation_duration_lbound``, ``situation_duration_ubound``


**Document-level attributes**

``pred1_contains_pred2``, ``pred2_contains_pred1``

**First UDS version**

2.0

**Notes**

1. Whether ``dynamic``, ``situation_duration_lbound``, and ``situation_duration_ubound`` are answered or ``part_similarity``, ``avg_part_duration_lbound``, and ``avg_part_duration_ubound`` are answered is dependent on the answer an annotator gives to ``natural_parts``. Thus, not all node attributes will necessarily be present on all nodes.

**References**

  Gantt, W., L. Glass, & A.S. White. 2021. `Decomposing and Recomposing Event Structure`_. arXiv:2103.10387 [cs.CL].


.. _Decomposing and Recomposing Event Structure: https://arxiv.org/abs/2103.10387
  
.. code-block:: latex

  @misc{gantt2021decomposing,
      title={Decomposing and Recomposing Event Structure}, 
      author={William Gantt and Lelia Glass and Aaron Steven White},
      year={2021},
      eprint={2103.10387},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
  }


 
