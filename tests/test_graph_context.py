import graphviz
import pytest

from graphviz_overlay import GraphContext


def test_instance_with_default_arguments():
    GraphContext()


def test_instance_with_stylesheet_argument():
    stylesheet = {
        'node': {
            'shape': 'box',
        },
        'custom-class': {
            'colour': 'lightgrey',
        }
    }
    expect = {
        'graph': {},
        'node': {
            'shape': 'box'
        },
        'edge': {},
        'custom-class': {
            'colour': 'lightgrey',
        },
    }
    ctx = GraphContext(stylesheet=stylesheet)
    assert ctx.styles == expect


def test_style_attribute_appends():
    stylesheet1 = {
        'node': {
            'style': ['solid'],
        }
    }
    stylesheet2 = {
        'node': {
            'style': ['dotted']
        }
    }
    ctx = GraphContext(stylesheet1)
    ctx.add_stylesheet(stylesheet2)
    ctx.add_stylesheet(stylesheet1)

    assert ctx.styles['node']['style'] == ['dotted', 'solid']


add_node_tests = [
    ('defaults', None, None),
    ('defaults2', {}, []),
    ('attributes', {'shape': 'box'}, None),
    ('classes', None, ['myclass']),
    ('attributs-classes', {'shape': 'box'}, ['myclass']),
]

parametrize_node_tests = pytest.mark.parametrize(
    "test,attributes,classes",
    add_node_tests,
)


@parametrize_node_tests
def test_add_node_with_default_stylesheet(
    test, attributes, classes, mocker
):
    expect = {
        'defaults': {},
        'defaults2': {},
        'attributes': {'shape': 'box'},
        'classes': {},
        'attributs-classes': {'shape': 'box'},
    }
    gv = mocker.Mock(spec=graphviz.Graph)
    m = mocker.Mock(return_value=gv)
    ctx = GraphContext()
    ctx.init_graph('G', m, {})
    ctx.add_node('anode', attributes=attributes, classes=classes)
    gv.node.assert_called_once_with(
        'anode',
        **expect[test]
    )


@parametrize_node_tests
def test_add_node_with_defined_stylesheet(
    test, attributes, classes, mocker
):
    expect = {
        'defaults': {},
        'defaults2': {},
        'attributes': {'shape': 'box'},
        'classes': {'color': 'lightgrey'},
        'attributs-classes': {'shape': 'box', 'color': 'lightgrey'},
    }
    stylesheet = {
        'myclass': {
            'color': 'lightgrey',
        }
    }
    gv = mocker.Mock(spec=graphviz.Graph)
    m = mocker.Mock(return_value=gv)
    ctx = GraphContext(stylesheet=stylesheet)
    ctx.init_graph('G', m, {})
    ctx.add_node('anode', attributes=attributes, classes=classes)
    gv.node.assert_called_once_with(
        'anode',
        **expect[test]
    )


def test_add_edge(mocker):
    gv = mocker.Mock(spec=graphviz.Graph)
    m = mocker.Mock(return_value=gv)
    ctx = GraphContext()
    ctx.init_graph('G', m, {})
    ctx.add_edge('hello', 'world')
    gv.edge.assert_called_once_with(
        'hello', 'world',
    )
