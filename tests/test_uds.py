import os
import json
from io import StringIO
from nose.tools import assert_raises
from pkg_resources import resource_filename
from predpatt import PredPatt, PredPattOpts, load_conllu
from decomp.syntax.dependency import DependencyGraphBuilder
from decomp.semantics.predpatt import PredPattGraphBuilder
from decomp.semantics.uds import NormalizedUDSDataset, RawUDSDataset, UDSAnnotation, UDSGraph, UDSCorpus

# TODO: move test strings to separate files
rawtree = '''1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	police	police	NOUN	NN	Number=Sing	3	compound	_	_
3	commander	commander	NOUN	NN	Number=Sing	7	nsubj	_	_
4	of	of	ADP	IN	_	6	case	_	_
5	Ninevah	Ninevah	PROPN	NNP	Number=Sing	6	compound	_	_
6	Province	Province	PROPN	NNP	Number=Sing	3	nmod	_	_
7	announced	announce	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
8	that	that	SCONJ	IN	_	11	mark	_	_
9	bombings	bombing	NOUN	NNS	Number=Plur	11	nsubj	_	_
10	had	have	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	11	aux	_	_
11	declined	decline	VERB	VBN	Tense=Past|VerbForm=Part	7	ccomp	_	_
12	80	80	NUM	CD	NumType=Card	13	nummod	_	_
13	percent	percent	NOUN	NN	Number=Sing	11	dobj	_	_
14	in	in	ADP	IN	_	15	case	_	_
15	Mosul	Mosul	PROPN	NNP	Number=Sing	11	nmod	_	SpaceAfter=No
16	,	,	PUNCT	,	_	11	punct	_	_
17	whereas	whereas	SCONJ	IN	_	20	mark	_	_
18	there	there	PRON	EX	_	20	expl	_	_
19	had	have	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	20	aux	_	_
20	been	be	VERB	VBN	Tense=Past|VerbForm=Part	11	advcl	_	_
21	a	a	DET	DT	Definite=Ind|PronType=Art	23	det	_	_
22	big	big	ADJ	JJ	Degree=Pos	23	amod	_	_
23	jump	jump	NOUN	NN	Number=Sing	20	nsubj	_	_
24	in	in	ADP	IN	_	26	case	_	_
25	the	the	DET	DT	Definite=Def|PronType=Art	26	det	_	_
26	number	number	NOUN	NN	Number=Sing	23	nmod	_	_
27	of	of	ADP	IN	_	28	case	_	_
28	kidnappings	kidnapping	NOUN	NNS	Number=Plur	26	nmod	_	SpaceAfter=No
29	.	.	PUNCT	.	_	7	punct	_	_'''

