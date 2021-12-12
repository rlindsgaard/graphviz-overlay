import graphviz


class GraphvizOverlay(object):
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


class GraphOverlay(GraphvizOverlay):

    name = 'graph'

    def draw(self, name, model):
        super().draw(name, model, graphviz.Graph)


class DigraphOverlay(GraphvizOverlay):

    name = 'digraph'

    def draw(self, name, model):
        super().draw(name, model, graphviz.Digraph)
