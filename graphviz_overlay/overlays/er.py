from overlays.graphviz import GraphOverlay

class EntityRelationshipOverlay(GraphOverlay):

    name = 'er'

    styles = {
        'entity': {
            'shape': 'box',
        },
        'attribute': {},
        'relationship': {
            'shape': 'diamond',
            'style': ['filled'],
            'color': 'lightgrey',
        },
        'cardinality': {},
    }

    def walk_model(self, ctx, model):
        self.add_domains(ctx, model.get('domains', {}))
        self.add_entity_relationships(ctx, model)
        self.add_ranks(ctx, model.get('ranks', {}))

    def add_domains(self, ctx, domains):
        for name, domain in domains.items():
            self.add_domain(ctx, name, domain)

    def add_domain(self, ctx, name, domain):
        graphname = f'cluster_{name}'

        new_ctx = ctx.new_context(graphname, name, domain)
        self.walk_model(new_ctx, domain)
        ctx.add_subgraph_from_context(new_ctx)

    def add_entity_relationships(self, ctx, model):
        self.add_entities(ctx, model.get('entities', {}))
        self.add_relationships(ctx, model.get('relationships', []))

    def add_entities(self, ctx, entities):
        for name, entity in entities.items():
            self.add_entity(ctx, name, entity)

    def add_entity(self, ctx, name, entity):
        ctx.add_node(
            name,
            entity,
            classes=['entity'],
        )
        self.add_entity_attributes(
            ctx,
            name,
            entity,
        )

    def add_entity_attributes(self, ctx, entity_name, entity):
        for attribute_name, attribute in entity.get('attributes', {}).items():
            self.add_entity_attribute(
                ctx,
                entity_name,
                attribute_name,
                attribute,
            )

    def add_entity_attribute(
        self, ctx, entity_name, attribute_name, attribute
    ):
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
        ctx.add_edge(node_name, entity_name)

    def add_relationships(self, ctx, relationships):
        for relationship in relationships:
            self.add_relationship(ctx, relationship)

    def add_relationship(self, ctx, relationship):
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
        self.add_cardinality(ctx, relationship)

    def add_cardinality(self, ctx, relationship):
        connector_id = connectorid(relationship)

        from_attrs = {'label': relationship['from'].get('cardinality', '')}
        from_attrs.update(relationship['from'])
        ctx.add_edge(
            label_to_nodename(relationship['from']['name']),
            connector_id,
            from_attrs,
            classes=['cardinality'],
        )
        to_attrs = {'label': relationship['to'].get('cardinality', '')}
        to_attrs.update(relationship['to'])
        ctx.add_edge(
            connector_id,
            label_to_nodename(relationship['to']['name']),
            to_attrs,
            classes=['cardinality'],
        )


def connectorid(relationship):
    return '_'.join(
        [
            label_to_nodename(relationship['from']['name']),
            label_to_nodename(relationship['to']['name']),
        ]
    )


def labels_to_nodename(*labels):
    return '_'.join(
        label_to_nodename(label)
        for label in labels
    )


def label_to_nodename(label):
    return label.lower().replace(' ', '_').replace('-', '_')
