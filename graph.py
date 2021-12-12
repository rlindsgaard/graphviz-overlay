"""
Generate a undirected graph
"""
from argparse import ArgumentParser
import graphviz
import json

valid_attrs = [
    '_background',
    'area',
    'arrowhead',
    'arrowsize',
    'arrowtail',
    'bb',
    'bgcolor',
    'center',
    'charset',
    'class',
    'clusterrank',
    'color',
    'colorscheme',
    'comment',
    'compound',
    'concentrate',
    'constraint',
    'Damping',
    'decorate',
    'defaultdist',
    'dim',
    'dimen',
    'dir',
    'diredgeconstraints',
    'distortion',
    'dpi',
    'edgehref',
    'edgetarget',
    'edgetooltip',
    'edgeURL',
    'epsilon',
    'esep',
    'fillcolor',
    'fixedsize',
    'fontcolor',
    'fontname',
    'fontnames',
    'fontpath',
    'fontsize',
    'forcelabels',
    'gradientangle',
    'group',
    'head_lp',
    'headclip',
    'headhref',
    'headlabel',
    'headport',
    'headtarget',
    'headtooltip',
    'headURL',
    'height',
    'href',
    'id',
    'image',
    'imagepath',
    'imagepos',
    'imagescale',
    'inputscale',
    'K',
    'label',
    'label_scheme',
    'labelangle',
    'labeldistance',
    'labelfloat',
    'labelfontcolor',
    'labelfontname',
    'labelfontsize',
    'labelhref',
    'labeljust',
    'labelloc',
    'labeltarget',
    'labeltooltip',
    'labelURL',
    'landscape',
    'layer',
    'layerlistsep',
    'layers',
    'layerselect',
    'layersep',
    'layout',
    'len',
    'levels',
    'levelsgap',
    'lhead',
    'lheight',
    'lp',
    'ltail',
    'lwidth',
    'margin',
    'maxiter',
    'mclimit',
    'mindist',
    'minlen',
    'mode',
    'model',
    'mosek',
    'newrank',
    'nodesep',
    'nojustify',
    'normalize',
    'notranslate',
    'nslimit',
    'nslimit1',
    'ordering',
    'orientation',
    'outputorder',
    'overlap',
    'overlap_scaling',
    'overlap_shrink',
    'pack',
    'packmode',
    'pad',
    'page',
    'pagedir',
    'pencolor',
    'penwidth',
    'peripheries',
    'pin',
    'pos',
    'quadtree',
    'quantum',
    # 'rank',  # We intepret this one ourselves
    'rankdir',
    'ranksep',
    'ratio',
    'rects',
    'regular',
    'remincross',
    'repulsiveforce',
    'resolution',
    'root',
    'rotate',
    'rotation',
    'samehead',
    'sametail',
    'samplepoints',
    'scale',
    'searchsize',
    'sep',
    'shape',
    'shapefile',
    'showboxes',
    'sides',
    'size',
    'skew',
    'smoothing',
    'sortv',
    'splines',
    'start',
    'style',
    'stylesheet',
    'tail_lp',
    'tailclip',
    'tailhref',
    'taillabel',
    'tailport',
    'tailtarget',
    'tailtooltip',
    'tailURL',
    'target',
    'tooltip',
    'truecolor',
    'URL',
    'vertices',
    'viewport',
    'voro_margin',
    'weight',
    'width',
    'xdotversion',
    'xlabel',
    'xlp',
    'z',
]


def main(opts):
    model = load_json_file(opts.infile)

    styles = {}
    if opts.stylesheet:
        styles = load_json_file(opts.stylesheet)

    ctx = GraphContext(styles)

    overlay = opts.overlay(ctx)
    overlay.draw(opts.name, model)

    print(overlay.source())


def load_json_file(filename):
    with open(filename, mode='r') as f:
        return json.load(f)


