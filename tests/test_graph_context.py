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
