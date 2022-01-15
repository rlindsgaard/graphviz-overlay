################
graphviz-overlay
################

.. image:: https://readthedocs.org/projects/graphviz-overlay/badge/?version=latest
  :target: https://graphviz-overlay.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

A templating tool for generating graphs using a structured data model.

The data model makes it possible to easily generate graphs directly
from code and makes it possible produce different looking graphs
from the same source.

Check out https://graphviz-overlay.readthedocs.io/ for more documentation.

Usage
=====

The ``graphviz-overlay`` executable reads from stdin and produces
dot source making it possible to produce a graph like this::

    graphviz-overlay$ cat examples/hello_world.json | graphviz-overlay graph
    graph G {
      hello -- world
    }

or a directed graph::

    cat examples/hello_world.json | graphviz-overlay digraph
    digraph G {
      hello -> world
    }


Features
========

Templating
----------

You can define your own overlays::

    import graphviz_overlay

    class MyOverlay(graphviz_overlay.GraphOverlay):
        pass


    ctx = graphviz_overlay.GraphContext()
    overlay = MyOverlay(ctx)

    model = {'edges': [{'from': 'hello', 'to': 'world'}]}
    print(overlay.draw(model))


Enhanced Styling
----------------

You can style the graph using classes defined in the model or
via a stylesheet specified as an argument making it possible to
define all shared attributes between edges, nodes
and graphs. You can of course also specify the attributes directly
on each element.

Every overlay you define can also define

Classes are defined as part of the model or as a separate `stylesheet`.

Functionality exposed depends on the overlay and it is possible
to define new ones. The basic overlays supports the following``graph`` and ``digraph``

Basic Overlay Support
=====================

The basic ``graph`` and ``digraph`` overlays add support for

Paths
-----

It is possible to define paths (the term borrowed from graph theory).

By defining a path you can control how the final graph is created from
the model.

Path selection syntax supports negation.

You can include nodes, edges and subgraphs as part of a path.


Selection
---------

You can choose to include selected paths only, via the command-line.

You can also choose whether de-selected elements should be hidden
(i.e. with ``style=invis``, to maintain placement of other elements)
or remove the elements entirely from the final dot-source.


Highlight/Shade Elements
------------------------

You can choose to highlight and/or shade specific paths or subgraphs
from the command line

These are really just built-in classes and can be customized
any way you need.


Version History
===============

0.1.1:
  - Add initial documentation and project description

0.1.0:
  - ``graph``, ``digraph`` and ``er`` commands.
  - Support for ``--select``, ``--highlight`` and ``--shade``
    via paths.
  - Support for ranks
  - External stylesheet definition.
  - Nodes, edges, and graphs can have `classes`.
