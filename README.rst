#####
About
#####

Generate templated graphviz source files from structured data

Why
===

The Graphviz dot language offers a descriptive and flexible way
to define graphs of various sorts. However, I think it also has
some issues.

- Maintenance/small changes quickly becomes a hassle, especially
  when you want to produce similar looking graphs. I.e. highlighting
  certain elements, or selecting specific parts (it is possible
  to render just subgraphs, but for me that is not always what
  I want).

- The layout engine is not exactly what you would call intuitive
  and getting it to do your bidding takes time and effort to
  discover. Also, you need to pull (and remember those) weird
  tricks. Basically, it's just boilerplate work.

- The defaults does not really produce pretty looking graphs, and
  customizing the design is often tedious work and for me often
  ends up involving a bunch of copy paste. For SVG output
  stylesheets are supported, however that doesn't really work
  with common cooperation tools (such as slack and github)

So, to address these issues I decided to put together a tool
to address all that (and more).


Usage
=====

CLI
---

The ``graphviz-overlay`` executable reads from stdin and produces
dot source::

    cat examples/simple.json | graphviz-overlay


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
