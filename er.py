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
    'rank',
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
    def __init__(self, graph, styles, prefix=''):
        self.graph = graph
        self.styles = styles

    def get_style(self, style_type, default={}):
        return self.styles.get(style_type, default)

    def node_name(self, name):
        if not self.prefix:
            return name
        return f'{self.prefix}_{name}'

    def add_edge(self, source_id, target_id, **kwargs):
        self.graph.edge(source_id, target_id, **kwargs)

    def add_node(self, name, **kwargs):
        self.graph.node(
            name,
            **kwargs
        )


def main(opts):
    with open(opts.infile, mode='r') as f:
        model = json.load(f)
    dot = graphviz.Graph()
    styles = model.get('styles', {})
    ctx = Context(dot, styles)

    if opts.domain:
        for domain in opts.domain.split('.'):
            model = model['domains'][domain]

    add_graph(ctx, model)

    print(dot.source)


def add_graph(ctx, model):
    attrs = ctx.get_style('graph')
    attrs.update(attrs_for('graph', model))
    # ctx.graph.attr('graph', **attrs)

    add_domains(ctx, model.get('domains', {}))
    add_entity_relationships(ctx, model)


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


def add_entity_relationships(ctx, model):
    add_entities(ctx, model.get('entities', {}))
    add_relationships(ctx, model.get('relationships', []))


def add_entities(ctx, entities):
    for name, entity in entities.items():
        add_entity(ctx, name, entity)


def add_entity(ctx, name, entity):
    attrs = ctx.styles.get(
        'entity',
        {
            'shape': 'box',
        }
    ).copy()
    attrs.update(attrs_for('node', entity))
    ctx.add_node(
        name,
        **attrs
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

    attrs = ctx.styles.get('attribute', {}).copy()
    attrs['label'] = attribute_name
    attrs.update(attrs_for('node', attribute))

    ctx.add_node(
        node_name,
        **attrs
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

    attrs = ctx.styles.get('relationship', {
        "shape": "diamond",
        "style": "filled",
        "color": "lightgrey",
    }).copy()
    attrs['label'] = label
    attrs.update(attrs_for('node', relationship))

    ctx.add_node(
        connectorid(relationship),
        **attrs
    )
    add_cardinality(ctx, relationship)


def add_cardinality(ctx, relationship):
    connector_id = connectorid(relationship)

    ctx.add_edge(
        label_to_nodename(relationship['from']['name']),
        connector_id,
        label=relationship['from'].get('cardinality', ''),
        **ctx.styles.get('cardinality', {})
    )
    ctx.add_edge(
        connector_id,
        label_to_nodename(relationship['to']['name']),
        label=relationship['to'].get('cardinality', ''),
        **ctx.styles.get('cardinality', {})
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
    for attr in valid_attrs:
        if attr in values:
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
    main(parser.parse_args())
