"""
Operations to load/contract quantum circuits. All functions
operating on Buckets (without any specific framework) should
go here.
"""

import itertools
import random
import networkx as nx
import src.operators as ops
import src.utils as utils

from src.logger_setup import log

random.seed(0)


def circ2buckets(circuit):
    """
    Takes circuit in the form of list of gate lists, builds
    its contraction graph and variable buckets. Buckets contain tuples
    corresponding to quantum gates and qubits they act on. Each bucket
    corresponds to a variable. Each bucket can hold gates acting on it's
    variable of variables with higher index.

    Parameters
    ----------
    circuit : list of lists
            quantum circuit as returned by
            :py:meth:`operators.read_circuit_file`

    Returns
    -------
    buckets : list of lists
            list of lists (buckets)
    g : networkx.Graph
            contraction graph of the circuit
    """
    # import pdb
    # pdb.set_trace()
    g = nx.Graph()

    qubit_count = len(circuit[0])
    # print(qubit_count)

    # Let's build an undirected graph for variables
    # we start from 1 here to avoid problems with quickbb
    for i in range(1, qubit_count+1):
        g.add_node(i, name=utils.num_to_alnum(i))

    # Build buckets for bucket elimination algorithm along the way.
    # we start from 1 here to follow the variable indices
    buckets = []
    for ii in range(1, qubit_count+1):
        buckets.append(
            [[f'O{ii}', [ii]]]
        )

    current_var = qubit_count
    layer_variables = list(range(1, qubit_count+1))

    for layer in reversed(circuit[1:-1]):
        for op in layer:
            if not op.diagonal:
                # Non-diagonal gate adds a new variable and
                # an edge to graph
                var1 = layer_variables[op._qubits[0]]
                var2 = current_var+1

                g.add_node(var2, name=utils.num_to_alnum(var2))
                g.add_edge(var1, var2)

                # Append gate 2-variable tensor to the first variable's
                # bucket. This yields buckets containing variables
                # in increasing order (starting at least with bucket's
                # variable)
                buckets[var1-1].append(
                    [op.name, [var1, var2]]
                )

                # Create a new variable
                buckets.append(
                    []
                )

                current_var += 1
                layer_variables[op._qubits[0]] = current_var

            if isinstance(op, ops.cZ):
                var1 = layer_variables[op._qubits[0]]
                var2 = layer_variables[op._qubits[1]]

                # cZ connects two variables with an edge
                g.add_edge(
                    var1, var2
                )

                # append cZ gate to the bucket of lower variable index
                var1, var2 = sorted([var1, var2])
                buckets[var1-1].append(
                    [op.name, [var1, var2]]
                )

            if isinstance(op, ops.T):
                var1 = layer_variables[op._qubits[0]]
                # Do not add any variables (buckets), but add tensor
                # to the bucket
                buckets[var1-1].append(
                    [op.name, [var1, ]]
                )

    # add last layer of measurement vectors
    for qubit_idx, var in zip(range(1, qubit_count+1),
                              layer_variables):
        buckets[var-1].append(
            [f'I{qubit_idx}', [var, ]]
        )

    v = g.number_of_nodes()
    e = g.number_of_edges()

    log.info(f"Generated graph with {v} nodes and {e} edges")
    log.info(f"last index contains from {layer_variables}")

    # with io.StringIO() as outstrings:
    #     aj = nx.adjacency_matrix(g)
    #     np.savetxt(outstrings, aj.toarray(), delimiter=" ",fmt='%i')
    #     s = outstrings.getvalue()
    #     log.info("Adjacency matrix:\n" + s.replace('0','-'))

    # plt.figure(figsize=(10,10))
    # nx.draw(g, with_labels=True)
    # plt.savefig('graph.eps')
    return buckets, g


def buckets2graph(buckets):
    """
    Takes buckets and produces a corresponding undirected graph. Single
    variable tensors are coded as self loops and there may be
    multiple parallel edges.

    Parameters
    ----------
    buckets : list of lists

    Returns
    -------
    graph : networkx.MultiGraph
            contraction graph of the circuit
    """
    graph = nx.MultiGraph()

    # Let's build an undirected graph for variables
    for n, bucket in enumerate(buckets):
        for element in bucket:
            tensor, variables = element
            for var in variables:
                graph.add_node(var, name=utils.num_to_alnum(var))
            if len(variables) > 1:
                edges = itertools.combinations(variables, 2)
            else:
                # If this is a single variable tensor, add self loop
                var = variables[0]
                edges = [[var, var]]
            graph.add_edges_from(
                edges, tensor=tensor,
                hash_tag=hash(
                    (tensor, tuple(variables), random.random())
                )
            )

    return graph
