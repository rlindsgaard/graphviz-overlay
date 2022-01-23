import json
import os.path

import graphviz
import pytest

from graphviz_overlay import GraphContext
from graphviz_overlay.overlays import Graph, Digraph

here = os.path.dirname(os.path.abspath(__file__))
examples = os.path.join(here, '..', 'examples')


def assert_hello_world_graph(m):
    print(m.mock_calls)
    m.edge.assert_called_with('hello', 'world')


@pytest.mark.parametrize('example,expect_func', [
    ('hello_world', assert_hello_world_graph)
])
def test_graphviz_graph(example, expect_func, mocker):
    gv = mocker.Mock(spec=graphviz.Graph)
    m = mocker.Mock(return_value=gv)

    model = load_example_model(example)
    overlay = Graph()
    overlay.draw(name='G', model=model, graph_class=m)

    expect_func(gv)


@pytest.mark.parametrize('example,expect_func', [
    ('hello_world', assert_hello_world_graph)
])
def test_graphviz_digraph(example, expect_func, mocker):
    gv = mocker.Mock(spec=graphviz.Digraph)
    m = mocker.Mock(return_value=gv)

    model = load_example_model(example)
    overlay = Graph()
    overlay.draw(name='G', model=model, graph_class=m)

    expect_func(gv)


def load_example_model(example):
    with open(os.path.join(examples, f'{example}.json'), mode='r') as f:
        return json.load(f)