graph_syntax_nodes = {'tree1-syntax-1': {'Definite': 'Def',
                                                        'PronType': 'Art',
                                                        'domain': 'syntax',
                                                        'form': 'The',
                                                        'lemma': 'the',
                                                        'position': 1,
                                                        'type': 'token',
                                                        'upos': 'DET',
                                                        'xpos': 'DT'},
                                     'tree1-syntax-10': {'Mood': 'Ind',
                                                         'Tense': 'Past',
                                                         'VerbForm': 'Fin',
                                                         'domain': 'syntax',
                                                         'form': 'had',
                                                         'lemma': 'have',
                                                         'position': 10,
                                                         'type': 'token',
                                                         'upos': 'AUX',
                                                         'xpos': 'VBD'},
                                     'tree1-syntax-11': {'Tense': 'Past',
                                                         'VerbForm': 'Part',
                                                         'domain': 'syntax',
                                                         'form': 'declined',
                                                         'lemma': 'decline',
                                                         'position': 11,
                                                         'type': 'token',
                                                         'upos': 'VERB',
                                                         'xpos': 'VBN'},
                                     'tree1-syntax-12': {'NumType': 'Card',
                                                         'domain': 'syntax',
                                                         'form': '80',
                                                         'lemma': '80',
                                                         'position': 12,
                                                         'type': 'token',
                                                         'upos': 'NUM',
                                                         'xpos': 'CD'},
                                     'tree1-syntax-13': {'Number': 'Sing',
                                                         'domain': 'syntax',
                                                         'form': 'percent',
                                                         'lemma': 'percent',
                                                         'position': 13,
                                                         'type': 'token',
                                                         'upos': 'NOUN',
                                                         'xpos': 'NN'},
                                     'tree1-syntax-14': {'domain': 'syntax',
                                                         'form': 'in',
                                                         'lemma': 'in',
                                                         'position': 14,
                                                         'type': 'token',
                                                         'upos': 'ADP',
                                                         'xpos': 'IN'},
                                     'tree1-syntax-15': {'Number': 'Sing',
                                                         'domain': 'syntax',
                                                         'form': 'Mosul',
                                                         'lemma': 'Mosul',
                                                         'position': 15,
                                                         'type': 'token',
                                                         'upos': 'PROPN',
                                                         'xpos': 'NNP'},
                                     'tree1-syntax-16': {'domain': 'syntax',
                                                         'form': ',',
                                                         'lemma': ',',
                                                         'position': 16,
                                                         'type': 'token',
                                                         'upos': 'PUNCT',
                                                         'xpos': ','},
                                     'tree1-syntax-17': {'domain': 'syntax',
                                                         'form': 'whereas',
                                                         'lemma': 'whereas',
                                                         'position': 17,
                                                         'type': 'token',
                                                         'upos': 'SCONJ',
                                                         'xpos': 'IN'},
                                     'tree1-syntax-18': {'domain': 'syntax',
                                                         'form': 'there',
                                                         'lemma': 'there',
                                                         'position': 18,
                                                         'type': 'token',
                                                         'upos': 'PRON',
                                                         'xpos': 'EX'},
                                     'tree1-syntax-19': {'Mood': 'Ind',
                                                         'Tense': 'Past',
                                                         'VerbForm': 'Fin',
                                                         'domain': 'syntax',
                                                         'form': 'had',
                                                         'lemma': 'have',
                                                         'position': 19,
                                                         'type': 'token',
                                                         'upos': 'AUX',
                                                         'xpos': 'VBD'},
                                     'tree1-syntax-2': {'Number': 'Sing',
                                                        'domain': 'syntax',
                                                        'form': 'police',
                                                        'lemma': 'police',
                                                        'position': 2,
                                                        'type': 'token',
                                                        'upos': 'NOUN',
                                                        'xpos': 'NN'},
                                     'tree1-syntax-20': {'Tense': 'Past',
                                                         'VerbForm': 'Part',
                                                         'domain': 'syntax',
                                                         'form': 'been',
                                                         'lemma': 'be',
                                                         'position': 20,
                                                         'type': 'token',
                                                         'upos': 'VERB',
                                                         'xpos': 'VBN'},
                                     'tree1-syntax-21': {'Definite': 'Ind',
                                                         'PronType': 'Art',
                                                         'domain': 'syntax',
                                                         'form': 'a',
                                                         'lemma': 'a',
                                                         'position': 21,
                                                         'type': 'token',
                                                         'upos': 'DET',
                                                         'xpos': 'DT'},
                                     'tree1-syntax-22': {'Degree': 'Pos',
                                                         'domain': 'syntax',
                                                         'form': 'big',
                                                         'lemma': 'big',
                                                         'position': 22,
                                                         'type': 'token',
                                                         'upos': 'ADJ',
                                                         'xpos': 'JJ'},
                                     'tree1-syntax-23': {'Number': 'Sing',
                                                         'domain': 'syntax',
                                                         'form': 'jump',
                                                         'lemma': 'jump',
                                                         'position': 23,
                                                         'type': 'token',
                                                         'upos': 'NOUN',
                                                         'xpos': 'NN'},
                                     'tree1-syntax-24': {'domain': 'syntax',
                                                         'form': 'in',
                                                         'lemma': 'in',
                                                         'position': 24,
                                                         'type': 'token',
                                                         'upos': 'ADP',
                                                         'xpos': 'IN'},
                                     'tree1-syntax-25': {'Definite': 'Def',
                                                         'PronType': 'Art',
                                                         'domain': 'syntax',
                                                         'form': 'the',
                                                         'lemma': 'the',
                                                         'position': 25,
                                                         'type': 'token',
                                                         'upos': 'DET',
                                                         'xpos': 'DT'},
                                     'tree1-syntax-26': {'Number': 'Sing',
                                                         'domain': 'syntax',
                                                         'form': 'number',
                                                         'lemma': 'number',
                                                         'position': 26,
                                                         'type': 'token',
                                                         'upos': 'NOUN',
                                                         'xpos': 'NN'},
                                     'tree1-syntax-27': {'domain': 'syntax',
                                                         'form': 'of',
                                                         'lemma': 'of',
                                                         'position': 27,
                                                         'type': 'token',
                                                         'upos': 'ADP',
                                                         'xpos': 'IN'},
                                     'tree1-syntax-28': {'Number': 'Plur',
                                                         'domain': 'syntax',
                                                         'form': 'kidnappings',
                                                         'lemma': 'kidnapping',
                                                         'position': 28,
                                                         'type': 'token',
                                                         'upos': 'NOUN',
                                                         'xpos': 'NNS'},
                                     'tree1-syntax-29': {'domain': 'syntax',
                                                         'form': '.',
                                                         'lemma': '.',
                                                         'position': 29,
                                                         'type': 'token',
                                                         'upos': 'PUNCT',
                                                         'xpos': '.'},
                                     'tree1-syntax-3': {'Number': 'Sing',
                                                        'domain': 'syntax',
                                                        'form': 'commander',
                                                        'lemma': 'commander',
                                                        'position': 3,
                                                        'type': 'token',
                                                        'upos': 'NOUN',
                                                        'xpos': 'NN'},
                                     'tree1-syntax-4': {'domain': 'syntax',
                                                        'form': 'of',
                                                        'lemma': 'of',
                                                        'position': 4,
                                                        'type': 'token',
                                                        'upos': 'ADP',
                                                        'xpos': 'IN'},
                                     'tree1-syntax-5': {'Number': 'Sing',
                                                        'domain': 'syntax',
                                                        'form': 'Ninevah',
                                                        'lemma': 'Ninevah',
                                                        'position': 5,
                                                        'type': 'token',
                                                        'upos': 'PROPN',
                                                        'xpos': 'NNP'},
                                     'tree1-syntax-6': {'Number': 'Sing',
                                                        'domain': 'syntax',
                                                        'form': 'Province',
                                                        'lemma': 'Province',
                                                        'position': 6,
                                                        'type': 'token',
                                                        'upos': 'PROPN',
                                                        'xpos': 'NNP'},
                                     'tree1-syntax-7': {'Mood': 'Ind',
                                                        'Tense': 'Past',
                                                        'VerbForm': 'Fin',
                                                        'domain': 'syntax',
                                                        'form': 'announced',
                                                        'lemma': 'announce',
                                                        'position': 7,
                                                        'type': 'token',
                                                        'upos': 'VERB',
                                                        'xpos': 'VBD'},
                                     'tree1-syntax-8': {'domain': 'syntax',
                                                        'form': 'that',
                                                        'lemma': 'that',
                                                        'position': 8,
                                                        'type': 'token',
                                                        'upos': 'SCONJ',
                                                        'xpos': 'IN'},
                                     'tree1-syntax-9': {'Number': 'Plur',
                                                        'domain': 'syntax',
                                                        'form': 'bombings',
                                                        'lemma': 'bombing',
                                                        'position': 9,
                                                        'type': 'token',
                                                        'upos': 'NOUN',
                                                        'xpos': 'NNS'}}
