from typing import Any, cast

import dash
import jsonpickle
import matplotlib
import numpy as np
import plotly.graph_objs as go
from dash import dcc, html

from ..semantics.uds import UDSCorpus, UDSSentenceGraph


def get_ontologies() -> tuple[list[str], list[str]]:
    """
    Collect node and edge ontologies from existing UDS corpus 
    """
    corpus = UDSCorpus(split="dev")
    metadata = corpus.metadata.sentence_metadata.metadata
    node_ontology = [f"{k}-{v_val}" for k,v in metadata.items() for v_val in v.keys() if k != "protoroles"]
    edge_ontology = [f"{k}-{v_val}" for k,v in metadata.items() for v_val in v.keys() if k == "protoroles"]

    return node_ontology, edge_ontology


class StringList:
    """
    Wrapper class for indexing into text,
    which is needed for ordering nodes when
    parsing from a new sentence in API mode.

    Parameters
    ----------
    text
        input sentence 
    """

    def __init__(self, text: str):
        self.text_list = text.split(" ")

    def index(self, item: str) -> int:
        try:
            return self.text_list.index(item)
        except ValueError:
            return 1000

    def __str__(self) -> str:
        return " ".join(self.text_list)


class UDSVisualization:
    """A toolkit for serving Dash-based visualizations
    of UDSSentenceGraphs in the browser.

    Parameters
    ----------
    graph
        the UDSSentenceGraph instance to visualize
    add_span_edges
        whether to add edges from semantic nodes to the syntactic nodes 
        included in their spans
    add_syntax_edges
        whether to add UD edges between syntactic nodes 
    from_prediction
        flag which indicates whether UDSSentenceGraph instance was generated
        by a parser when true
    sentence
        input sentence, provided when using predicted graph 
    syntax_y
        height of syntax nodes 
    semantics_y
        height of semantics nodes
    node_offset
        separation between semantics nodes 
    width
        visualization width
    height 
        visualization height 
    """

    def __init__(self,
                 graph: UDSSentenceGraph,
                 add_span_edges: bool = True,
                 add_syntax_edges: bool = False,
                 from_prediction: bool = False,
                 sentence: str | None = None,
                 syntax_y: float = 0.0,
                 semantics_y: float = 10.0,
                 node_offset: float = 7.0,
                 width: float = 1000,
                 height: float = 400):

        if graph is None:
            graph = UDSCorpus(split="dev")['ewt-dev-1']  # type: ignore[unreachable]
            sentence = str(sentence)

        self.graph = graph

        self.from_prediction = from_prediction
        self.sentence = StringList(sentence) if sentence is not None else None

        self.width = width
        self.height = height
        self.syntax_y = 0.0
        self.semantics_y = height/10

        # dynamically compute all sizes based on width and height
        self.syntax_marker_size = 15
        self.semantics_marker_size = 40
        self.node_offset = width/len(self.graph.syntax_subgraph)
        self.arrow_len = width/200

        self.do_shorten = True if len(self.graph.syntax_subgraph) > 12 else False

        self.shapes: list[dict[str, Any]] = []
        self.trace_list: list[go.Scatter] = []
        self.node_to_xy: dict[str, tuple[float, float]] = {}

        self.added_edges: list[tuple[str, str]] = []
        self.add_span_edges = add_span_edges
        self.add_syntax_edges = add_syntax_edges

        self.node_ontology_orig, self.edge_ontology_orig = get_ontologies()
        self.node_ontology = [x for x in self.node_ontology_orig]
        self.edge_ontology = [x for x in self.edge_ontology_orig]

    def _format_line(self, start: tuple[float, float], end: tuple[float, float], radius: float | None = None) -> tuple[Any, Any, Any]:
        # format a line between dependents
        if start == end:
            return None, None, None

        x0, y0 = start
        x1, y1 = end
        if x0 > x1:
            x1, x0 = x0, x1
            y1, y0 = y0, y1
        offset = x1-x0

        height_factor = 1/(4*offset)
        x_range = np.linspace(x0, x1, num=100)

        different = y1 != y0

        if different:
            if y0 < y1 and x0 < x1:
                x1_root = 4*(y1 - y0) + x1
                y_range = -height_factor * (x_range - x0) * (x_range-x1_root) + y0
            elif y0 > y1 and x0 < x1:
                x0_root = -4*(y0-y1) + x0
                y_range = -height_factor * (x_range - x0_root) * (x_range-x1) + y1
            else:
                raise ValueError
        else:
            y_range = -height_factor * (x_range - x0)*(x_range - x1) + y0

        # find out what's on the radius of x0, y0
        # x^2 + y^2 = r^2
        zeroed_x_range = x_range - x0
        zeroed_y_range = y_range - y0
        sum_range = zeroed_x_range**2 + zeroed_y_range**2
        x_range_true: list[float] = []
        y_range_true: list[float] = []
        y_range_true

        for i in range(len(x_range)):
            if radius is not None and x_range[i] > np.sqrt(radius/2):
                x_range_true.append(x_range[i])
                y_range_true.append(y_range[i])

        x_range = [None] + x_range.tolist() + [None]
        y_range = [None] + y_range.tolist() + [None]
        return x_range, y_range, np.max(y_range[1:-1])

    def _add_arrowhead(self, point: tuple[float, float], root0: float, root1: float, direction: str, color: str = "black", width: float = 0.1) -> None:
        # get tangent line at point
        x,y = point
        if direction in ["left", "right"]:
            derivative = 1/(4*(root1-root0)) * (2*x - root0 - root1)
            theta_rad = np.arctan(derivative)
        else:
            # downward at a slope
            if x != root0:
                derivative = (y-root1)/(x-root0)
                theta_rad = 3.14 - np.arctan(derivative)
            else:
                theta_rad = 3.14/2

        l = self.arrow_len
        x0 = x
        y0 = y
        x1 = x - l
        x2 = x - l
        y1 = y + width*l
        y2 = y - width*l

        # put at origin
        vertices: list[list[float]] = [[0, 0], [x1-x0, y1-y0], [x2-x0, y2-y0], [0,0]]

        width = 1
        if direction in ["left"]:
            arrowhead_transformation = (matplotlib.transforms.Affine2D()
                                        .rotate_around(0,0,theta_rad)
                                        .rotate_around(0,0,3.14)
                                        .translate(x0, y0)
                                        .frozen())
        elif direction in ["down-right"]:
            arrowhead_transformation = (matplotlib.transforms.Affine2D()
                                        .rotate_around(0,0,3.14-theta_rad)
                                        .translate(x0, y0)
                                        .frozen())
        else:
            arrowhead_transformation = (matplotlib.transforms.Affine2D()
                                        .rotate_around(0,0,-theta_rad)
                                        .translate(x0, y0)
                                        .frozen())


        vertices_prime = [arrowhead_transformation.transform_point((float(x), float(y))) for (x, y) in vertices]
        x0_prime, y0_prime = vertices_prime[0]
        x1_prime, y1_prime = vertices_prime[1]
        x2_prime, y2_prime = vertices_prime[2]

        arrow = go.Scatter(x=[x0_prime , x1_prime , x2_prime , x0_prime ],
                           y=[y0_prime , y1_prime , y2_prime , y0_prime ],
                           hoverinfo='skip',
                           mode='lines',
                           fill='toself',
                           line={'width': 0.5, "color":color},
                           fillcolor=color,
                          )

        self.trace_list.append(arrow)

    def _get_attribute_str(self, node: str | tuple[str, str], is_node:bool=True) -> str:
        # format attribute string for hovering
        to_ret_list: list[str] = []
        pairs = []
        lens = []
        if is_node:
            onto = self.node_ontology
            choose_from = self.graph.nodes
        else:
            onto = self.edge_ontology
            choose_from = self.graph.edges  # type: ignore[assignment]

        for attr in onto:
            try:
                split_attr = attr.split("-")
                attr_type = split_attr[0]
                attr_subtype = "-".join(split_attr[1:])
                val = choose_from[node][attr_type][attr_subtype]["value"]  # type: ignore[index]
            except KeyError:
                continue
            try:
                val = np.round(val, 2)
            except (TypeError, AttributeError):
                assert(type(val) == dict)
                raise AttributeError("Only normalized annotations are supported for visualization")

            pairs.append((attr, val))

            lens.append(len(attr) + len(str(val)) + 2)

        if len(lens) > 0:
            max_len = max(lens)
            for i, (attr, val) in enumerate(pairs):
                # don't try to display more than 20 at once
                if i > 15:
                    to_ret_list.append("...")
                    break
                line_len = lens[i]
                n_spaces = max_len - line_len
                to_ret_list.append(f"{attr}: {val}")

        to_ret_str = "<br>".join(to_ret_list)
        if is_node and isinstance(node, str):
            to_ret_str = f"<b>{node}</b> <br> {to_ret_str}"

        return to_ret_str

    def _get_xy_from_edge(self, node_0: str, node_1: str) -> tuple[float, float, float, float] | None:
        # get the (x,y) coordinates of the endpoints of an edge
        try:
            x0,y0 = self.node_to_xy[node_0]
            x1,y1 = self.node_to_xy[node_1]
            return (x0, y0, x1, y1)
        except KeyError:
            # addresse, root, speaker nodes
            return None

    def _select_direction(self, x0: float, x1: float) -> str:
        # determine which way an arrowhead should face
        if x0 == x1:
            return "down"
        if x0 < x1:
            return "down-right"
        else:
            return "down-left"

    def _make_label_node(self, x: Any, y: Any, hovertext: Any, text: Any, marker: dict[str, Any] | None = None) -> go.Scatter:
        # make invisible nodes that hold labels
        if marker is None:
            marker = {'size': 20, 'color': "LightGrey",
                       'opacity': 1.0}
        text_node_trace = go.Scatter(x=x, y=y,
                                     hovertext=hovertext,
                                     text=text,
                                     mode='markers+text',
                                     textposition="top center",
                                     hoverinfo="text",
                                     marker = marker)
        return text_node_trace

    def _get_prediction_node_head(self, node_0: str) -> str | None:
        # different function needed for dealing with MISO predicted graphs
        outgoing_edges = [e for e in self.graph.edges if e[0] == node_0]
        try:
            head_edges = [e for e in outgoing_edges if self.graph.edges[e]['semrel'] == "head"]
        except KeyError:
            return None

        if len(head_edges) != 1:
            return None

        head_edge = head_edges[0]
        node_1 = str(head_edge[1])
        return node_1

    def _add_syntax_nodes(self) -> None:
        syntax_layer = self.graph.syntax_subgraph
        syntax_node_trace = go.Scatter(x=[], y=[],hovertext=[], text=[],
                                        mode='markers+text', textposition="bottom center",
                                        hoverinfo="text",
                                        marker={'size': self.syntax_marker_size,
                                                'sizemin': self.syntax_marker_size,
                                                'sizeref': self.syntax_marker_size,
                                                "color":'#9166d1',
                                                "line": dict(width=0.5,
                                                          color="black")
                                               }
                                      )

        if self.from_prediction:
            if self.sentence is not None:
                nodes_and_idxs = []
                for node in syntax_layer.nodes:
                    if "form" in self.graph.nodes[node].keys():
                        key = "form"
                    else:
                        key = "text"
                    try:
                        text = syntax_layer.nodes[node][key]
                    except KeyError:
                        text = ""
                    idx = self.sentence.index(text)
                    nodes_and_idxs.append((node, idx))
                sorted_nodes = sorted(nodes_and_idxs, key = lambda x: x[1])
                syntax_iterator = [x[0] for x in sorted_nodes]
            else:
                syntax_iterator = sorted(syntax_layer.nodes, key = lambda x: int(str(x).split('-')[1]))
        else:
            syntax_iterator = list(syntax_layer.nodes)

        for i, node in enumerate(syntax_iterator):
            if "form" in self.graph.nodes[node].keys():
                key = "form"
            else:
                key = "text"

            if self.graph.nodes[node][key] == "@@ROOT@@":
                continue

            if not self.from_prediction:
                node_idx = int(node.split("-")[-1])
            else:
                node_idx = i
            syntax_node_trace['x'] += tuple([node_idx * self.node_offset])
            # alternate heights
            y = self.syntax_y + i%2*0.5
            syntax_node_trace['y'] += tuple([y])
            self.node_to_xy[node] = (node_idx * self.node_offset, y)



            syntax_node_trace['hovertext'] += tuple([self.graph.nodes[node][key]])
            if self.do_shorten:
                syntax_node_trace['text'] += tuple([self.graph.nodes[node][key][0:3]])
            else:
                syntax_node_trace['text'] += tuple([self.graph.nodes[node][key]])

            x=node_idx * self.node_offset

        self.trace_list.append(syntax_node_trace)

    def _add_semantics_nodes(self) -> None:
        semantics_layer = self.graph.semantics_subgraph

        semantics_data: dict[str, dict[str, dict[str, list[Any]]]] = {
            "large": {"pred": {"x": [], "y": [], "hovertext": [], "text": []},
                     "arg": {"x": [], "y": [], "hovertext": [], "text": []}},
            "small": {"pred": {"x": [], "y": [], "hovertext": [], "text": []},
                     "arg": {"x": [], "y": [], "hovertext": [], "text": []}}}

        taken: list[float] = []
        next_increment = 0
        for i, node in enumerate(semantics_layer):
            attr_str = self._get_attribute_str(node, is_node=True)

            if len(attr_str.split("<br>")) > 2:
                size_key = "large"
            else:
                size_key = "small"

            node_type = self.graph.nodes[node]['type']
            if not self.from_prediction:
                try:
                    node_idx, __ = self.graph.head(node)
                except (ValueError, KeyError, IndexError):
                    # addressee, root, speaker nodes
                    if ("root" not in node and
                        "speaker" not in node and
                        "author" not in node and
                        "addressee" not in node):
                        # arg node
                        try:
                            node_idx = int(node.split("-")[-1])
                        except ValueError:
                            node_idx = i
                    else:
                        continue
                if not node.startswith("tree"):
                    node_name = "-".join(node.split("-")[0:3])
                else:
                    node_name = node.split("-")[0]
                node_1 = f"{node_name}-syntax-{node_idx}"
                if node_idx > 0:
                    head_text = self.graph.nodes[node_1]['form']
                else:
                    head_text = "root"
            else:
                head_synt_node = self._get_prediction_node_head(node)
                # add root nodes
                if node == "-semantics-arg-0":
                    head_synt_node = "root"

                if head_synt_node is None:
                    continue
                else:
                    if head_synt_node == "root":
                        node_idx = 0
                    else:
                        if self.sentence is not None:
                            node_idx = self.sentence.index(self.graph.nodes[head_synt_node]['form'])
                        else:
                            node_idx = 0
                        if node_idx == 1000:
                            node_idx = -2
                if head_synt_node == "root":
                    head_text = "root"
                else:
                    head_text = self.graph.nodes[head_synt_node]['form']

            head_text = "root" if head_text == "@@ROOT@@" else head_text

            if node_type == "argument":
                arg_key = "arg"
            else:
                arg_key = "pred"

            x_pos = node_idx * self.node_offset
            if x_pos in taken:
                next_increment = 25
            x_pos += next_increment

            semantics_data[size_key][arg_key]['x'] += tuple([x_pos])
            semantics_data[size_key][arg_key]['y'] += tuple([self.semantics_y])
            semantics_data[size_key][arg_key]['text'] += tuple([head_text[0:3]])
            semantics_data[size_key][arg_key]['hovertext'] += tuple([attr_str])
            self.node_to_xy[node] = (x_pos, self.semantics_y)

            taken.append(x_pos)
            next_increment = 0

        size_prefs = {"large": 4,
                            "small": 2}
        color_prefs = {"pred": '#ee5b76',
                       "arg": '#1f7ecd'}

        for size in semantics_data:
            pred_and_arg = semantics_data[size]
            for p_or_a in pred_and_arg.keys():
                trace_data = pred_and_arg[p_or_a]

                semantics_node_trace = go.Scatter(x=trace_data['x'], y=trace_data['y'],
                                                       mode='markers+text',
                                                       textposition="top center",
                                                       hoverinfo="skip",
                                                       marker={'size': 20, 'color': color_prefs[p_or_a],
                                                                "line":dict(color="black",
                                                                            width=size_prefs[size])
                                                              }
                                                      )

                text_node_trace = self._make_label_node(trace_data['x'], trace_data['y'],
                                                        trace_data['hovertext'], trace_data['text'])
                self.trace_list.append(text_node_trace)
                self.trace_list.append(semantics_node_trace)

    def _add_syntax_edges(self) -> None:
        for (node_0, node_1) in self.graph.syntax_subgraph.edges:
            # swap order
            result = self._get_xy_from_edge(node_1, node_0)
            if result is None:
                continue
            x0,y0,x1,y1 = result
            x_range, y_range, height = self._format_line((x0,y0), (x1,y1), radius = self.syntax_marker_size)
            if x_range is None:
                continue

            edge_trace = go.Scatter(x=tuple(x_range), y=tuple(y_range),
                                   hoverinfo='skip',
                                   mode='lines',
                                   line={'width': 0.5},
                                   marker=dict(color='blue'),
                                   line_shape='spline',
                                   opacity=1)
            self.trace_list.append(edge_trace)
            if x1 > x0:
                direction = "right"
            else:
                direction = "left"

            self._add_arrowhead((x1,y1), x0, x1, direction, color="blue")

    def _add_semantics_edges(self) -> None:
        for (node_0, node_1) in self.graph.semantics_subgraph.edges:
            if "speaker" in node_0 or "speaker" in node_1 or "addressee" in node_0 or "addressee" in node_1:
                continue
            result = self._get_xy_from_edge(node_0, node_1)
            if result is None:
                continue
            x0,y0,x1,y1 = result

            # add a curve above for all semantic relations
            x_range, y_range, height = self._format_line((x0,y0), (x1,y1), radius = self.semantics_marker_size)
            if x_range is None:
                continue

            edge_trace = go.Scatter(x=tuple(x_range), y=tuple(y_range),
                                   hoverinfo='skip',
                                   mode='lines',
                                   line={'width': 1},
                                   marker=dict(color='black'),
                                   line_shape='spline',
                                   opacity=1)

            x_mid = x_range[int(len(x_range)/2)]

            attributes = self._get_attribute_str((node_0, node_1), is_node=False)
            if len(attributes) > 0:
                midpoint_trace = go.Scatter(x=tuple([x_mid]), y=tuple([height]),
                                            hoverinfo="skip",
                                            mode='markers+text',
                                            textposition="top center",
                                            marker={'symbol': 'square', 'size': 15,
                                                    'color': '#e1aa21',
                                                    'line':dict(width=2, color='black'),
                                                    'opacity':1
                                                   }
                                           )

                marker={'symbol': 'square', 'size': 15, 'color': 'LightGrey'}
                mid_text_trace = self._make_label_node([x_mid], [height], attributes, "", marker)
                self.trace_list.append(mid_text_trace)
                self.trace_list.append(midpoint_trace)
            self.trace_list.append(edge_trace)

            if x1 < x0:
                direction = "left"
            else:
                direction = "right"

            self._add_arrowhead((x1,y1), x0, x1, direction, width=0.2)

    def _add_head_edges(self) -> None:
        semantics_layer = self.graph.semantics_subgraph
        for node_0 in semantics_layer:
            try:
                if not self.from_prediction:
                    node_idx, __ = self.graph.head(node_0)
                    node_name = "-".join(node_0.split("-")[0:3])
                    node_1 = f"{node_name}-syntax-{node_idx}"
                else:
                    pred_head = self._get_prediction_node_head(node_0)
                    if pred_head is None:
                        continue
                    node_1 = pred_head

                key="text"
                if "form" in self.graph.nodes[node_1].keys():
                    key = "form"
                if self.graph.nodes[node_1][key] == "@@ROOT@@":
                    continue

                result = self._get_xy_from_edge(node_0, node_1)
                if result is None:
                    continue
                x0,y0,x1,y1 = result
            except (ValueError, KeyError, IndexError):
                continue

            edge_trace = go.Scatter(x=tuple([x0, x1]), y=tuple([y0,y1]),
                                   hoverinfo='skip',
                                   mode='lines',
                                   line={'width': 3},
                                   marker=dict(color='grey'),
                                   line_shape='spline',
                                   opacity=1)

            self.trace_list.append(edge_trace)

            point = (x1, y1)
            direction = self._select_direction(x0, x1)

            self._add_arrowhead(point, x0, y0, direction, color="grey", width=0.5)

            self.added_edges.append((node_0, node_1))

    def _add_span_edges(self) -> None:
        for (node_0, node_1) in self.graph.instance_edges():
            if (node_0, node_1) not in self.added_edges:
                # skip arg-pred edges
                if self.graph.edges[(node_0, node_1)]['type'] != "nonhead":
                    continue
                try:
                    result = self._get_xy_from_edge(node_0, node_1)
                    if result is None:
                        continue
                    x0,y0,x1,y1 = result
                except (KeyError, IndexError):
                    continue

                edge_trace = go.Scatter(x=tuple([x0, x1]), y=tuple([y0,y1]),
                                   hoverinfo='skip',
                                   mode='lines',
                                   line={'width': 1},
                                   marker=dict(color='grey'),
                                   line_shape='spline',
                                   opacity=1)

                self.trace_list.append(edge_trace)

                point = (x1, y1)
                direction = self._select_direction(x0, x1)

                self._add_arrowhead(point, x0, y0, direction, color="grey")


    def prepare_graph(self) -> dict:
        """Converts a UDS graph into a Dash-ready layout"""
        # clear
        self.trace_list = []
        # redo
        self._add_semantics_nodes()
        self._add_semantics_edges()

        self._add_syntax_nodes()
        if self.add_syntax_edges:
            self._add_syntax_edges()

        self._add_head_edges()
        if self.add_span_edges:
            self._add_span_edges()

        figure = {
                "data": self.trace_list,
                "layout": go.Layout(title=self.graph.name, showlegend=False,
                                    margin={'b': 40, 'l': 0, 'r': 0, 't': 40},
                                    xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                    yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                    width=self.width,
                                    height=self.height,
                                    shapes=self.shapes,
                                    hovermode='closest'),
                }

        return figure

    def _get_uds_subspaces(self) -> list[dict[str, str]]:
        types_set = set()
        for prop in self.node_ontology_orig + self.edge_ontology_orig:
            types_set |= set([prop.split("-")[0]])
        types = sorted(list(types_set))
        to_ret = []
        for t in types:
            to_ret.append({"label": t, "value": t})
        return to_ret

    def _update_ontology(self, subspaces: list[str]) -> None:
        self.node_ontology = [x for x in self.node_ontology_orig if x.split("-")[0] in subspaces]
        self.edge_ontology = [x for x in self.edge_ontology_orig if x.split("-")[0] in subspaces]

    def serve(self, do_return: bool = False) -> dash.Dash | None:
        """Serve graph to locally-hosted site to port 8050 with no parser"""
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        print(f"name is {__name__}")
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        app.title = self.graph.name
        app.layout = html.Div([
            html.Div(className="row",
                  children=[
                      html.Div(className="twelve columns",
                               children = [
                                   html.Div(className="four columns",
                                            children=[
                                                dcc.Checklist(id="subspace-list",
                                                                    options=self._get_uds_subspaces(),  # type: ignore[arg-type]
                                                              value=[x['label'] for x in self._get_uds_subspaces()],
                                                              className="subspace-checklist"
                                                                    )

                                                     ],
                                            style={'height': '200px',
                                                   "width": '150px'}
                                           ),
                                   html.Div(id = "my-graph-div",
                                            className="eight columns",
                                            children=[dcc.Graph(id="my-graph",
                                                                figure=self.prepare_graph())],
                                            )
                                        ]
                                )
                            ]
                )
                    ])


        @app.callback(dash.dependencies.Output('my-graph', 'figure'),
                  [dash.dependencies.Input('subspace-list', 'value')])
        def update_output(value: list[str]) -> dict[str, Any]:
            """Callback to update ontology based on which subspaces are checked
            
            Parameters
            ----------
            value
                list of selected subspaces 
            """
            self._update_ontology(value)
            return self.prepare_graph()
        if not do_return:
            app.run_server(debug=False)
            return None
        else:
            return app

    def show(self) -> None:
        """Show in-browser, usuable in jupyter notebooks"""
        figure = self.prepare_graph()
        fig = go.Figure(figure)
        fig.show()

    def to_json(self) -> str:
        """Serialize visualization object, required for callback"""
        sentence_str = str(self.sentence)
        # temporarily store the string version
        original_sentence = self.sentence
        self.sentence = sentence_str  # type: ignore[assignment]
        graph = self.graph.to_dict()
        json_str = jsonpickle.encode(self, unpicklable=False)
        json_dict = jsonpickle.decode(json_str)
        json_dict['graph'] = graph

        result = jsonpickle.encode(json_dict)
        # restore original sentence object
        self.sentence = original_sentence
        return str(result)

    @classmethod
    def from_json(cls, data: dict) -> 'UDSVisualization':
        """Load serialized visualization object

        Parameters
        ----------
        data
            json dict representation of the current visualization 
        """
        uds_graph = data['graph']
        miso_graph = cast(UDSSentenceGraph, UDSSentenceGraph.from_dict(uds_graph, 'test-graph'))

        vis = cls(miso_graph, sentence = data['sentence'])
        for k, v in data.items():
            if k == "graph" or k == "sentence":
                continue
            else:
                setattr(vis, k, v)
        return vis

