import json
import os
import shutil

import pytest

from decomp.semantics.uds import UDSSentenceGraph
from decomp.vis.uds_vis import UDSVisualization


# check if chromedriver is available
requires_chromedriver = pytest.mark.skipif(
    shutil.which("chromedriver") is None,
    reason="ChromeDriver executable not found in PATH"
)


@pytest.fixture
def basic_sentence_graph(test_data_dir):
    graph_data = json.load(open(os.path.join(test_data_dir, "vis_data.json")))
    graph = UDSSentenceGraph.from_dict(graph_data)
    return graph

@requires_chromedriver
def test_vis_basic(basic_sentence_graph, dash_duo):
    vis = UDSVisualization(basic_sentence_graph, add_syntax_edges=True)
    app = vis.serve(do_return = True)
    dash_duo.start_server(app)
    assert(dash_duo.find_element("title") is not None)

def test_vis_raw(raw_sentence_graph):
    with pytest.raises(AttributeError):
        vis = UDSVisualization(raw_sentence_graph, add_syntax_edges=True)
        vis.serve()