graph_normalized_semantics_nodes = {'tree1-semantics-arg-0': {'domain': 'semantics',
                           'frompredpatt': False,
                           'type': 'argument'},
 'tree1-semantics-arg-11': {'domain': 'semantics',
                            'frompredpatt': True,
                            'type': 'argument'},
 'tree1-semantics-arg-13': {'domain': 'semantics',
                            'frompredpatt': True,
                            'genericity': {'arg-abstract': {'confidence': 1.0,
                                                            'value': -1.147},
                                           'arg-kind': {'confidence': 1.0,
                                                        'value': -1.147},
                                           'arg-particular': {'confidence': 1.0,
                                                              'value': 1.1619}},
                            'type': 'argument'},
 'tree1-semantics-arg-15': {'domain': 'semantics',
                            'frompredpatt': True,
                            'genericity': {'arg-abstract': {'confidence': 1.0,
                                                            'value': -1.147},
                                           'arg-kind': {'confidence': 1.0,
                                                        'value': 1.1619},
                                           'arg-particular': {'confidence': 1.0,
                                                              'value': 1.1619}},
                            'type': 'argument'},
 'tree1-semantics-arg-23': {'domain': 'semantics',
                            'frompredpatt': True,
                            'genericity': {'arg-abstract': {'confidence': 1.0,
                                                            'value': -1.147},
                                           'arg-kind': {'confidence': 1.0,
                                                        'value': -1.147},
                                           'arg-particular': {'confidence': 1.0,
                                                              'value': 1.1619}},
                            'type': 'argument'},
 'tree1-semantics-arg-3': {'domain': 'semantics',
                           'frompredpatt': True,
                           'genericity': {'arg-abstract': {'confidence': 1.0,
                                                           'value': -1.147},
                                          'arg-kind': {'confidence': 1.0,
                                                       'value': -1.147},
                                          'arg-particular': {'confidence': 1.0,
                                                             'value': 1.1619}},
                           'type': 'argument'},
 'tree1-semantics-arg-9': {'domain': 'semantics',
                           'frompredpatt': True,
                           'genericity': {'arg-abstract': {'confidence': 1.0,
                                                           'value': -1.147},
                                          'arg-kind': {'confidence': 1.0,
                                                       'value': -1.147},
                                          'arg-particular': {'confidence': 1.0,
                                                             'value': 1.1619}},
                           'type': 'argument'},
'tree1-semantics-arg-author': {'domain': 'semantics', 'frompredpatt': False, 'type': 'argument'},
 'tree1-semantics-arg-addressee': {'domain': 'semantics',
                                   'frompredpatt': False,
                                   'type': 'argument'},
 'tree1-semantics-pred-11': {'domain': 'semantics',
                             'frompredpatt': True,
                             'genericity': {'pred-dynamic': {'confidence': 1.0,
                                                             'value': 0.7748},
                                            'pred-hypothetical': {'confidence': 1.0,
                                                                  'value': -1.5399},
                                            'pred-particular': {'confidence': 1.0,
                                                                'value': 0.7748}},
                             'type': 'predicate'},
 'tree1-semantics-pred-20': {'domain': 'semantics',
                             'frompredpatt': True,
                             'genericity': {'pred-dynamic': {'confidence': 1.0,
                                                             'value': -1.5399},
                                            'pred-hypothetical': {'confidence': 1.0,
                                                                  'value': 0.7748},
                                            'pred-particular': {'confidence': 1.0,
                                                                'value': -1.54}},
                             'type': 'predicate'},
 'tree1-semantics-pred-7': {'domain': 'semantics',
                            'frompredpatt': True,
                            'genericity': {'pred-dynamic': {'confidence': 1.0,
                                                            'value': 0.7748},
                                           'pred-hypothetical': {'confidence': 1.0,
                                                                 'value': -1.54},
                                           'pred-particular': {'confidence': 1.0,
                                                               'value': 0.7748}},
                            'type': 'predicate'},
 'tree1-semantics-pred-root': {'domain': 'semantics',
                               'frompredpatt': False,
                               'type': 'predicate'}}

graph_raw_semantics_nodes = {'tree1-semantics-pred-7': {'domain': 'semantics', 'frompredpatt': True, 'type': 'predicate', 'subspace': {'property': {'confidence': {'annotator1': 0.12}, 'value': {'annotator1': 0.0}}}}, 
                             'tree1-semantics-pred-11': {'domain': 'semantics', 'frompredpatt': True, 'type': 'predicate', 'subspace': {'property': {'confidence': {'annotator2': 0.55, 'annotator3': 0.07}, 'value': {'annotator2': 0.0, 'annotator3': 0.0}}}},
                             'tree1-semantics-pred-20': {'domain': 'semantics', 'frompredpatt': True, 'type': 'predicate', 'subspace': {'property': {'confidence': {'annotator2': 0.55}, 'value': {'annotator2': 0.0}}}},
                             'tree1-semantics-arg-3': {'domain': 'semantics', 'frompredpatt': True, 'type': 'argument'}, 
                             'tree1-semantics-arg-11': {'domain': 'semantics', 'frompredpatt': True, 'type': 'argument'},
                             'tree1-semantics-arg-9': {'domain': 'semantics', 'frompredpatt': True, 'type': 'argument'},
                             'tree1-semantics-arg-13': {'domain': 'semantics', 'frompredpatt': True, 'type': 'argument'},
                             'tree1-semantics-arg-15': {'domain': 'semantics', 'frompredpatt': True, 'type': 'argument'},
                             'tree1-semantics-arg-23': {'domain': 'semantics', 'frompredpatt': True, 'type': 'argument'},
                             'tree1-semantics-pred-root': {'domain': 'semantics', 'type': 'predicate', 'frompredpatt': False}, 
                             'tree1-semantics-arg-0': {'domain': 'semantics', 'type': 'argument', 'frompredpatt': False},
                             'tree1-semantics-arg-author': {'domain': 'semantics', 'type': 'argument', 'frompredpatt': False},
                             'tree1-semantics-arg-addressee': {'domain': 'semantics', 'type': 'argument', 'frompredpatt': False}}

