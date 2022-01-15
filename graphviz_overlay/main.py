"""
Generate a undirected graph
"""
from argparse import ArgumentParser, FileType
import sys

from graphviz_overlay import GraphContext, overlays
from graphviz_overlay.util import load_json_file


def main(opts):
    model = load_json_file(opts.infile)

    styles = load_json_file(opts.stylesheet)

    ctx = GraphContext(styles)

    overlay_args = {
        arg: getattr(opts, arg)
        for arg in opts.overlay.arguments()
    }

    overlay = opts.overlay(ctx, **overlay_args)
    overlay.draw(opts.name, model)

    print(overlay.source())


overlays = [
    overlays.Graph,
    overlays.Digraph,
    overlays.EntityRelationship,
]


def run():
    parser = ArgumentParser()
    parser.add_argument(
        '-n', '--name',
        default='G',
        help='Name of the graph')
    parser.add_argument(
        '-i', '--infile',
        type=FileType(mode='r'),
        help='Input json file',
        default=sys.stdin
    )
    parser.add_argument(
        '-s', '--stylesheet',
        type=FileType(mode='r'),
        default=None,
        help='Stylesheet file',
    )

    subparsers = parser.add_subparsers(
        title='Overlays',
        description='The overlay that will be used to generate the graph.',
        required=True,
        dest='overlay',
        help='Select the overlay to render the graph.',
    )

    for overlay in overlays:
        subparser = subparsers.add_parser(overlay.name)
        args = overlay.arguments()
        for arg, params in args.items():
            arg = arg.replace('_', '-')
            subparser.add_argument(f'--{arg}', **params)
        subparser.set_defaults(overlay=overlay)

    main(parser.parse_args())
