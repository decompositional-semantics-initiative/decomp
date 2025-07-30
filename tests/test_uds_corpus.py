import importlib.resources
import logging
import os

import pytest

from decomp.semantics.uds import UDSCorpus


test_document_name = 'answers-20111105112131AA6gIX6_ans'
test_document_genre = 'answers'
test_document_timestamp = '20111105112131'
test_document_text = 'My dad just does n\'t understand ? Ugh my dad is so stupid ... he just does n\'t understand anything ! I have 5 sisters and so including my mom ... he is the only guy in a house of six females . Now I \'m the youngest and I just got my period so now we all have ours and he thinks it \'s a good thing ? He \'s always like " ohh you must be so happy to finally have yours , I wish I had mine ! " and he is n\'t even joking . I think just living in a house with so many girls is making him go crazy ? Yep , the females are just getting to him ... dads .. Do n\'t blame him please , he feels lonely and wants to show his attention to all of you to look after you , please forgive and sympathy if he miss something . I am sorry for him , he is a good dad'
test_document_sentence_ids = {'ewt-train-7189': 'answers-20111105112131AA6gIX6_ans-0001',
 'ewt-train-7190': 'answers-20111105112131AA6gIX6_ans-0002',
 'ewt-train-7191': 'answers-20111105112131AA6gIX6_ans-0003',
 'ewt-train-7192': 'answers-20111105112131AA6gIX6_ans-0004',
 'ewt-train-7193': 'answers-20111105112131AA6gIX6_ans-0005',
 'ewt-train-7194': 'answers-20111105112131AA6gIX6_ans-0006',
 'ewt-train-7195': 'answers-20111105112131AA6gIX6_ans-0007',
 'ewt-train-7196': 'answers-20111105112131AA6gIX6_ans-0008',
 'ewt-train-7197': 'answers-20111105112131AA6gIX6_ans-0009'}
test_document_node = 'ewt-train-7195-document-pred-7'
test_document_semantics_node_normalized = {'ewt-train-7195-semantics-pred-7': {'domain': 'semantics',
  'frompredpatt': True,
  'type': 'predicate',
  'factuality': {'factual': {'confidence': 1.0, 'value': 1.2225}},
  'time': {'dur-weeks': {'confidence': 0.3991, 'value': 0.7263},
   'dur-decades': {'confidence': 0.3991, 'value': -1.378},
   'dur-days': {'confidence': 0.3991, 'value': 0.7498},
   'dur-hours': {'confidence': 0.3991, 'value': -1.1733},
   'dur-seconds': {'confidence': 0.3991, 'value': -1.4243},
   'dur-forever': {'confidence': 0.3991, 'value': -1.2803},
   'dur-centuries': {'confidence': 0.3991, 'value': -1.1213},
   'dur-instant': {'confidence': 0.3991, 'value': -1.3219},
   'dur-years': {'confidence': 0.3991, 'value': -1.1953},
   'dur-minutes': {'confidence': 0.3991, 'value': 0.8558},
   'dur-months': {'confidence': 0.3991, 'value': 0.6852}},
  'genericity': {'pred-dynamic': {'confidence': 1.0, 'value': 1.1508},
   'pred-hypothetical': {'confidence': 1.0, 'value': -1.1583},
   'pred-particular': {'confidence': 1.0, 'value': 1.1508}}}}
test_document_semantics_node_raw = {'ewt-train-7195-semantics-pred-7': {'domain': 'semantics', 'frompredpatt': True, 'type': 'predicate', 'factuality': {'factual': {'value': {'factuality-annotator-26': 1, 'factuality-annotator-34': 1}, 'confidence': {'factuality-annotator-26': 4, 'factuality-annotator-34': 4}}}, 'time': {'duration': {'value': {'time-annotator-508': 4, 'time-annotator-619': 6, 'time-annotator-310': 5, 'time-annotator-172': 4, 'time-annotator-448': 5, 'time-annotator-548': 6}, 'confidence': {'time-annotator-508': 2, 'time-annotator-619': 4, 'time-annotator-310': 4, 'time-annotator-172': 4, 'time-annotator-448': 1, 'time-annotator-548': 2}}}, 'genericity': {'pred-dynamic': {'value': {'genericity-pred-annotator-277': 0}, 'confidence': {'genericity-pred-annotator-277': 2}}, 'pred-hypothetical': {'value': {'genericity-pred-annotator-277': 0}, 'confidence': {'genericity-pred-annotator-277': 2}}, 'pred-particular': {'value': {'genericity-pred-annotator-277': 0}, 'confidence': {'genericity-pred-annotator-277': 2}}}}}