graph_normalized_semantics_edges = {('tree1-semantics-arg-0', 'tree1-semantics-pred-20'): {'domain': 'semantics',
                                                        'frompredpatt': False,
                                                        'type': 'head'},
 ('tree1-semantics-arg-0', 'tree1-semantics-pred-7'): {'domain': 'semantics',
                                                       'frompredpatt': False,
                                                       'type': 'head'},
 ('tree1-semantics-arg-11', 'tree1-semantics-pred-11'): {'domain': 'semantics',
                                                         'frompredpatt': True,
                                                         'type': 'head'},
 ('tree1-semantics-pred-11', 'tree1-semantics-arg-13'): {'domain': 'semantics',
                                                         'frompredpatt': True,
                                                         'protoroles': {'awareness': {'confidence': 1.0,
                                                                                      'value': -0.0},
                                                                        'change_of_location': {'confidence': 1.0,
                                                                                               'value': -0.0},
                                                                        'change_of_possession': {'confidence': 1.0,
                                                                                                 'value': -0.0},
                                                                        'change_of_state': {'confidence': 0.1675,
                                                                                            'value': 0.0032},
                                                                        'change_of_state_continuous': {'confidence': 0.1675,
                                                                                                       'value': 0.0032},
                                                                        'existed_after': {'confidence': 0.6796,
                                                                                          'value': 0.0111},
                                                                        'existed_before': {'confidence': 0.6796,
                                                                                           'value': 0.0111},
                                                                        'existed_during': {'confidence': 1.0,
                                                                                           'value': 1.3421},
                                                                        'instigation': {'confidence': 1.0,
                                                                                        'value': -0.0},
                                                                        'partitive': {'confidence': 0.564,
                                                                                      'value': -0.0941},
                                                                        'sentient': {'confidence': 1.0,
                                                                                     'value': -0.9348},
                                                                        'volition': {'confidence': 1.0,
                                                                                     'value': -0.0},
                                                                        'was_for_benefit': {'confidence': 1.0,
                                                                                            'value': -0.0},
                                                                        'was_used': {'confidence': 0.564,
                                                                                     'value': -0.0}},
                                                         'type': 'dependency'},
 ('tree1-semantics-pred-11', 'tree1-semantics-arg-15'): {'domain': 'semantics',
                                                         'frompredpatt': True,
                                                         'type': 'dependency'},
 ('tree1-semantics-pred-11', 'tree1-semantics-arg-9'): {'domain': 'semantics',
                                                        'frompredpatt': True,
                                                        'protoroles': {'awareness': {'confidence': 0.1395,
                                                                                     'value': -0.0549},
                                                                       'change_of_location': {'confidence': 0.1395,
                                                                                              'value': -0.0549},
                                                                       'change_of_possession': {'confidence': 1.0,
                                                                                                'value': -0.3909},
                                                                       'change_of_state': {'confidence': 0.3333,
                                                                                           'value': -0.0085},
                                                                       'change_of_state_continuous': {'confidence': 0.0791,
                                                                                                      'value': -0.0351},
                                                                       'existed_after': {'confidence': 0.6567,
                                                                                         'value': 0.124},
                                                                       'existed_before': {'confidence': 1.0,
                                                                                          'value': 1.3954},
                                                                       'existed_during': {'confidence': 1.0,
                                                                                          'value': 1.3959},
                                                                       'instigation': {'confidence': 1.0,
                                                                                       'value': -1.5074},
                                                                       'partitive': {'confidence': 0.0791,
                                                                                     'value': -0.1354},
                                                                       'sentient': {'confidence': 1.0,
                                                                                    'value': -1.508},
                                                                       'volition': {'confidence': 1.0,
                                                                                    'value': -0.3909},
                                                                       'was_for_benefit': {'confidence': 0.3418,
                                                                                           'value': 0.0008},
                                                                       'was_used': {'confidence': 0.3333,
                                                                                    'value': -0.0085}},
                                                        'type': 'dependency'},
 ('tree1-semantics-pred-20', 'tree1-semantics-arg-23'): {'domain': 'semantics',
                                                         'frompredpatt': True,
                                                         'type': 'dependency'},
 ('tree1-semantics-pred-7', 'tree1-semantics-arg-11'): {'domain': 'semantics',
                                                        'frompredpatt': True,
                                                        'type': 'dependency'},
 ('tree1-semantics-pred-7', 'tree1-semantics-arg-3'): {'domain': 'semantics',
                                                       'frompredpatt': True,
                                                       'protoroles': {'awareness': {'confidence': 1.0,
                                                                                    'value': 1.3526},
                                                                      'change_of_location': {'confidence': 0.272,
                                                                                             'value': -0.0922},
                                                                      'change_of_possession': {'confidence': 0.7724,
                                                                                               'value': -0.0},
                                                                      'change_of_state': {'confidence': 0.2067,
                                                                                          'value': -0.0548},
                                                                      'change_of_state_continuous': {'confidence': 1.0,
                                                                                                     'value': -0.0},
                                                                      'existed_after': {'confidence': 1.0,
                                                                                        'value': 1.3527},
                                                                      'existed_before': {'confidence': 1.0,
                                                                                         'value': 1.3527},
                                                                      'existed_during': {'confidence': 1.0,
                                                                                         'value': 1.3557},
                                                                      'instigation': {'confidence': 1.0,
                                                                                      'value': 1.3557},
                                                                      'partitive': {'confidence': 0.1148,
                                                                                    'value': -0.0018},
                                                                      'sentient': {'confidence': 1.0,
                                                                                   'value': 1.354},
                                                                      'volition': {'confidence': 1.0,
                                                                                   'value': 1.3545},
                                                                      'was_for_benefit': {'confidence': 0.1976,
                                                                                          'value': -0.0504},
                                                                      'was_used': {'confidence': 0.4373,
                                                                                   'value': -0.0207}},
                                                       'type': 'dependency'},
 ('tree1-semantics-pred-root', 'tree1-semantics-arg-0'): {'domain': 'semantics',
                                                          'frompredpatt': False,
                                                          'type': 'dependency'},
 ('tree1-semantics-pred-root', 'tree1-semantics-arg-addressee'): {'domain': 'semantics',
                                                                  'frompredpatt': False,
                                                                  'type': 'dependency'},
 ('tree1-semantics-pred-root', 'tree1-semantics-arg-author'): {'domain': 'semantics',
                                                                'frompredpatt': False,
                                                                'type': 'dependency'}}

