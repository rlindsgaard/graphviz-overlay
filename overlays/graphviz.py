import graphviz


class GraphvizOverlay(object):
    """
    Base overlay for graphviz based graphs.
    """

    styles = {
        'highlight': {
            'penwidth': '3',
        },
    }

    def __init__(self, ctx, select, highlight):
        self.ctx = ctx
        self.selected_paths = [
            p.strip()
            for p in select.split(',')
        ]
        self.highlighted_paths = [
            p.strip()
            for p in highlight.split(',')
        ]

    @classmethod
    def arguments(self):
        return {
            'select': {'default': ''},
            'highlight': {'default': ''},
        }

    def draw(self, name, model, graph_class):
        self.ctx.init_graph(
            name,
            graph_class,
            styles=self.styles
        )
        processed_model = self.preprocess_model(model)
        self.walk_model(self.ctx, processed_model)

    def source(self):
        return self.ctx.source()

    def preprocess_model(self, model, current_path=''):
        """
        Preprocess the model selecting only elements in selected paths
        :returns: A filtered version of the model
        """
        new_model = model.copy()
        paths = []
        if current_path:
            paths.append(current_path)

        new_model['nodes'] = self.preprocess_nodes(
            model.get('nodes', {}),
            paths,
        )

        new_model['edges'] = self.preprocess_edges(
            model.get('edges', {}),
            paths,
        )

        new_model['subgraphs'] = self.preprocess_subgraphs(
            model.get('subgraphs', {}),
            paths,
            current_path,
        )

        return new_model

    def preprocess_nodes(self, nodes, paths):
        selected_nodes = {}
        for nodeid, node in nodes.items():
            node_paths = paths + node.get('paths', [])
            if not self.in_a_selected_path(node_paths):
                continue

            if self.is_highlighted(node_paths):
                node['classes'] = node.get('classes', []) + ['highlight']

            selected_nodes[nodeid] = node
        return selected_nodes

    def preprocess_edges(self, edges, paths):
        selected_edges = []
        for edge in edges:
            edge_paths = paths + edge.get('paths', [])
            if not self.in_a_selected_path(edge_paths):
                continue

            if self.is_highlighted(edge_paths):
                edge['classes'] = edge.get('classes', []) + ['highlight']

            selected_edges.append(edge)
        return selected_edges

    def preprocess_subgraphs(self, subgraphs, paths, current_path=''):
        selected_subgraphs = {}
        for subgraph_name, subgraph in subgraphs.items():
            subgraph_path = self.subgraph_path(subgraph_name, current_path)

            paths = [subgraph_path]

            if (
                self.partially_selected_path(paths)
                or self.in_a_selected_path(paths)
            ):
                processed_subgraph = self.preprocess_model(
                    subgraph,
                    current_path=subgraph_path,
                )
                if (
                    processed_subgraph.get('nodes', False)
                    or processed_subgraph.get('edges', False)
                ):
                    selected_subgraphs[subgraph_name] = processed_subgraph
                else:
                    selected_subgraphs.update(
                        processed_subgraph.get('subgraphs', {})
                    )
        return selected_subgraphs

    def subgraph_path(self, subgraph_name, current_path):
        if current_path:
            return f'{current_path}.{subgraph_name}'
        return subgraph_name

    def is_highlighted(self, paths):
        return self.paths_in_paths(paths, self.highlighted_paths)

    def in_a_selected_path(self, paths):
        """Element is in a selected path"""
        if self.selected_paths == ['']:
            return True
        return self.paths_in_paths(paths, self.selected_paths)

    def paths_in_paths(self, paths, selected_paths):
        inverted_paths = [
            p[1:]
            for p in selected_paths
            if p.startswith('^')
        ]
        in_inverted_path = False

        for path in paths:
            if any(path.startswith(p) for p in selected_paths):
                return True

            in_inverted_path = (
                in_inverted_path
                or any(path.startswith(p) for p in inverted_paths)
            )

        return (inverted_paths and not in_inverted_path)

    def partially_selected_path(self, paths):
        """Is any current path prefix of a selected path."""
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
            ctx.add_edge(edge, edge)

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