class GraphContext(object):
    """
    Defines a context for graph objects.

    A wrapper for the Graphviz interface to define objects via
    a dictionary structure and turn it into a graph.

    Automatically adds graphviz attributes defined in the object
    see https://graphviz.org/doc/info/attrs.html for availability.

    Attributes added to the root dictionary is added as graph attributes.
    Furthermore special "attributes" are interpreted as such::

        "nodes": {
            "node_id": {
                # Node attributes
                "classes": ["mynode"], # Nodes have the base style "node"
                #
                The ``rank`` attribute is treated differently, as it is defined
                by an id in the node object. e.g. "rank": "myrank". At the

                "rank": "myrank"
            }
        },
        "edges": [
            # An edge pointing to and from the same node
            {
                "from": "node_id",
                "to": "node_id"
                "classes": ["myedge"],  # Edges have the base style "edge"
            }
        ],
        "subgraphs": {
            "subgraph_name": {
                # Recursively treated as an individual graph
            }
        }
        "classes": ["mygraph"],  #  All graphs have the base style "graph"


        "ranks": {
            "myrank": "same",
        }
        "styles": {
            "mynode": {

            }
        }
        }
    """
    base_styles = {
        'graph': {},
        'node': {},
        'edge': {},
    }

    def __init__(
        self, stylesheet, prefix='', _level=0
    ):
        self.graph = None
        self.styles = self.base_styles.copy()
        self.styles.update(stylesheet)

        self._ranks = {}
        self._level = _level
        self.prefix = prefix

    def init_graph(self, name, graph_class, attributes={}):
        graph_attrs = self._build_attributes(
            'graph',
            attributes,
        )
        self.graph = graph_class(
            name,
            graph_attr=graph_attrs,
            node_attr=self._build_attributes('node', {}),
            edge_attr=self._build_attributes('edge', {}),
        )

    def new_context(self, name, model):
        styles = self.styles.copy()
        # styles.update(model.get('styles', {}))
        ctx = self.__class__(
            styles,
            prefix=model.get('prefix', ''),
            _level=self._level + 1,
        )
        ctx.init_graph(name, self.graph.__class__, model)
        return ctx

    def add_subgraph_from_context(self, ctx):
        self.graph.subgraph(
            ctx.graph,
        )
        for rank, nodes in ctx.get_ranks().items():
            self._ranks[rank] = self._ranks.get(rank, []) + nodes

    def get_ranks(self):
        return self._ranks

    def node_id(self, name):
        if not self.prefix:
            return name
        return f'{self.prefix}_{name}'

    def add_edge(self, edge, attributes=None, classes=None):
        classes = classes or []

        attrs = self._build_attributes(
            'edge',
            attributes,
            classes,
        )
        self.graph.edge(
            edge['from'],
            edge['to'],
            **attrs
        )

    def add_node(self, name, attributes=None, classes=None):
        classes = classes or []

        if 'rank' in attributes:
            rank_name = attributes['rank']
            rank_nodes = self._ranks.get(rank_name, [])
            self._ranks[rank_name] = rank_nodes + [name]

        attrs = self._build_attributes(
            'node',
            attributes,
            classes,
        )

        self.graph.node(
            self.node_id(name),
            **attrs
        )

    def _build_attributes(
        self, type: str, attributes: dict, classes: list = None
    ) -> dict:
        """
        Construct a dictionary of attributes for a graphviz element.

        Filters out any non-valid attributes and applies any attributes
        defined in any of the classes.

        Classes work like CSS classes, any attribute defined gets
        overriden by that later defined one.

        Any attributes specified overrides the one supplied by
        any classes.

        :param str type: The DOT element, graph, subgraph, node, edge
        :param dict attributes: (key, value) pairs. The value is
            treated as a literal.
        :param list classes: Any classes to apply defined by the stylesheet.
        :returns: A (key, value) mapping of element attributes.
        :rtype: dict
        """
        attrs = {}

        classes = classes or []
        attributes = attributes or {}

        for c in classes + attributes.get('classes', []):
            attrs.update(self.styles.get(c, {}))

        if attributes:
            attrs.update(attributes)

        result = {}
        for attr in attrs.keys():
            if attr in valid_attrs:
                result[attr] = attrs[attr]
        return result

    def add_rank(self, rank_name, rank_type):
        rank_nodes = self._ranks.get(rank_name)

        fmt = '{{rank={rank_type}; {nodenames}}}'
        self.graph.body.append(
            fmt.format(
                rank_type=rank_type,
                nodenames=' '.join(rank_nodes)),
        )

    def source(self):
        return self.graph.source


class BaseOverlay(object):
    def __init__(self, ctx):
        self.ctx = ctx

    def draw(self, name, model, graph_class):
        self.ctx.init_graph(
            name,
            graph_class,
        )
        self.walk_model(self.ctx, model)

    def load_styles(self, stylesheet, model):
        styles = {}
        if stylesheet:
            styles.update(stylesheet)
        styles.update(
            model.get('styles', {}),
        )
        return styles

    def source(self):
        return self.ctx.source()

    def walk_model(self, ctx, model):
        self.add_nodes(ctx, model.get('nodes', {}))
        self.add_subgraphs(ctx, model.get('subgraphs', {}))
        self.add_edges(ctx, model.get('edges', {}))
        self.add_ranks(ctx, model.get('ranks', {}))

    def add_nodes(self, ctx, nodes):
        for node_id, attributes in nodes.items():
            ctx.add_node(node_id, attributes)

    def add_subgraphs(self, ctx, subgraphs):
        for subgraph_name, model in subgraphs.items():
            subgraph_ctx = ctx.new_context(subgraph_name, model)

            self.walk_model(subgraph_ctx, model)

            ctx.add_subgraph_from_context(subgraph_ctx)

    def add_edges(self, ctx, edges):
        for edge in edges:
            ctx.add_edge(edge)

    def add_ranks(self, ctx, ranks):
        for rank_name, rank_type in ranks.items():
            ctx.add_rank(rank_name, rank_type)


class GraphOverlay(BaseOverlay):

    name = 'graph'

    def draw(self, name, model):
        super().draw(name, model, graphviz.Graph)


class DigraphOverlay(BaseOverlay):

    name = 'digraph'

    def draw(self, name, model):
        super().draw(name, model, graphviz.Digraph)


overlays = [
    GraphOverlay,
    DigraphOverlay,
]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-n', '--name',
        default='G',
        help='Name of the graph')
    parser.add_argument(
        '-i', '--infile',
        help='Input json file',
    )
    parser.add_argument(
        '-s', '--stylesheet',
        default=None,
        help='Stylesheet file',
    )
    subparsers = parser.add_subparsers()

    for overlay in overlays:
        subparser = subparsers.add_parser(overlay.name)
        subparser.set_defaults(overlay=overlay)

    main(parser.parse_args())