graph_raw_semantics_edges = {('tree1-semantics-pred-7', 'tree1-semantics-arg-3'): {'domain': 'semantics', 'type': 'dependency', 'frompredpatt': True, 'subspace': {'property': {'confidence': {'annotator2': 0.55}, 'value': {'annotator2': 0.0}}}}, 
                             ('tree1-semantics-pred-7', 'tree1-semantics-arg-11'): {'domain': 'semantics', 'type': 'dependency', 'frompredpatt': True}, 
                             ('tree1-semantics-pred-11', 'tree1-semantics-arg-9'): {'domain': 'semantics', 'type': 'dependency', 'frompredpatt': True},
                             ('tree1-semantics-pred-11', 'tree1-semantics-arg-13'): {'domain': 'semantics', 'type': 'dependency', 'frompredpatt': True, 'subspace': {'property': {'confidence': {'annotator1': 0.12}, 'value': {'annotator1': 0.0}}}},
                             ('tree1-semantics-pred-11', 'tree1-semantics-arg-15'): {'domain': 'semantics', 'type': 'dependency', 'frompredpatt': True, 'subspace': {'property': {'confidence': {'annotator2': 0.55, 'annotator3': 0.07}, 'value': {'annotator2': 0.0, 'annotator3': 0.0}}}},
                             ('tree1-semantics-pred-20', 'tree1-semantics-arg-23'): {'domain': 'semantics', 'type': 'dependency', 'frompredpatt': True},
                             ('tree1-semantics-arg-11', 'tree1-semantics-pred-11'): {'domain': 'semantics', 'type': 'head', 'frompredpatt': True},
                             ('tree1-semantics-pred-root', 'tree1-semantics-arg-0'): {'domain': 'semantics', 'type': 'dependency', 'frompredpatt': False},
                             ('tree1-semantics-pred-root', 'tree1-semantics-arg-author'): {'domain': 'semantics', 'type': 'dependency', 'frompredpatt': False},
                             ('tree1-semantics-pred-root', 'tree1-semantics-arg-addressee'): {'domain': 'semantics', 'type': 'dependency', 'frompredpatt': False},
                             ('tree1-semantics-arg-0', 'tree1-semantics-pred-7'): {'domain': 'semantics', 'type': 'head', 'frompredpatt': False},
                             ('tree1-semantics-arg-0', 'tree1-semantics-pred-20'): {'domain': 'semantics', 'type': 'head', 'frompredpatt': False}}

graph_syntax_edges = {('tree1-root-0', 'tree1-syntax-7'): {'deprel': 'root',
                                                                         'domain': 'syntax',
                                                                         'type': 'dependency'},
                                     ('tree1-syntax-11', 'tree1-syntax-10'): {'deprel': 'aux',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-11', 'tree1-syntax-13'): {'deprel': 'dobj',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-11', 'tree1-syntax-15'): {'deprel': 'nmod',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-11', 'tree1-syntax-16'): {'deprel': 'punct',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-11', 'tree1-syntax-20'): {'deprel': 'advcl',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-11', 'tree1-syntax-8'): {'deprel': 'mark',
                                                                             'domain': 'syntax',
                                                                             'type': 'dependency'},
                                     ('tree1-syntax-11', 'tree1-syntax-9'): {'deprel': 'nsubj',
                                                                             'domain': 'syntax',
                                                                             'type': 'dependency'},
                                     ('tree1-syntax-13', 'tree1-syntax-12'): {'deprel': 'nummod',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-15', 'tree1-syntax-14'): {'deprel': 'case',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-20', 'tree1-syntax-17'): {'deprel': 'mark',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-20', 'tree1-syntax-18'): {'deprel': 'expl',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-20', 'tree1-syntax-19'): {'deprel': 'aux',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-20', 'tree1-syntax-23'): {'deprel': 'nsubj',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-23', 'tree1-syntax-21'): {'deprel': 'det',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-23', 'tree1-syntax-22'): {'deprel': 'amod',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-23', 'tree1-syntax-26'): {'deprel': 'nmod',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-26', 'tree1-syntax-24'): {'deprel': 'case',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-26', 'tree1-syntax-25'): {'deprel': 'det',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-26', 'tree1-syntax-28'): {'deprel': 'nmod',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-28', 'tree1-syntax-27'): {'deprel': 'case',
                                                                              'domain': 'syntax',
                                                                              'type': 'dependency'},
                                     ('tree1-syntax-3', 'tree1-syntax-1'): {'deprel': 'det',
                                                                            'domain': 'syntax',
                                                                            'type': 'dependency'},
                                     ('tree1-syntax-3', 'tree1-syntax-2'): {'deprel': 'compound',
                                                                            'domain': 'syntax',
                                                                            'type': 'dependency'},
                                     ('tree1-syntax-3', 'tree1-syntax-6'): {'deprel': 'nmod',
                                                                            'domain': 'syntax',
                                                                            'type': 'dependency'},
                                     ('tree1-syntax-6', 'tree1-syntax-4'): {'deprel': 'case',
                                                                            'domain': 'syntax',
                                                                            'type': 'dependency'},
                                     ('tree1-syntax-6', 'tree1-syntax-5'): {'deprel': 'compound',
                                                                            'domain': 'syntax',
                                                                            'type': 'dependency'},
                                     ('tree1-syntax-7', 'tree1-syntax-11'): {'deprel': 'ccomp',
                                                                             'domain': 'syntax',
                                                                             'type': 'dependency'},
                                     ('tree1-syntax-7', 'tree1-syntax-29'): {'deprel': 'punct',
                                                                             'domain': 'syntax',
                                                                             'type': 'dependency'},
                                     ('tree1-syntax-7', 'tree1-syntax-3'): {'deprel': 'nsubj',
                                                                            'domain': 'syntax',
                                                                            'type': 'dependency'}}