total_graphs = 16622
total_documents = 1174


data_dir = str(importlib.resources.files('decomp') / 'data')


def _load_corpus(base, version, annotation_format):
    UDSCorpus.CACHE_DIR = base

    try:
        os.makedirs(os.path.join(base,
                                 version,
                                 annotation_format,
                                 'sentence/'))
        os.makedirs(os.path.join(base,
                                 version,
                                 annotation_format,
                                 'document/'))

    except FileExistsError:
        pass

    return UDSCorpus(version=version,
                     annotation_format=annotation_format)

def _assert_correct_corpus_initialization(uds, raw):
    # Assert all graphs and documents initialized
    assert uds.ngraphs == total_graphs
    assert uds.ndocuments == total_documents

    n_sentence_graphs = 0

    for doc_id in uds.documentids:
        n_sentence_graphs += len(uds.documents[doc_id].sentence_graphs)

    assert n_sentence_graphs == total_graphs

    # Inspect a test document
    test_doc = uds.documents[test_document_name]
    assert test_doc.genre == test_document_genre
    assert test_doc.timestamp == test_document_timestamp
    assert test_doc.sentence_ids == test_document_sentence_ids
    assert test_doc.text == test_document_text
    assert test_doc.document_graph is not None

    print(test_doc.semantics_node(test_document_node))

    if raw:
        assert uds.annotation_format == 'raw'
        #assert test_doc.semantics_node(test_document_node) == test_document_semantics_node_raw
    else:
        assert uds.annotation_format == 'normalized'
        #assert test_doc.semantics_node(test_document_node) == test_document_semantics_node_normalized

def _assert_document_annotation(uds, raw):
    if raw:
        node_ann, edge_ann = setup_raw_document_annotations()
    else:
        node_ann, edge_ann = setup_normalized_document_annotations()

    document = list(node_ann.node_attributes.keys())[0]

    # assert node annotations
    node_ann_attrs = dict(list(node_ann.node_attributes.values())[0])

    for doc_node, node_annotation in node_ann_attrs.items():
        for k, v in node_annotation.items():
            assert uds.documents[document].document_graph.nodes[doc_node][k] == v

    # assert edge annotations
    edge_ann_attrs = dict(list(edge_ann.edge_attributes.values())[0])

    for doc_edge, edge_annotation in edge_ann_attrs.items():
        for k, v in edge_annotation.items():
            assert uds.documents[document].document_graph.edges[doc_edge][k] == v

