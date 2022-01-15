########
Examples
########

Examples are inspired by https://graphviz.org/gallery/.

.. contents:: Examples
  :depth: 2
  :local:


Hello World
===========

https://graphviz.org/Gallery/directed/hello.html

Model:

    .. graphviz::

        digraph G {
        	hello -> world
        }


.. literalinclude:: ../examples/hello_world.json
    :caption: hello_world.json


Command::

    $ cat examples/hello_world.json | graphviz-overlay digraph > hello_world.dot


Generated source:

    .. code-block::
        :caption: hello_world.dot

        digraph G {
        	hello -> world
        }



Clusters
========

https://graphviz.org/Gallery/directed/cluster.html

Model:

    .. graphviz::

        digraph G {
        	start [shape=Mdiamond]
        	end [shape=Msquare]
        	subgraph cluster_0 {
        		graph [color=lightgrey label="process #1" style=filled]
        		node [color=white style=filled]
        		a0 -> a1
        		a1 -> a2
        		a2 -> a3
        	}
        	subgraph cluster_1 {
        		graph [color=blue label="process #2" style=solid]
        		node [style=filled]
        		b0 -> b1
        		b1 -> b2
        		b2 -> b3
        	}
        	start -> a0
        	start -> b0
        	a1 -> b3
        	b2 -> a3
        	a3 -> a0
        	a3 -> end
        	b3 -> end
        }


.. literalinclude:: ../examples/cluster.json
    :caption: cluster.json


Command::

    $ cat examples/cluster.json | graphviz-overlay digraph > cluster.dot


Generated source:

    .. code-block::
        :caption: cluster.dot

        digraph G {
        	start [shape=Mdiamond]
        	end [shape=Msquare]
        	subgraph cluster_0 {
        		graph [color=lightgrey label="process #1" style=filled]
        		node [color=white style=filled]
        		a0 -> a1
        		a1 -> a2
        		a2 -> a3
        	}
        	subgraph cluster_1 {
        		graph [color=blue label="process #2" style=solid]
        		node [style=filled]
        		b0 -> b1
        		b1 -> b2
        		b2 -> b3
        	}
        	start -> a0
        	start -> b0
        	a1 -> b3
        	b2 -> a3
        	a3 -> a0
        	a3 -> end
        	b3 -> end
        }



Entity-Relation Data Model
==========================

https://graphviz.org/Gallery/undirected/ER.html

Model:

    .. graphviz::

        graph G {
        	graph [layout=neato]
        	course [shape=box]
        	course_name [label=name]
        	course_name -- course
        	course_code [label=code]
        	course_code -- course
        	institute [shape=box]
        	institute_name [label=name]
        	institute_name -- institute
        	student [shape=box]
        	student_name [label=name]
        	student_name -- student
        	student_number [label=number]
        	student_number -- student
        	student_grade [label=grade]
        	student_grade -- student
        	course_institute [label="C-I" color=lightgrey shape=diamond style=filled]
        	course -- course_institute [label=n]
        	course_institute -- institute [label=1]
        	student_course [label="S-C" color=lightgrey shape=diamond style=filled]
        	student -- student_course [label=m]
        	student_course -- course [label=n]
        	student_institute [label="S-I" color=lightgrey shape=diamond style=filled]
        	student -- student_institute [label=n]
        	student_institute -- institute [label=1]
        }


.. literalinclude:: ../examples/er.json
    :caption: er.json


Command::

    $ cat examples/er.json | graphviz-overlay er > er.dot


Generated source:

    .. code-block::
        :caption: er.dot

        graph G {
        	graph [layout=neato]
        	course [shape=box]
        	course_name [label=name]
        	course_name -- course
        	course_code [label=code]
        	course_code -- course
        	institute [shape=box]
        	institute_name [label=name]
        	institute_name -- institute
        	student [shape=box]
        	student_name [label=name]
        	student_name -- student
        	student_number [label=number]
        	student_number -- student
        	student_grade [label=grade]
        	student_grade -- student
        	course_institute [label="C-I" color=lightgrey shape=diamond style=filled]
        	course -- course_institute [label=n]
        	course_institute -- institute [label=1]
        	student_course [label="S-C" color=lightgrey shape=diamond style=filled]
        	student -- student_course [label=m]
        	student_course -- course [label=n]
        	student_institute [label="S-I" color=lightgrey shape=diamond style=filled]
        	student -- student_institute [label=n]
        	student_institute -- institute [label=1]
        }

