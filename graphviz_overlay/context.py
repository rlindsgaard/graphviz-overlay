import copy
import logging

log = logging.getLogger(__name__)
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
        self, stylesheet: dict = None, path: str = '', prefix: str = '',
        _level: int = 0
    ):
        self.graph = None
        self.styles = copy.deepcopy(self.base_styles)
        self.add_stylesheet(stylesheet or {})
        self._ranks = {}
        self._level = _level
        self.prefix = prefix
        self.path = path

    def init_graph(self, name, graph_class, attributes):
        styles = attributes.get('styles', {})

        graph_attrs = styles.get('graph', {})
        graph_attrs.update(attributes)

        graph_attrs = self._build_attributes(
            'graph',
            graph_attrs
        )
        self.graph = graph_class(
            name,
            graph_attr=graph_attrs,
            node_attr=self._build_attributes(
                'node',
                styles.get('node'),
            ),
            edge_attr=self._build_attributes(
                'edge',
                styles.get('edge'),
            ),
        )

    def add_stylesheet(self, stylesheet: dict):
        """
        Add stylesheet to the context stylesheet.

        A stylesheet consists of a dictionary of class
        definitions which are themselves dictionaries.
        """
        new_stylesheet = self.styles.copy()
        for class_name, attrs in stylesheet.items():
            new_class = new_stylesheet.get(class_name, {})
            for attr, value in attrs.items():
                if attr == 'style':
                    if 'style' not in new_class:
                        new_class['style'] = value.copy()
                    else:
                        new_value = []
                        for v in new_class['style']:
                            if v in value:
                                continue
                            new_value.append(v)
                        for v in value:
                            new_value.append(v)
                        new_class['style'] = new_value
                else:
                    new_class[attr] = value
            new_stylesheet[class_name] = new_class
        self.styles = new_stylesheet

    def new_context(self, name, path, model):
        stylesheet = self.styles.copy()
        ctx = GraphContext(
            stylesheet,
            path=path,
            prefix=model.get('prefix', ''),
            _level=self._level + 1,
        )

        if model.get('cluster', False):
            if not name.startswith('cluster_'):
                name = f'cluster_{name}'

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

    def add_edge(
        self, node_from: str, node_to: str, attributes: dict = None,
        classes=None
    ):
        log.info('Enter add_edge')

        classes = classes or []

        attrs = self._build_attributes(
            'edge',
            attributes,
            classes,
        )

        log.info('Adding edge')
        log.debug(f'{node_from=} {node_to=} {attrs=}')
        self.graph.edge(
            node_from,
            node_to,
            **attrs
        )

    def add_node(self, name, attributes=None, classes=None):
        log.info('Enter add_node')

        classes = classes or []
        attributes = attributes or {}

        log.debug(f'{name} {attributes} {classes}')

        if 'rank' in attributes:
            rank_name = attributes['rank']
            rank_nodes = self._ranks.get(rank_name, [])
            self._ranks[rank_name] = rank_nodes + [name]

        attrs = self._build_attributes(
            'node',
            attributes,
            classes,
        )

        if 'label' in attrs and isinstance(attrs['label'], dict):
            attrs['label'] = format_html_label(attrs['label'])
            attrs['shape'] = 'plain'

        node_name = self.node_id(name)
        log.info('Adding node')
        log.debug(f'{node_name=} {attrs=}')
        self.graph.node(
            node_name,
            **attrs
        )

    def _build_attributes(
        self, element_type: str, attributes: dict, classes: list = None
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
        attrs = self.styles.get(element_type, {}).copy()

        classes = classes or []
        attributes = attributes or {}

        for c in classes + attributes.get('classes', []):
            attrs.update(self.styles.get(c, {}))

        if attributes:
            attrs.update(attributes)

        styles = attrs.get('style', [])

        if not isinstance(styles, list):
            raise ValueError(
                "style attribute must be a list, got '%r'" % styles
            )

        if not attributes.get('visible', True):
            styles.append('invis')
        elif attributes.get('cluster', False):
            if not styles:
                styles.append('solid')

        if styles:
            attrs['style'] = ','.join(styles)

        result = {}
        for attr in attrs.keys():
            if attr in valid_attrs:
                result[attr] = attrs[attr]
        return result

    def add_rank(self, rank_name: str, rank_type: str) -> ():
        """Add rank specification to the graph

        :param str rank_name: Name given the rank.
        :param str rank_type: same, min, or max.
        """
        rank_nodes = self._ranks.get(rank_name)

        if rank_type not in ['same', 'min', 'max']:
            log.warning("Rank type '%s' not valid, replacing with 'same'", rank_type)
            rank_type = 'same'

        with self.graph.subgraph() as s:
            s.attr(rank=rank_type)
            for nodename in rank_nodes:
                s.node(nodename)

    def source(self):
        return self.graph.source


def format_html_label(label):
    """Produces a graphviz html label from a dictionary."""

    rows = []
    for row in label['trs']:
        tds = []
        for td in row:
            tds.append(
                format_html_tag('td', td, td['value'])
            )
        rows.append(
            format_html_tag('tr', inner=''.join(tds))
        )
    table = format_html_tag('table', label, ''.join(rows))
    return f'<{table}>'


def format_html_tag(tag, attrs={}, inner=''):
    html_attrs = {
        'TABLE': [
            'ALIGN', 'BGCOLOR', 'BORDER', 'CELLBORDER', 'CELLPADDING',
            'CELLSPACING', 'COLOR', 'COLUMNS', 'FIXEDSIZE', 'GRADIENTANGLE',
            'HEIGHT', 'HREF', 'ID', 'PORT', 'ROWS', 'SIDES',
            'STYLE', 'TARGET', 'TITLE', 'TOOLTIP', 'VALIGN',
            'WIDTH',
        ],
        'TD': [
            'ALIGN', 'BALIGN', 'BGCOLOR', 'BORDER', 'CELLPADDING',
            'CELLSPACING', 'COLOR', 'COLSPAN', 'FIXEDSIZE', 'GRADIENTANGLE',
            'HEIGHT', 'HREF', 'ID', 'PORT', 'ROWSPAN', 'SIDES',
            'STYLE', 'TARGET', 'TITLE', 'TOOLTIP', 'VALIGN',
            'WIDTH',
        ]
    }
    tag = tag.upper()
    tag_attrs = [
        f'{k.upper()}="{v}"'
        for k, v in attrs.items()
        if k.upper() in html_attrs[tag]
    ]
    log.debug(f'{tag_attrs=}')
    html = f'<{tag}'
    if tag_attrs:
        html += f" {' '.join(tag_attrs)}"
    html += f'>{inner}</{tag}>'
    return html
