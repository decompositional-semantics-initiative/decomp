import os

import pytest

from decomp.semantics.uds.annotation import NormalizedUDSAnnotation, RawUDSAnnotation


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )

def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )

def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return

    skip_slow = pytest.mark.skip(reason="need --runslow option to run")

    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)

@pytest.fixture
def test_dir():
    return os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def test_data_dir(test_dir):
    return os.path.join(test_dir, 'data/')


@pytest.fixture
def normalized_node_sentence_annotation(test_data_dir):
    fpath = os.path.join(test_data_dir, 'normalized_node_sentence_annotation.json')

    with open(fpath) as f:
        return f.read()

@pytest.fixture
def normalized_edge_sentence_annotation(test_data_dir):
    fpath = os.path.join(test_data_dir, 'normalized_edge_sentence_annotation.json')

    with open(fpath) as f:
        return f.read()

@pytest.fixture
def normalized_sentence_annotations(normalized_node_sentence_annotation,
                                    normalized_edge_sentence_annotation):
    norm_node_ann = NormalizedUDSAnnotation.from_json(normalized_node_sentence_annotation)
    norm_edge_ann = NormalizedUDSAnnotation.from_json(normalized_edge_sentence_annotation)

    return norm_node_ann, norm_edge_ann

@pytest.fixture
def raw_node_sentence_annotation(test_data_dir):
    fpath = os.path.join(test_data_dir, 'raw_node_sentence_annotation.json')

    with open(fpath) as f:
        return f.read()

@pytest.fixture
def raw_edge_sentence_annotation(test_data_dir):
    fpath = os.path.join(test_data_dir, 'raw_edge_sentence_annotation.json')

    with open(fpath) as f:
        return f.read()

@pytest.fixture
def raw_sentence_annotations(raw_node_sentence_annotation,
                             raw_edge_sentence_annotation):
    raw_node_ann = RawUDSAnnotation.from_json(raw_node_sentence_annotation)
    raw_edge_ann = RawUDSAnnotation.from_json(raw_edge_sentence_annotation)

    return raw_node_ann, raw_edge_ann
