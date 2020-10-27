import pytest

import os, json

from pprint import pprint

from decomp.semantics.uds.metadata import UDSAnnotationMetadata
from decomp.semantics.uds.annotation import UDSAnnotation
from decomp.semantics.uds.annotation import NormalizedUDSAnnotation
from decomp.semantics.uds.annotation import RawUDSAnnotation

class TestUDSAnnotation:

    def test_direct_instantiation_of_uds_annotation_fails(self):
        with pytest.raises(TypeError):
            UDSAnnotation(None)

class TestNormalizedUDSAnnotation:

    def test_from_json(self,
                       normalized_node_sentence_annotation,
                       normalized_edge_sentence_annotation,
                       normalized_sentence_annotations):
        norm_node_ann, norm_edge_ann = normalized_sentence_annotations
        norm_node_ann_direct = json.loads(normalized_node_sentence_annotation)
        norm_edge_ann_direct = json.loads(normalized_edge_sentence_annotation)

        assert norm_node_ann.metadata == UDSAnnotationMetadata.from_dict(norm_node_ann_direct['metadata'])
        assert norm_edge_ann.metadata == UDSAnnotationMetadata.from_dict(norm_edge_ann_direct['metadata'])

        assert all([not edge_attrs
                    for n, (node_attrs, edge_attrs) in norm_node_ann.items()])

        assert all([norm_node_ann_direct['data']['tree1'][k] == v
                    for n, (node_attrs, edge_attrs) in norm_node_ann.items()
                    for k, v in node_attrs.items()])

        assert all([not node_attrs
                    for n, (node_attrs, edge_attrs) in norm_edge_ann.items()])

        assert all([norm_edge_ann_direct['data']['tree1']['%%'.join(k)] == v
                    for n, (node_attrs, edge_attrs) in norm_edge_ann.items()
                    for k, v in edge_attrs.items()])

class TestRawUDSAnnotation:

    def test_from_json(self,
                       raw_node_sentence_annotation,
                       raw_edge_sentence_annotation,
                       raw_sentence_annotations):
        raw_node_ann, raw_edge_ann = raw_sentence_annotations
        raw_node_ann_direct = json.loads(raw_node_sentence_annotation)
        raw_edge_ann_direct = json.loads(raw_edge_sentence_annotation)

        assert raw_node_ann.metadata == UDSAnnotationMetadata.from_dict(raw_node_ann_direct['metadata'])
        assert raw_edge_ann.metadata == UDSAnnotationMetadata.from_dict(raw_edge_ann_direct['metadata'])

        assert all([not edge_attrs
                    for n, (node_attrs, edge_attrs) in raw_node_ann.items()])

        assert all([raw_node_ann_direct['data']['tree1'][k] == v
                    for n, (node_attrs, edge_attrs) in raw_node_ann.items()
                    for k, v in node_attrs.items()])

        assert all([not node_attrs
                    for n, (node_attrs, edge_attrs) in raw_edge_ann.items()])

        assert all([raw_edge_ann_direct['data']['tree1']['%%'.join(k)] == v
                    for n, (node_attrs, edge_attrs) in raw_edge_ann.items()
                    for k, v in edge_attrs.items()])


    def test_annotators(self, raw_sentence_annotations, test_data_dir):
        raw_node_ann, raw_edge_ann = raw_sentence_annotations

        with open(os.path.join(test_data_dir, 'raw_node_sentence_annotators.txt')) as f:
            assert raw_node_ann.annotators() == {line.strip() for line in f}

        with open(os.path.join(test_data_dir, 'raw_edge_sentence_annotators.txt')) as f:
            assert raw_edge_ann.annotators() == {line.strip() for line in f}

    def test_items(self, raw_sentence_annotations):
        raw_node_ann, raw_edge_ann = raw_sentence_annotations

        # verify that items by annotator generator works
        for gid, (node_attrs, edge_attrs) in raw_node_ann.items(annotator_id='genericity-pred-annotator-88'):
            assert gid == 'tree1'
            assert json.dumps(node_attrs) == '{"tree1-semantics-pred-7": {"genericity": {"pred-dynamic": {"confidence": 4, "value": 0}, "pred-hypothetical": {"confidence": 4, "value": 0}, "pred-particular": {"confidence": 4, "value": 0}}}, "tree1-semantics-pred-11": {"genericity": {"pred-dynamic": {"confidence": 4, "value": 0}, "pred-hypothetical": {"confidence": 4, "value": 0}, "pred-particular": {"confidence": 4, "value": 0}}}, "tree1-semantics-pred-20": {"genericity": {"pred-dynamic": {"confidence": 0, "value": 1}, "pred-hypothetical": {"confidence": 0, "value": 1}, "pred-particular": {"confidence": 0, "value": 1}}}}'
            assert json.dumps(edge_attrs) == '{}'

        # verify that node attribute-only generator works
        for gid, node_attrs in raw_node_ann.items(annotation_type="node",
                                                   annotator_id='genericity-pred-annotator-88'):
            assert gid == 'tree1'
            assert json.dumps(node_attrs) == '{"tree1-semantics-pred-7": {"genericity": {"pred-dynamic": {"confidence": 4, "value": 0}, "pred-hypothetical": {"confidence": 4, "value": 0}, "pred-particular": {"confidence": 4, "value": 0}}}, "tree1-semantics-pred-11": {"genericity": {"pred-dynamic": {"confidence": 4, "value": 0}, "pred-hypothetical": {"confidence": 4, "value": 0}, "pred-particular": {"confidence": 4, "value": 0}}}, "tree1-semantics-pred-20": {"genericity": {"pred-dynamic": {"confidence": 0, "value": 1}, "pred-hypothetical": {"confidence": 0, "value": 1}, "pred-particular": {"confidence": 0, "value": 1}}}}'

        # generator for edge attributes for the node attribute-only annotation
        # should yield empty results for the graph
        with pytest.raises(ValueError):
            for gid, edge_attrs in raw_node_ann.items(annotation_type="edge",
                                                      annotator_id='genericity-pred-annotator-88'):
                pass

        # verify that edge attribute-only generator works
        for gid, (node_attrs, edge_attrs) in raw_edge_ann.items(annotator_id='protoroles-annotator-14'):
            assert gid == 'tree1'
            assert json.dumps({'%%'.join(e): attrs for e, attrs in edge_attrs.items()}) == '{"tree1-semantics-pred-11%%tree1-semantics-arg-9": {"protoroles": {"awareness": {"confidence": 1, "value": 4}, "change_of_location": {"confidence": 1, "value": 4}, "change_of_possession": {"confidence": 1, "value": 4}, "change_of_state": {"confidence": 1, "value": 4}, "change_of_state_continuous": {"confidence": 1, "value": 4}, "existed_after": {"confidence": 1, "value": 4}, "existed_before": {"confidence": 1, "value": 4}, "existed_during": {"confidence": 1, "value": 4}, "instigation": {"confidence": 1, "value": 4}, "partitive": {"confidence": 1, "value": 4}, "sentient": {"confidence": 1, "value": 4}, "volition": {"confidence": 1, "value": 4}, "was_for_benefit": {"confidence": 1, "value": 4}, "was_used": {"confidence": 1, "value": 4}}}}'

        # generator for node attributes for the edge attribute-only annotation
        # should yield empty results for the graph
        with pytest.raises(ValueError):
            for gid, node_attrs in raw_edge_ann.items(annotation_type="node",
                                                      annotator_id='protoroles-annotator-14'):
                pass