def serve_parser(parser: Any, with_syntax: bool = False) -> None:
    """Wrapper for serving from MISO parser

    Parameters
    ----------
    with_syntax
        flag to show or hide syntactic edges
    """
    graph = UDSCorpus(split="dev")['ewt-dev-1']
    vis = UDSVisualization(graph, sentence = graph.sentence, from_prediction = False, add_syntax_edges=with_syntax)

    vis_json = vis.to_json()

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__ + "_parser", external_stylesheets=external_stylesheets)
    app.title = "MISO Web API"

    app.layout = html.Div([
        html.Div(className="row",
              children=[
                  html.Div([dcc.Input(
                            id="input_text",
                            type="text",
                            placeholder="input type text",
                            value=str(vis.sentence),
                            ),
                            html.Button(id='submit-button', type='submit', children='Submit'),
                            ]),
                  html.Div(className="row", children = [
                  html.Div(className="twelve columns",
                           children = [
                               html.Div(className="four columns",
                                        children=[
                                            dcc.Checklist(id="subspace-list",
                                                                options=vis._get_uds_subspaces(),  # type: ignore[arg-type]
                                                          value=[x['label'] for x in vis._get_uds_subspaces()],
                                                          className="subspace-checklist"
                                                                )

                                                 ],
                                        style={'height': '200px',
                                               "width": '150px'}
                                       ),
                               html.Div(id = "my-graph-div",
                                        className="eight columns",
                                        children=[dcc.Graph(id="my-graph",
                                                            figure=vis.prepare_graph()),
                                                    html.Div(id='vis-hidden', children = [vis_json], style={'display': 'none'})
                                                    ]
                                        )
                                    ]
                            )
                        ]
            )
                ])
    ])


    @app.callback(dash.dependencies.Output('vis-hidden', 'children'),
                  [dash.dependencies.Input('submit-button', 'n_clicks')],
              [dash.dependencies.State('input_text', 'value'), dash.dependencies.State('vis-hidden', 'children')])
    def parse_new_sentence(n_clicks:int, text_value: str, vis_data: list[str]) -> list[str]:
        """Dash callback to link the submit button with a change in state to the input text,
        executes upon click of submit button and parses new sentence, updating the visualziation

        Parameters
        ----------
        n_clicks
            submit button counter
        text_value
            input value inside text form 
        vis_data
            serialized current visualization 
        """
        vis = UDSVisualization.from_json(jsonpickle.decode(vis_data[0]))
        sent = str(vis.sentence)
        # make sure box clicked and it's actually a new sentence
        if n_clicks is not None and n_clicks > 0 and text_value != sent:
            # parse
            graph = parser(text_value)
            # update graph
            vis.graph = graph
            # update sentence
            vis.sentence = StringList(text_value)
            vis.add_syntax_edges = with_syntax
            vis.from_prediction = True
        return [vis.to_json()]

    @app.callback(dash.dependencies.Output("my-graph", "figure"),
            [dash.dependencies.Input('vis-hidden', 'children'),
             dash.dependencies.Input('subspace-list', 'value')])
    def update_graph_from_vis(vis_data: list[str], subspace_list: list[str]) -> dict:
        """Callback to update the visualization when subspaces are
        selected or deselected 

        Parameters
        ----------
        vis_data
            serialized version of the current visualization
        subspace_list
            list of selected subspaces 
        """
        vis = UDSVisualization.from_json(jsonpickle.decode(vis_data[0]))
        vis._update_ontology(subspace_list)

        return vis.prepare_graph()

    app.run_server(debug=False)
