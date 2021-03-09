import json
import os 
from predpatt import PredPatt, PredPattOpts, load_conllu
from decomp.syntax.dependency import DependencyGraphBuilder
from decomp.semantics.predpatt import PredPattGraphBuilder
from decomp.semantics.uds import UDSSentenceGraph, UDSCorpus
from decomp.vis.uds_vis import UDSVisualization
from decomp import NormalizedUDSAnnotation
import pdb 

from test_uds_graph import raw_sentence_graph, rawtree, listtree
import pytest
import dash 
from dash.testing.application_runners import import_app


@pytest.fixture
def basic_sentence_graph(test_data_dir):
    graph_data = json.load(open(os.path.join(test_data_dir, "vis_data.json")))
    graph = UDSSentenceGraph.from_dict(graph_data)
    return graph

def test_vis_basic(basic_sentence_graph, dash_duo):
    vis = UDSVisualization(basic_sentence_graph, add_syntax_edges=True)
    app = vis.serve(do_return = True)
    dash_duo.start_server(app)
    assert(dash_duo.find_element("title") is not None)

def test_vis_raw(raw_sentence_graph):
    with pytest.raises(AttributeError):
        vis = UDSVisualization(raw_sentence_graph, add_syntax_edges=True)
        vis.serve()
