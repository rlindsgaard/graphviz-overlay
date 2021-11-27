"""
Generate a graphviz ER diagram from a json structure.

Produces an ER diagram in the format presented as example
in graphvizs gallery https://graphviz.org/Gallery/undirected/ER.html

"""
from argparse import ArgumentParser
import graphviz
import json

graph_attrs = ["layout"]


def main(opts):
    with open(opts.infile, mode='r') as f:
        model = json.load(f)
    dot = graphviz.Graph()

    styles = model.get('styles', {})
    if opts.domain:
        for domain in opts.domain.split('.'):
            model = model['domains'][domain]

    add_graph(dot, model, styles)

    print(dot.source)


def add_graph(g, model, styles):
    attrs = {}
    for attr_name in graph_attrs:
        if attr_name in model:
            attrs[attr_name] = model[attr_name]
    g.attr('graph', **attrs)

    add_domains(g, model.get('domains', {}), styles)
    add_entity_relationships(g, model, styles)


def add_domains(g, domains, styles):
    for label, domain in domains.items():
        add_domain(g, label, domain, styles)


def add_domain(g, label, domain, styles):
    name = domain.get('name', '')
    graphname = f'cluster_{label_to_nodename(label)}'

    domain_styles = styles.copy()
    domain_styles.update(domain.get('styles', {}))

    with g.subgraph(name=graphname) as c:
        c.attr(label=name)
        add_domains(c, domain.get('domains', {}), domain_styles)
        add_entity_relationships(c, domain, domain_styles)


def add_entity_relationships(g, model, styles):
    add_entities(g, model.get('entities', []), styles)
    add_relationships(g, model.get('relationships', []), styles)


def add_entities(g, entities, styles):
    for node in entities:
        add_entity(g, node, styles)


def add_relationships(g, relationships, styles):
    for relationship in relationships:
        add_relationship(g, relationship, styles)


def add_entity(g, entity, styles):
    add_node(
        g,
        label_to_nodename(entity['name']),
        entity['name'],
        **styles.get('entity', {
            'shape': 'box',
        }))
    add_entity_attributes(
        g,
        entity,
        styles,
    )


def add_entity_attributes(g, entity, styles):
    for attribute in entity.get('attributes', []):
        add_entity_attribute(g, entity, attribute, styles)


def add_entity_attribute(g, entity, attribute, styles):
    node_name = labels_to_nodename(entity['name'], attribute['name'])
    add_node(
        g,
        node_name,
        attribute['name'],
        **styles.get('attribute', {})
    )
    add_edge(
        g,
        node_name,
        entity['name'],
    )


def add_relationship(g, relationship, styles):
    label = relationship.get(
        'comment',
        '-'.join([
            relationship['source']['name'].upper()[0],
            relationship['target']['name'].upper()[0],
        ]))

    add_node(
        g,
        connectorid(relationship),
        label,
        **styles.get('relationship', {
            "shape": "diamond",
            "style": "filled",
            "color": "lightgrey",
        })
    )
    add_cardinality(g, relationship, styles)


def add_cardinality(g, relationship, styles):
    connector_id = connectorid(relationship)

    add_edge(
        g,
        label_to_nodename(relationship['source']['name']),
        connector_id,
        label=relationship['source'].get('cardinality', ''),
        **styles.get('cardinality', {})
    )
    add_edge(
        g,
        connector_id,
        label_to_nodename(relationship['target']['name']),
        label=relationship['target'].get('cardinality'),
        **styles.get('cardinality', {})
    )


def add_edge(g, source_id, target_id, **kwargs):
    g.edge(source_id, target_id, **kwargs)


def connectorid(relationship):
    return '_'.join(
        [
            label_to_nodename(relationship['source']['name']),
            label_to_nodename(relationship['target']['name']),
        ]
    )


def add_node(g, node_id, label, **kwargs):
    args = {
        'label': label,
    }
    args.update(kwargs)
    g.node(
        node_id,
        **args
    )


def labels_to_nodename(*labels):
    return '_'.join(label_to_nodename(l) for l in labels)


def label_to_nodename(label):
    return label.lower().replace(' ', '_').replace('-', '_')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-i', '--infile',
        help='Input json file',
    )
    parser.add_argument('-d', '--domain',
        help='Domain to output',
    )
    main(parser.parse_args())