graph_query_results = {('tree1-semantics-pred-7', 'tree1-semantics-arg-3'): {'domain': 'semantics',
                                                       'frompredpatt': True,
                                                       'protoroles': {'awareness': {'confidence': 1.0,
                                                                                    'value': 1.3526},
                                                                      'change_of_location': {'confidence': 0.272,
                                                                                             'value': -0.0922},
                                                                      'change_of_possession': {'confidence': 0.7724,
                                                                                               'value': -0.0},
                                                                      'change_of_state': {'confidence': 0.2067,
                                                                                          'value': -0.0548},
                                                                      'change_of_state_continuous': {'confidence': 1.0,
                                                                                                     'value': -0.0},
                                                                      'existed_after': {'confidence': 1.0,
                                                                                        'value': 1.3527},
                                                                      'existed_before': {'confidence': 1.0,
                                                                                         'value': 1.3527},
                                                                      'existed_during': {'confidence': 1.0,
                                                                                         'value': 1.3557},
                                                                      'instigation': {'confidence': 1.0,
                                                                                      'value': 1.3557},
                                                                      'partitive': {'confidence': 0.1148,
                                                                                    'value': -0.0018},
                                                                      'sentient': {'confidence': 1.0,
                                                                                   'value': 1.354},
                                                                      'volition': {'confidence': 1.0,
                                                                                   'value': 1.3545},
                                                                      'was_for_benefit': {'confidence': 0.1976,
                                                                                          'value': -0.0504},
                                                                      'was_used': {'confidence': 0.4373,
                                                                                   'value': -0.0207}},
                                                       'type': 'dependency'}}
graph_sentence = 'The police commander of Ninevah Province announced that bombings had declined 80 percent in Mosul , whereas there had been a big jump in the number of kidnappings .'

listtree = [l.split() for l in rawtree.split('\n')]

normalized_node_annotation = '{"tree1": {"tree1-semantics-arg-15": {"genericity": {"arg-kind": {"confidence": 1.0, "value": 1.1619}, "arg-abstract": {"confidence": 1.0, "value": -1.147}, "arg-particular": {"confidence": 1.0, "value": 1.1619}}}, "tree1-semantics-pred-7": {"genericity": {"pred-dynamic": {"confidence": 1.0, "value": 0.7748}, "pred-hypothetical": {"confidence": 1.0, "value": -1.54}, "pred-particular": {"confidence": 1.0, "value": 0.7748}}}, "tree1-semantics-arg-3": {"genericity": {"arg-kind": {"confidence": 1.0, "value": -1.147}, "arg-abstract": {"confidence": 1.0, "value": -1.147}, "arg-particular": {"confidence": 1.0, "value": 1.1619}}}, "tree1-semantics-pred-11": {"genericity": {"pred-dynamic": {"confidence": 1.0, "value": 0.7748}, "pred-hypothetical": {"confidence": 1.0, "value": -1.5399}, "pred-particular": {"confidence": 1.0, "value": 0.7748}}}, "tree1-semantics-pred-20": {"genericity": {"pred-dynamic": {"confidence": 1.0, "value": -1.5399}, "pred-hypothetical": {"confidence": 1.0, "value": 0.7748}, "pred-particular": {"confidence": 1.0, "value": -1.54}}}, "tree1-semantics-arg-23": {"genericity": {"arg-kind": {"confidence": 1.0, "value": -1.147}, "arg-abstract": {"confidence": 1.0, "value": -1.147}, "arg-particular": {"confidence": 1.0, "value": 1.1619}}}, "tree1-semantics-arg-9": {"genericity": {"arg-kind": {"confidence": 1.0, "value": -1.147}, "arg-abstract": {"confidence": 1.0, "value": -1.147}, "arg-particular": {"confidence": 1.0, "value": 1.1619}}}, "tree1-semantics-arg-13": {"genericity": {"arg-kind": {"confidence": 1.0, "value": -1.147}, "arg-abstract": {"confidence": 1.0, "value": -1.147}, "arg-particular": {"confidence": 1.0, "value": 1.1619}}}}}'
normalized_edge_annotation = '{"tree1": {"tree1-semantics-pred-11%%tree1-semantics-arg-13": {"protoroles": {"instigation": {"confidence": 1.0, "value": -0.0}, "change_of_possession": {"confidence": 1.0, "value": -0.0}, "existed_before": {"confidence": 0.6796, "value": 0.0111}, "was_for_benefit": {"confidence": 1.0, "value": -0.0}, "change_of_state_continuous": {"confidence": 0.1675, "value": 0.0032}, "change_of_state": {"confidence": 0.1675, "value": 0.0032}, "volition": {"confidence": 1.0, "value": -0.0}, "change_of_location": {"confidence": 1.0, "value": -0.0}, "partitive": {"confidence": 0.564, "value": -0.0941}, "existed_during": {"confidence": 1.0, "value": 1.3421}, "existed_after": {"confidence": 0.6796, "value": 0.0111}, "awareness": {"confidence": 1.0, "value": -0.0}, "sentient": {"confidence": 1.0, "value": -0.9348}, "was_used": {"confidence": 0.564, "value": -0.0}}}, "tree1-semantics-pred-7%%tree1-semantics-arg-3": {"protoroles": {"instigation": {"confidence": 1.0, "value": 1.3557}, "change_of_possession": {"confidence": 0.7724, "value": -0.0}, "existed_before": {"confidence": 1.0, "value": 1.3527}, "was_for_benefit": {"confidence": 0.1976, "value": -0.0504}, "change_of_state_continuous": {"confidence": 1.0, "value": -0.0}, "change_of_state": {"confidence": 0.2067, "value": -0.0548}, "volition": {"confidence": 1.0, "value": 1.3545}, "change_of_location": {"confidence": 0.272, "value": -0.0922}, "partitive": {"confidence": 0.1148, "value": -0.0018}, "existed_during": {"confidence": 1.0, "value": 1.3557}, "existed_after": {"confidence": 1.0, "value": 1.3527}, "awareness": {"confidence": 1.0, "value": 1.3526}, "sentient": {"confidence": 1.0, "value": 1.354}, "was_used": {"confidence": 0.4373, "value": -0.0207}}}, "tree1-semantics-pred-11%%tree1-semantics-arg-9": {"protoroles": {"instigation": {"confidence": 1.0, "value": -1.5074}, "change_of_possession": {"confidence": 1.0, "value": -0.3909}, "existed_before": {"confidence": 1.0, "value": 1.3954}, "was_for_benefit": {"confidence": 0.3418, "value": 0.0008}, "change_of_state_continuous": {"confidence": 0.0791, "value": -0.0351}, "change_of_state": {"confidence": 0.3333, "value": -0.0085}, "volition": {"confidence": 1.0, "value": -0.3909}, "change_of_location": {"confidence": 0.1395, "value": -0.0549}, "partitive": {"confidence": 0.0791, "value": -0.1354}, "existed_during": {"confidence": 1.0, "value": 1.3959}, "existed_after": {"confidence": 0.6567, "value": 0.124}, "awareness": {"confidence": 0.1395, "value": -0.0549}, "sentient": {"confidence": 1.0, "value": -1.508}, "was_used": {"confidence": 0.3333, "value": -0.0085}}}}}'

