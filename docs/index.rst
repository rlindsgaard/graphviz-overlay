###########################################
Welcome to graphiz-overlay's documentation!
###########################################

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents:

   examples

Graphviz-overlay is a templating tool for generating graphs.

It uses a data-structure for defining graphviz element making
it possible to generate different graphs based on the  the same
model and customizing them at the same time.

It adds functionality and customization lacking in graphviz but
does not take anything away. Full control of the produced dot
source code is maintained.

Usage
=====

CLI
---

The ``graphviz-overlay`` executable reads from stdin and produces
dot source::

    cat examples/simple.json | graphviz-overlay graph


Features
========

Functionality exposed depends on the overlay, overlays should
derive from the basic ``graph`` and ``digraph`` overlays including

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


Highlight/Shade
------------------

You can choose to highlight and/or shade specific paths making
specific parts of the graph stand out.

These are really just built-in classes ready for customization.


Classes
-------

You can specify your own classes defining attributes to add for an
element containing that class.

Classes are defined as part of the model or as a separate `stylesheet`.


Defining The Model
==================

Graphviz Attributes
-------------------

You define graphviz attributes directly on an element as
dictionary elements ``"attr": "value"``.

They will be added to the element in the final dot-source. Only
attributes applicable for an element will be added.
Special rules apply for:

style:
  The value needs to be defined as a list. Order of application
  is respected and is maintained as a set. If added as part of a
  class, the last definition wins.

rank:
  Ranks are interpreted differently as they are treated as first
  class elements. See :ref:`ranks_detailed`


.. _graphviz-overlay_attributes:

Graphviz-overlay defined attributes
-----------------------------------

visible (bool):
  Indicates whether the element should be displayed. Translates into
  ``style=invis`` false.
  If used on a graph, subgraphs will still be displayed (contrary to
  graphviz behaviour)

  .. note::
    You can still set::

      "style": ["invis"]

    if you want that behaviour.

cluster (bool):
  Applies to subgraphs only. Renders the graph as a cluster similar to
  prefix the subgraph name with ``cluster_``.

paths list(str):
  A list of paths the element is included in (i.e. an element can be part
  of several paths)


.. _graph_model:

Graphs
------
::

    {
        "nodes": {
            ...
        },
        "edges": {
            ...
        },
        "subgraphs": {
            ...
        },
        "ranks": {
            ...
        },
        "styles": {
            ...
        }
        "graph": {

        },
        "node": {

        },
        "edge": {

        }
    }

Whether it produced a graph or a digraph is decided by what overlay
you use.


Subgraphs
---------

The dictionary key defines the subgraph name. The value follows
the :ref:`graph_model` structure recursively.::

  "subgraphs": {
      "mysubgraph": {
          "nodes": {
              ...
          },
          "edges": {
              ...
          }
          "subgraphs": {
              "mysubsubgraph": {
                  ...
              }
          }
      }
  }

- Defining subgraphs you automatically create a path. Subgraph paths
  are delimited with ".". In the example you can choose "mysubgraph"
  or "mysubgraph.mysubsubgraph"

- The label is not inherited by a parent graph (but is set to '') by
  default.

- You create a cluster either by naming it with the cluster prefix (
  in that case you need to include it in the path) or by using `cluster`
  as defined in :ref:`graphviz-overlay_attributes`

.. note::

 ``"styles":`` are currently only interpreted from the main graph.


Nodes
-----

The dictionary key defines the node name, this is used when defining
edges.

::

    "nodes": {
        "name": {
            "attr": "value",
            "classes": [...]
        }
        ...
    }


Edges
-----
A list of dictionaries

::

    "edges": [
        {
            "from": "node1",
            "to": "node2"
        }
    ]


.. _ranks_detailed:

Ranks
-----

Ranks only apply to nodes. You define a rank with a label::

  "rank": "myrank"

on the graph or subgraph you define where the rank is defined.::

  "ranks": {
      "myrank": "same"
  }

key is the label you chose, the value is either "same", "min" or "max".

.. tip::
  You can choose to rank nodes the same between subgraphs, remember
  to add ``"newrank": True`` to the main graph though.


HTML-labels
-----------

You can add html-like labels how you usually would define the label.

Tables are supported via giving the label a dictionary value::

    "label": {
        "border": "1",
        "trs": [
            [
                {
                    "colspan": "2",
                    "value": "Record"
                }
            ],
            [
                {
                    "port": "p0",
                    "value": "foo"
                },
                {
                    "port": "p1",
                    "value": "bar"
                }
            ]
        ]
    }

All the html attributes are supported and are parsed as part of
the html.


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
