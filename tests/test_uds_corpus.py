import os
import json
import pytest

from glob import glob
from pkg_resources import resource_filename
from decomp.semantics.uds import UDSCorpus


total_graphs = 16622
total_documents = 1174


data_dir = resource_filename('decomp', 'data/')


def _load_corpus(base, version, annotation_format):
    UDSCorpus.CACHE_DIR = base
    
    os.makedirs(os.path.join(base,
                             version,
                             annotation_format,
                             'sentence/'))
    os.makedirs(os.path.join(base,
                             version,
                             annotation_format,
                             'document/'))
    UDSCorpus(version=version,
              annotation_format=annotation_format)


class TestUDSCorpus:

    @pytest.mark.slow
    def test_load_v1_normalized(self, tmp_path):
        _load_corpus(tmp_path, '1.0', 'normalized')

    @pytest.mark.slow        
    def test_load_v2_normalized(self, tmp_path):
        _load_corpus(tmp_path, '2.0', 'normalized')

    @pytest.mark.slow        
    def test_load_v1_raw(self, tmp_path):
        _load_corpus(tmp_path, '1.0', 'raw')

    @pytest.mark.slow        
    def test_load_v2_raw(self, tmp_path):
        _load_corpus(tmp_path, '2.0', 'raw')

# def assert_correct_corpus_initialization(uds, raw):
#     # Assert all graphs and documents initialized
#     assert uds.ngraphs == total_graphs
#     assert uds.ndocuments == total_documents
#     n_sentence_graphs = 0
#     for doc_id in uds.documentids:
#         n_sentence_graphs += len(uds.documents[doc_id].sentence_graphs)
#     assert n_sentence_graphs == total_graphs

#     # Inspect a test document
#     test_doc = uds.documents[test_document_name]
#     assert test_doc.genre == test_document_genre
#     assert test_doc.timestamp == test_document_timestamp
#     assert test_doc.sentence_ids == test_document_sentence_ids
#     assert test_doc.text == test_document_text
#     assert test_doc.document_graph is not None

#     if raw:
#         assert uds.annotation_format == 'raw'
#         print(test_doc.semantics_node(test_document_node))
#         assert test_doc.semantics_node(test_document_node) == test_document_semantics_node_raw
#     else:
#         assert uds.annotation_format == 'normalized'
#         assert test_doc.semantics_node(test_document_node) == test_document_semantics_node_normalized

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

# @pytest.mark.slow
# def test_uds_corpus_load_v1_with_raw(data_dir):
#     _test_uds_corpus_load('1.0', raw=True, data_dir=data_dir)

# @pytest.mark.slow    
# def test_uds_corpus_load_v1_with_normalized(data_dir):
#     _test_uds_corpus_load('1.0', raw=False, data_dir=data_dir)

# @pytest.mark.slow    
# def test_uds_corpus_load_v2_with_raw(data_dir):
#     _test_uds_corpus_load('2.0', raw=True, data_dir=data_dir)

# @pytest.mark.slow
# def test_uds_corpus_load_v2_with_normalized(data_dir):
#     _test_uds_corpus_load('2.0', raw=False, data_dir=data_dir)