raw_node_annotation = '{"tree1": {"tree1-semantics-pred-7": {"subspace": {"property": {"confidence": {"annotator1": 0.12}, "value": {"annotator1": 0.0}}}}, "tree1-semantics-pred-11": {"subspace": {"property": {"confidence": {"annotator2": 0.55, "annotator3": 0.07}, "value": {"annotator2": 0.0, "annotator3": 0.0}}}}, "tree1-semantics-pred-20": {"subspace": {"property": {"confidence": {"annotator2": 0.55}, "value": {"annotator2": 0.0}}}}}}'
raw_edge_annotation = '{"tree1": {"tree1-semantics-pred-11%%tree1-semantics-arg-13": {"subspace": {"property": {"confidence": {"annotator1": 0.12}, "value": {"annotator1": 0.0}}}}, "tree1-semantics-pred-11%%tree1-semantics-arg-15": {"subspace": {"property": {"confidence": {"annotator2": 0.55, "annotator3": 0.07}, "value": {"annotator2": 0.0, "annotator3": 0.0}}}}, "tree1-semantics-pred-7%%tree1-semantics-arg-3": {"subspace": {"property": {"confidence": {"annotator2": 0.55}, "value": {"annotator2": 0.0}}}}}}'

def setup_normalized_annotations():
    norm_node_ann = NormalizedUDSDataset(json.loads(normalized_node_annotation))
    norm_edge_ann = NormalizedUDSDataset(json.loads(normalized_edge_annotation))

    return norm_node_ann, norm_edge_ann

def setup_raw_annotations():
    raw_node_ann = RawUDSDataset(json.loads(raw_node_annotation))
    raw_edge_ann = RawUDSDataset(json.loads(raw_edge_annotation))

    return raw_node_ann, raw_edge_ann

def setup_graph(normalized=True):
    if normalized:
        node_ann, edge_ann = setup_normalized_annotations()
    else:
        node_ann, edge_ann = setup_raw_annotations()
    
    ud = DependencyGraphBuilder.from_conll(listtree, 'tree1')
    
    pp = PredPatt(next(load_conllu(rawtree))[1],
                  opts=PredPattOpts(resolve_relcl=True,
                                    borrow_arg_for_relcl=True,
                                    resolve_conj=False,
                                    cut=True))

    pp_graph = PredPattGraphBuilder.from_predpatt(pp, ud, 'tree1')

    graph = UDSGraph(pp_graph, 'tree1')
    graph.add_annotation(*node_ann['tree1'])
    graph.add_annotation(*edge_ann['tree1'])
    
    return graph

def test_constructing_rdf_for_graph_with_raw_annotations_fails():
    graph = setup_graph(normalized=False)
    assert hasattr(graph, '_rdf') == False # RDF not yet built
    assert_raises(TypeError, lambda: graph.rdf) # attempt to build RDF

def test_direct_instantiation_of_uds_annotation_fails():
    assert_raises(TypeError, UDSAnnotation, None)

def test_normalized_uds_annotation():
    norm_node_ann, norm_edge_ann = setup_normalized_annotations()
    norm_node_ann_direct = json.loads(normalized_node_annotation)['tree1']
    norm_edge_ann_direct = json.loads(normalized_edge_annotation)['tree1']

    assert all([not edge_attrs
                for n, (node_attrs, edge_attrs) in norm_node_ann.items()])

    assert all([norm_node_ann_direct[k] == v
                for n, (node_attrs, edge_attrs) in norm_node_ann.items()
                for k, v in node_attrs.items()])

    assert all([not node_attrs
                for n, (node_attrs, edge_attrs) in norm_edge_ann.items()])

    assert all([norm_edge_ann_direct['%%'.join(k)] == v
                for n, (node_attrs, edge_attrs) in norm_edge_ann.items()
                for k, v in edge_attrs.items()])