class TestUDSCorpus:

    # @pytest.mark.slow
    # def test_load_v1_normalized(self, tmp_path, caplog):
    #     caplog.set_level(logging.WARNING)

    #     uds = _load_corpus(tmp_path, '1.0', 'normalized')

    #     raw = False

    #     _assert_correct_corpus_initialization(uds, raw)
    #     #_assert_document_annotation(uds, raw)

    #     # reload the UDSCorpus, which will initialize it from
    #     # the now-serialized graphs
    #     uds_cached = _load_corpus(tmp_path, '1.0', 'normalized')

    #     _assert_correct_corpus_initialization(uds_cached, raw)
    #     #_assert_document_annotation(uds_cached, raw)


    # @pytest.mark.slow
    # def test_load_v2_normalized(self, tmp_path, caplog):
    #     caplog.set_level(logging.WARNING)

    #     uds = _load_corpus(tmp_path, '2.0', 'normalized')

    #     raw = False

    #     _assert_correct_corpus_initialization(uds, raw)
    #     #_assert_document_annotation(uds, raw)

    #     # reload the UDSCorpus, which will initialize it from
    #     # the now-serialized graphs
    #     uds_cached = _load_corpus(tmp_path, '2.0', 'normalized')

    #     _assert_correct_corpus_initialization(uds_cached, raw)
    #     #_assert_document_annotation(uds_cached, raw)

    # @pytest.mark.slow
    # def test_load_v1_raw(self, tmp_path, caplog):
    #     caplog.set_level(logging.WARNING)

    #     uds = _load_corpus(tmp_path, '1.0', 'raw')

    #     raw = True

    #     _assert_correct_corpus_initialization(uds, raw)
    #     #_assert_document_annotation(uds, raw)

    #     # reload the UDSCorpus, which will initialize it from
    #     # the now-serialized graphs
    #     uds_cached = _load_corpus(tmp_path, '1.0', 'raw')

    #     _assert_correct_corpus_initialization(uds_cached, raw)
    #     #_assert_document_annotation(uds_cached, raw)

    @pytest.mark.slow
    def test_load_v2_raw(self, tmp_path, caplog):
        caplog.set_level(logging.WARNING)

        uds = _load_corpus(tmp_path, '2.0', 'raw')

        raw = True

        #print(uds.metadata.to_dict())

        print(uds._sentences_paths)
        print(uds._documents_paths)
        _assert_correct_corpus_initialization(uds, raw)
        #_assert_document_annotation(uds, raw)

        # reload the UDSCorpus, which will initialize it from
        # the now-serialized graphs
        uds_cached = _load_corpus(tmp_path, '2.0', 'raw')

        print()
        #print(uds_cached.metadata.to_dict())

        _assert_correct_corpus_initialization(uds_cached, raw)
        #_assert_document_annotation(uds_cached, raw)

# def _test_uds_corpus_load(version, raw, data_dir):
#     # Remove cached graphs
#     if raw:
#         annotation_format = 'raw'
#     else:
#         annotation_format = 'normalized'

#     sentence_path = os.path.join(data_dir, version, annotation_format, 'sentence')
#     doc_path = os.path.join(data_dir, version, annotation_format, 'document')

#     if glob(os.path.join(sentence_path, '*.json')):
#         os.system('rm ' + sentence_path + '/*.json')

#     if glob(os.path.join(doc_path, '*.json')):
#         os.system('rm ' + doc_path + '/*.json')


#     annotations_dir = os.path.join(doc_path, 'annotations')
#     if not glob(annotations_dir):
#         os.system('mkdir ' + annotations_dir)
#     if raw:
#         # Dump the test anontations to JSON files
#         raw_node_ann = json.loads(raw_node_document_annotation)
#         raw_edge_ann = json.loads(raw_edge_document_annotation)
#         raw_node_ann_path = os.path.join(annotations_dir, 'raw_node.json')
#         raw_edge_ann_path = os.path.join(annotations_dir, 'raw_edge.json')
#         annotations = [raw_node_ann, raw_edge_ann]
#         paths = [raw_node_ann_path, raw_edge_ann_path]
#     else:
#         norm_node_ann = json.loads(normalized_node_document_annotation)
#         norm_edge_ann = json.loads(normalized_edge_document_annotation)
#         norm_node_ann_path = os.path.join(annotations_dir, 'norm_node.json')
#         norm_edge_ann_path = os.path.join(annotations_dir, 'norm_edge.json')
#         annotations = [norm_node_ann, norm_edge_ann]
#         paths = [norm_node_ann_path, norm_edge_ann_path]


#     for ann, path in zip(annotations, paths):
#         os.system('touch ' + path)
#         with open(path, 'w') as out:
#             json.dump(ann, out)

#     # Load the UDSCorpus without any options
#     uds = UDSCorpus(version=version, annotation_format=annotation_format)
#     assert_correct_corpus_initialization(uds, raw)
#     assert_document_annotation(uds, raw)

#     # Reload the UDSCorpus, which will initialize it from
#     # the now-serialized graphs
#     uds_cached = UDSCorpus(version=version, annotation_format=annotation_format)
#     assert_correct_corpus_initialization(uds_cached, raw)
#     assert_document_annotation(uds, raw)

#     # Remove the cached graphs and annotations
#     os.system('rm ' + sentence_path + '/*.json')
#     os.system('rm ' + doc_path + '/*.json')
#     for path in paths:
#         os.system('rm ' + path)
