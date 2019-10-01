`Universal Decompositional Semantic`_ Types
===========================================

.. _Universal Decompositional Semantic: http://decomp.io/

PredPatt makes very coarse-grained typing distinctions—between predicate and argument nodes, on the one hand, and between dependency and head edges, on the other. UDS provides ultra fine-grained typing distinctions, represented as collections of real-valued attributes. The union of all node and edge attributes defined in UDS determines the *UDS type space*; any proper subset determines a *UDS type subspace*. 

UDS attributes are derived from crowd-sourced annotations of the heads or spans corresponding to predicates and/or arguments and are represented in the dataset as node and/or edge attributes. It is important to note that, though all nodes and edges in the semantics domain have a ``type`` attribute, UDS does not afford any special status to these types. That is, the only thing that UDS "sees" are the nodes and edges in the semantics domain. The set of nodes and edges visible to UDS is a superset of those associated with PredPatt predicates and their arguments.

There are currently four node type subspaces.

  - `Factuality`_ (``factuality``)
  - `Genericity`_ (``genericity``)
  - `Time`_ (``time``)
  - `Entity type`_ (``wordsense``)

There is currently one edge type subspace.

  - `Semantic Proto-Roles`_ (``protoroles``)

Each subspace key lies at the same level as the ``type`` attribute and map to a dictionary value. This dictionary maps from attribute keys (see *Attributes* in each section below) to dictionaries that always have two keys ``value`` and ``confidence``. See the below paper for information on how the these are derived from the underlying dataset.

White, A.S., E. Stengel-Eskin, S. Vashishtha, V. Govindarajan, D. Reisinger, T. Vieira, K. Sakaguchi, S. Zhang, F. Ferraro, R. Rudinger, K. Rawlins, B. Van Durme. 2019. The Universal Decompositional Semantics Dataset and Decomp Toolkit.
    
Factuality
----------

**Project page**

`<http://decomp.io/projects/factuality/>`_

**Attributes**

``factual``

**References**

White, A.S., D. Reisinger, K. Sakaguchi, T. Vieira, S. Zhang, R. Rudinger, K. Rawlins, & B. Van Durme. 2016. Universal Decompositional Semantics on Universal Dependencies. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, pages 1713–1723, Austin, Texas, November 1-5, 2016.

Rudinger, R., White, A.S., & B. Van Durme. 2018. Neural models of factuality. Proceedings of NAACL-HLT 2018, pages 731–744. New Orleans, Louisiana, June 1-6, 2018.

Genericity
----------

**Project page**

`<http://decomp.io/projects/genericity/>`_

**Attributes**

``arg-particular``, ``arg-kind``, ``arg-abstract``, ``pred-particular``, ``pred-dynamic``, ``pred-hypothetical``

**References**

Govindarajan, V.S., B. Van Durme, & A.S. White. 2019. Decomposing Generalization: Models of Generic, Habitual, and Episodic Statements. To appear in Transactions of the Association for Computational Linguistics.

Time
----

**Project page**

`<http://decomp.io/projects/time/>`_

**Attributes**

``dur-hours``, ``dur-instant``, ``dur-forever``, ``dur-weeks``, ``dur-days``, ``supersense-noun.time``, ``dur-months``, ``dur-years``, ``dur-centuries``, ``dur-seconds``, ``dur-minutes``, ``dur-decades``

**References**

Vashishtha, S., B. Van Durme, & A.S. White. 2019. Fine-Grained Temporal Relation Extraction. To appear in Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics (ACL 2019), Florence, Italy, July 29-31, 2019.

Entity type
-----------

**Project page**

`<http://decomp.io/projects/word-sense/>`_

**Attributes**

``supersense-noun.shape``, ``supersense-noun.process``, ``supersense-noun.relation``, ``supersense-noun.communication``, ``supersense-noun.time``, ``supersense-noun.plant``, ``supersense-noun.phenomenon``, ``supersense-noun.animal``, ``supersense-noun.state``, ``supersense-noun.substance``, ``supersense-noun.person``, ``supersense-noun.possession``, ``supersense-noun.Tops``, ``supersense-noun.object``, ``supersense-noun.event``, ``supersense-noun.artifact``, ``supersense-noun.act``, ``supersense-noun.body``, ``supersense-noun.attribute``, ``supersense-noun.quantity``, ``supersense-noun.motive``, ``supersense-noun.location``, ``supersense-noun.cognition``, ``supersense-noun.group``, ``supersense-noun.food``, ``supersense-noun.feeling``

**Note**

The key is called ``wordsense`` because the normalized annotations come from UDS-Word Sense (v1.0).

**References**

White, A.S., D. Reisinger, K. Sakaguchi, T. Vieira, S. Zhang, R. Rudinger, K. Rawlins, & B. Van Durme. 2016. Universal Decompositional Semantics on Universal Dependencies. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, pages 1713–1723, Austin, Texas, November 1-5, 2016.

Semantic Proto-Roles
--------------------

**Project page**

`<http://decomp.io/projects/semantic-proto-roles/>`_

**Attributes**

``was_used``, ``purpose``, ``partitive``, ``location``, ``instigation``, ``existed_after``, ``time``, ``awareness``, ``change_of_location``, ``manner``, ``sentient``, ``was_for_benefit``, ``change_of_state_continuous``, ``existed_during``, ``change_of_possession``, ``existed_before``, ``volition``, ``change_of_state``

**References**

White, A.S., D. Reisinger, K. Sakaguchi, T. Vieira, S. Zhang, R. Rudinger, K. Rawlins, & B. Van Durme. 2016. Universal Decompositional Semantics on Universal Dependencies. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, pages 1713–1723, Austin, Texas, November 1-5, 2016.