def test_raw_uds_annotation():
    raw_node_ann, raw_edge_ann = setup_raw_annotations()
    raw_node_ann_direct = json.loads(raw_node_annotation)['tree1']
    raw_edge_ann_direct = json.loads(raw_edge_annotation)['tree1']

    assert all([not edge_attrs
                for n, (node_attrs, edge_attrs) in raw_node_ann.items()])

    assert all([raw_node_ann_direct[k] == v
                for n, (node_attrs, edge_attrs) in raw_node_ann.items()
                for k, v in node_attrs.items()])

    assert all([not node_attrs
                for n, (node_attrs, edge_attrs) in raw_edge_ann.items()])

    assert all([raw_edge_ann_direct['%%'.join(k)] == v
                for n, (node_attrs, edge_attrs) in raw_edge_ann.items()
                for k, v in edge_attrs.items()])

    # verify that annotator IDs are stored appropriately
    assert raw_node_ann.annotator_ids == {'annotator1', 'annotator2', 'annotator3'}
    assert raw_edge_ann.annotator_ids == {'annotator1', 'annotator2', 'annotator3'}

    # verify that annotators generator works
    for annotator_id in raw_node_ann.annotators():
        assert annotator_id in raw_node_ann.annotator_ids
    for annotator_id in raw_edge_ann.annotators():
        assert annotator_id in raw_edge_ann.annotator_ids

    # verify that items by annotator generator works
    for name, (node_attrs, edge_attrs) in raw_node_ann.items_for_annotator('annotator2'):
        assert name == 'tree1'
        assert json.dumps(node_attrs) == '{"tree1-semantics-pred-11": {"subspace": {"property": '\
                                            '{"confidence": 0.0, "value": 0.55}}}, '\
                                         '"tree1-semantics-pred-20": {"subspace": {"property": '\
                                         '{"confidence": 0.0, "value": 0.55}}}}'
        assert json.dumps(edge_attrs) == '{}'

    # verify that node attribute-only generator works
    for name, node_attrs in raw_node_ann.node_attrs_for_annotator('annotator2'):
        assert name == 'tree1'
        assert json.dumps(node_attrs) == '{"tree1-semantics-pred-11": {"subspace": {"property": '\
                                    '{"confidence": 0.0, "value": 0.55}}}, '\
                                 '"tree1-semantics-pred-20": {"subspace": {"property": '\
                                 '{"confidence": 0.0, "value": 0.55}}}}'

    # generator for edge attributes for the node attribute-only annotation
    # should yield empty results for the graph
    for name, edge_attrs in raw_node_ann.edge_attrs_for_annotator('annotator2'):
        assert len(edge_attrs) == 0

    # verify that edge attribute-only generator works
    for name, edge_attrs in raw_edge_ann.edge_attrs_for_annotator('annotator2'):
        assert name == 'tree1'
        assert json.dumps({n1 + '%%' + n2: anno for (n1, n2), anno in edge_attrs.items()}) == \
            '{"tree1-semantics-pred-11%%tree1-semantics-arg-15": {"subspace": {"property": '\
                    '{"confidence": 0.0, "value": 0.55}}}, '\
            '"tree1-semantics-pred-7%%tree1-semantics-arg-3": {"subspace": {"property": '\
                    '{"confidence": 0.0, "value": 0.55}}}}'

    # generator for node attributes for the edge attribute-only annotation
    # should yield empty results for the graph
    for name, node_attrs in raw_edge_ann.node_attrs_for_annotator('annotator2'):
        assert len(node_attrs) == 0

    
def test_normalized_uds_graph():
    graph = setup_graph(normalized=True)

    assert graph.sentence == graph_sentence
    assert graph.syntax_nodes == graph_syntax_nodes
    assert graph.semantics_nodes == graph_normalized_semantics_nodes
    assert graph.syntax_edges() == graph_syntax_edges
    assert graph.semantics_edges() == graph_normalized_semantics_edges
    
    assert graph.maxima() == ['tree1-semantics-pred-root']
    assert graph.minima() == ['tree1-syntax-1',
                              'tree1-syntax-2',
                              'tree1-syntax-4',
                              'tree1-syntax-5',
                              'tree1-syntax-8',
                              'tree1-syntax-9',
                              'tree1-syntax-10',
                              'tree1-syntax-12',
                              'tree1-syntax-14',
                              'tree1-syntax-16',
                              'tree1-syntax-17',
                              'tree1-syntax-18',
                              'tree1-syntax-19',
                              'tree1-syntax-21',
                              'tree1-syntax-22',
                              'tree1-syntax-24',
                              'tree1-syntax-25',
                              'tree1-syntax-27',
                              'tree1-syntax-29',
                              'tree1-semantics-arg-author',
                              'tree1-semantics-arg-addressee']

    noroot = [nid for nid in graph.nodes
              if nid != 'tree1-semantics-pred-root']
    assert graph.maxima(noroot) == ['tree1-semantics-arg-0',
                                    'tree1-semantics-arg-author',
                                    'tree1-semantics-arg-addressee']

    noperformative = [nid for nid in graph.nodes
                      if nid not in ['tree1-semantics-pred-root',
                                     'tree1-semantics-arg-0',
                                     'tree1-semantics-arg-author',
                                     'tree1-semantics-arg-addressee']]
    assert graph.maxima(noperformative) == ['tree1-root-0',
                                            'tree1-semantics-pred-7',
                                            'tree1-semantics-pred-20']


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

    assert graph.query(querystr, query_type='edge') == graph_query_results
    
    in_then_out = graph.from_dict(graph.to_dict(), 'tree1').to_dict()
    assert graph.to_dict() == in_then_out
    assert in_then_out == graph.from_dict(in_then_out, 'tree1').to_dict()

def test_raw_uds_graph():
    graph = setup_graph(normalized=False)

    assert graph.sentence == graph_sentence
    assert graph.syntax_nodes == graph_syntax_nodes
    assert graph.semantics_nodes == graph_raw_semantics_nodes
    assert graph.syntax_edges() == graph_syntax_edges
    assert graph.semantics_edges() == graph_raw_semantics_edges