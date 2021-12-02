"""
Generate a graphviz ER diagram from a json structure.

Produces an ER diagram in the format presented as example
in graphvizs gallery https://graphviz.org/Gallery/undirected/ER.html

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


class Context(object):
    base_styles = {
        'graph': {},
        'node': {},
        'edge': {},
        'entity': {
            'shape': 'box',
        },
        'attribute': {},
        'relationship': {
            'shape': 'diamond',
            'style': 'filled',
            'color': 'lightgrey',
        },
        'cardinality': {},
    }

    def __init__(self, graph, styles, prefix=''):
        self.graph = graph
        self.styles = self.base_styles.copy()
        self.styles.update(styles)

    def get_style(self, style_type, default={}):
        return self.styles.get(style_type, default)

    def node_name(self, name):
        if not self.prefix:
            return name
        return f'{self.prefix}_{name}'

    def add_edge(self, source_id, target_id, attributes=None, classes=None):
        classes = classes or []

        attrs = self._build_attributes(
            attributes,
            ['edge'] + classes,
        )
        self.graph.edge(
            source_id,
            target_id,
            **attrs
        )

    def add_node(self, name, attributes=None, classes=None):
        classes = classes or []

        attrs = self._build_attributes(
            attributes,
            ['node'] + classes,
        )

        self.graph.node(
            name,
            **attrs
        )

    def _build_attributes(self, attributes, classes):
        attrs = {}

        for c in classes:
            attrs.update(self.styles.get(c, {}))

        if attributes:
            attrs.update(attributes)

        return attrs_for(classes[0], attrs)

    def rank(self, rank_type, nodenames):
        fmt = '{{rank={rank_type}; {nodenames}}}'
        self.graph.body.append(
            fmt.format(
                rank_type=rank_type,
                nodenames=' '.join(nodenames)),
        )


def main(opts):
    with open(opts.infile, mode='r') as f:
        model = json.load(f)
    dot = graphviz.Graph()

    styles = {}
    if opts.stylesheet:
        with open(opts.stylesheet, mode='r') as f:
            styles.update(json.load(f))
    styles.update(model.get('styles', {}))

    ctx = Context(dot, styles)

    if opts.domain:
        for domain in opts.domain.split('.'):
            model = model['domains'][domain]

    add_graph(ctx, model)

    print(dot.source)


def add_graph(ctx, model):
    attrs = ctx.get_style('graph')
    attrs.update(attrs_for('graph', model))
    ctx.graph.attr('graph', **attrs)

    add_domains(ctx, model.get('domains', {}))
    add_entity_relationships(ctx, model)

    # Append rank
    for rank_type, nodenames in model.get('rank', {}).items():
        ctx.rank(rank_type, nodenames)


def add_domains(ctx, domains):
    for name, domain in domains.items():
        add_domain(ctx, name, domain)


def add_domain(ctx, name, domain):
    graphname = f'cluster_{name}'

    domain_styles = ctx.styles.copy()
    domain_styles.update(domain.get('styles', {}))

    with ctx.graph.subgraph(name=graphname) as c:
        new_ctx = Context(c, domain_styles)

        c.attr(**attrs_for('graph', domain))

        add_domains(new_ctx, domain.get('domains', {}))
        add_entity_relationships(new_ctx, domain)

        # Append rank
        for rank_type, nodenames in domain.get('rank', {}).items():
            ctx.rank(rank_type, nodenames)


def add_entity_relationships(ctx, model):
    add_entities(ctx, model.get('entities', {}))
    add_relationships(ctx, model.get('relationships', []))


def add_entities(ctx, entities):
    for name, entity in entities.items():
        add_entity(ctx, name, entity)


def add_entity(ctx, name, entity):
    ctx.add_node(
        name,
        entity,
        classes=['entity'],
    )
    add_entity_attributes(
        ctx,
        name,
        entity,
    )


def add_entity_attributes(ctx, entity_name, entity):
    for attribute_name, attribute in entity.get('attributes', {}).items():
        add_entity_attribute(ctx, entity_name, attribute_name, attribute)


def add_entity_attribute(ctx, entity_name, attribute_name, attribute):
    node_name = labels_to_nodename(entity_name, attribute_name)

    attrs = {
        'label': attribute_name,
    }
    attrs.update(attribute)

    ctx.add_node(
        node_name,
        attrs,
        classes=['attribute'],
    )
    ctx.add_edge(
        node_name,
        entity_name,
    )


def add_relationships(ctx, relationships):
    for relationship in relationships:
        add_relationship(ctx, relationship)


def add_relationship(ctx, relationship):
    label = relationship.get(
        'label',
        '-'.join([
            relationship['from']['name'].upper()[0],
            relationship['to']['name'].upper()[0],
        ]))

    attrs = {
        'label': label,
    }
    attrs.update(relationship)

    ctx.add_node(
        connectorid(relationship),
        attrs,
        classes=['relationship'],
    )
    add_cardinality(ctx, relationship)


def add_cardinality(ctx, relationship):
    connector_id = connectorid(relationship)

    ctx.add_edge(
        label_to_nodename(relationship['from']['name']),
        connector_id,
        {'label': relationship['from'].get('cardinality', '')},
        classes=['cardinality'],
    )
    ctx.add_edge(
        connector_id,
        label_to_nodename(relationship['to']['name']),
        {'label': relationship['to'].get('cardinality', '')},
        classes=['cardinality'],
    )


def connectorid(relationship):
    return '_'.join(
        [
            label_to_nodename(relationship['from']['name']),
            label_to_nodename(relationship['to']['name']),
        ]
    )


def attrs_for(type, values):
    result = {}
    for attr in values.keys():
        if attr in valid_attrs:
            result[attr] = values[attr]
    return result


def labels_to_nodename(*labels):
    return '_'.join(
        label_to_nodename(label)
        for label in labels
    )


def label_to_nodename(label):
    return label.lower().replace(' ', '_').replace('-', '_')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-i', '--infile',
        help='Input json file',
    )
    parser.add_argument(
        '-d', '--domain',
        help='Domain to output',
    )
    parser.add_argument(
        '-s', '--stylesheet',
        help='Stylesheet file',
    )
    main(parser.parse_args())
