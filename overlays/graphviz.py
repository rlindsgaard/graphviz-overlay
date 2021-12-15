import graphviz


class GraphvizOverlay(object):
    """
    Base overlay for graphviz based graphs.
    """

    styles = {}

    def __init__(self, ctx, select):
        self.ctx = ctx
        self.selected_paths = [
            p.strip()
            for p in select.split(',')
        ]

    @classmethod
    def arguments(self):
        return {
            'select': {'default': ''}
        }

    def draw(self, name, model, graph_class):
        self.ctx.init_graph(
            name,
            graph_class,
            styles=self.styles
        )
        processed_model = self.process_paths(model)
        self.walk_model(self.ctx, processed_model)

    def source(self):
        return self.ctx.source()

    def process_paths(self, model, current_path=''):
        """
        Preprocess the model selecting only elements in selected paths
        :returns: A filtered version of the model
        """
        new_model = model.copy()
        paths = []
        if current_path:
            paths.append(current_path)

        nodes = {}
        for nodeid, node in model.get('nodes', {}).items():
            node_paths = paths + node.get('paths', [])
            if self.in_selected_paths(node_paths):
                nodes[nodeid] = node
        new_model['nodes'] = nodes
        edges = []
        for edge in model.get('edges', {}):
            edge_paths = paths + edge.get('paths', [])
            if self.in_selected_paths(edge_paths):
                edges.append(edge)
        new_model['edges'] = edges
        subgraphs = {}
        for subgraph_name, subgraph in model.get('subgraphs', {}).items():
            subgraph_path = subgraph_name
            if current_path:
                subgraph_path = f'{current_path}.{subgraph_name}'
            paths = [subgraph_path]

            if self.in_path_prefix(paths) or self.in_selected_paths(paths):
                processed_subgraph = self.process_paths(
                    subgraph,
                    current_path=subgraph_path,
                )
                if (
                    processed_subgraph.get('nodes', False)
                    or processed_subgraph.get('edges', False)
                ):
                    subgraphs[subgraph_name] = processed_subgraph
                else:
                    subgraphs.update(processed_subgraph.get('subgraphs', {}))

        new_model['subgraphs'] = subgraphs
        return new_model

    def in_selected_paths(self, paths):
        if self.selected_paths == ['']:
            return True

        for path in paths:
            if any(path.startswith(p) for p in self.selected_paths):
                return True

        return False

    def in_path_prefix(self, paths):
        if self.selected_paths == ['']:
            return True
        for path in paths:
            if any(p.startswith(path) for p in self.selected_paths):
                return True
        return False

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
            subgraph_ctx = ctx.new_context(
                subgraph_name,
                subgraph_name,
                model,
            )

            self.walk_model(subgraph_ctx, model)

            ctx.add_subgraph_from_context(subgraph_ctx)

    def add_edges(self, ctx, edges):
        for edge in edges:
            ctx.add_edge(edge)

    def add_ranks(self, ctx, ranks):
        for rank_name, rank_type in ranks.items():
            ctx.add_rank(rank_name, rank_type)


class GraphOverlay(GraphvizOverlay):
    """
    Overlay generating an undirected graph.
    """

    name = 'graph'

    def draw(self, name, model):
        super().draw(name, model, graphviz.Graph)


class DigraphOverlay(GraphvizOverlay):
    """
    Overlay generating a directed graph.
    """

    name = 'digraph'

    def draw(self, name, model):
        super().draw(name, model, graphviz.Digraph)
