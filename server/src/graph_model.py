"""
Operations with graphical models
"""

import numpy as np
import re
import copy
import networkx as nx
import itertools
import random

from collections import Counter

from src.quickbb_api import gen_cnf, run_quickbb
from src.logger_setup import log

random.seed(0)

QUICKBB_COMMAND = './quickbb/run_quickbb_64.sh'
QUICKBB_COMMAND = './quickbb/quickbb_64'
MAXIMAL_MEMORY = 100000000   # 100000000 64bit complex numbers


def relabel_graph_nodes(graph, label_dict=None):
    """
    Relabel graph nodes to consequtive numbers. If label
    dictionary is not provided, a relabelled graph and a
    dict {new : old} will be returned. Otherwise, the graph
    is relabelled (and returned) according to the label
    dictionary and an inverted dictionary is returned.

    Parameters
    ----------
    graph : networkx.Graph
            graph to relabel
    label_dict : optional, dict-like
            dictionary for relabelling {old : new}

    Returns
    -------
    new_graph : networkx.Graph
            relabeled graph
    label_dict : dict
            {new : old} dictionary for inverse relabeling
    """
    if label_dict is None:
        label_dict = {old: num for num, old in
                      enumerate(graph.nodes(data=False), 1)}
        new_graph = nx.relabel_nodes(graph, label_dict, copy=True)
    else:
        new_graph = nx.relabel_nodes(graph, label_dict, copy=True)

    # invert the dictionary
    label_dict = {val: key for key, val in label_dict.items()}

    return new_graph, label_dict


def get_peo(old_graph):
    """
    Calculates the elimination order for an undirected
    graphical model of the circuit. Optionally finds `n_qubit_parralel`
    qubits and splits the contraction over their values, such
    that the resulting contraction is lowest possible cost.
    Optionally fixes the values border nodes to calculate
    full state vector.

    Parameters
    ----------
    graph : networkx.Graph
            graph of the undirected graphical model to decompose

    Returns
    -------
    peo : list
          list containing indices in loptimal order of elimination
    treewidth : int
          treewidth of the decomposition
    """

    cnffile = 'output/quickbb.cnf'
    initial_indices = old_graph.nodes()
    graph, label_dict = relabel_graph_nodes(old_graph)

    if graph.number_of_edges() - graph.number_of_selfloops() > 0:
        gen_cnf(cnffile, graph)
        out_bytes = run_quickbb(cnffile, QUICKBB_COMMAND)

        # Extract order
        m = re.search(b'(?P<peo>(\d+ )+).*Treewidth=(?P<treewidth>\s\d+)',
                      out_bytes, flags=re.MULTILINE | re.DOTALL)

        peo = [int(ii) for ii in m['peo'].split()]

        # Map peo back to original indices
        peo = [label_dict[pp] for pp in peo]

        treewidth = int(m['treewidth'])
    else:
        peo = []
        treewidth = 1

    # find the rest of indices which quickBB did not spit out.
    # Those include isolated nodes (don't affect
    # scaling and may be added to the end of the variables list)
    # and something else

    isolated_nodes = nx.isolates(old_graph)
    peo = peo + sorted(isolated_nodes)

    # assert(set(initial_indices) - set(peo) == set())
    missing_indices = set(initial_indices)-set(peo)
    # The next line needs review. Why quickBB misses some indices?
    # It is here to make program work, but is it an optimal order?
    peo = peo + sorted(list(missing_indices))

    assert(sorted(peo) == sorted(initial_indices))
    log.info('Final peo from quickBB:\n{}'.format(peo))

    return peo, treewidth


def get_cost_by_node(graph, node):
    """
    Outputs the cost corresponding to the
    contraction of the node in the graph

    Parameters
    ----------
    graph : networkx.Graph or networkx.MultiGraph
               Graph containing the information about the contraction
    node : node of the graph (such that graph can be indexed by it)

    Returns
    -------
    memory : int
              Memory cost for contraction of node
    flops : int
              Flop cost for contraction of node
    """
    neighbors = list(graph[node])

    # We have to find all unique tensors which will be contracted
    # in this bucket. They label the edges coming from
    # the current node (may be multiple edges between
    # the node and its neighbor).
    # Then we have to count only the number of unique tensors.
    if graph.is_multigraph():
        edges_from_node = [list(graph[node][neighbor].values())
                           for neighbor in neighbors]
        tensor_hash_tags = [edge['hash_tag'] for edges_of_neighbor
                            in edges_from_node
                            for edge in edges_of_neighbor]
    else:
        tensor_hash_tags = [graph[node][neighbor]['hash_tag']
                            for neighbor in neighbors]
    # The order of tensor in each term is the number of neighbors
    # having edges with the same hash tag + 1 (the node itself)
    neighbor_tensor_orders = {hash_tag: count+1 for
                              hash_tag, count in
                              Counter(tensor_hash_tags).items()}
    # memory estimation: the size of the result + all sizes of terms
    memory = 2**(len(neighbors))
    for order in neighbor_tensor_orders.values():
        memory += 2**order

    n_unique_tensors = len(set(tensor_hash_tags))

    if n_unique_tensors == 0:
        n_multiplications = 0
    else:
        n_multiplications = n_unique_tensors - 1

    # there are number_of_terms - 1 multiplications and 1 addition
    # repeated size_of_the_result*size_of_contracted_variables
    # times for each contraction
    flops = (2**(len(neighbors) + 1)       # this is addition
             + 2**(len(neighbors) + 1)*n_multiplications)

    return memory, flops


def eliminate_node(graph, node):
    """
    Eliminates node according to the tensor contraction rules.
    A new clique is formed, which includes all neighbors of the node.

    Parameters
    ----------
    graph : networkx.Graph or networkx.MultiGraph
            Graph containing the information about the contraction
            GETS MODIFIED IN THIS FUNCTION
    node : node to contract (such that graph can be indexed by it)

    Returns
    -------
    None
    """

    neighbors = list(graph[node])

    # Delete node itself from the list of its neighbors.
    # This eliminates possible self loop
    while node in neighbors:
        neighbors.remove(node)

    if len(neighbors) > 1:
        edges = itertools.combinations(neighbors, 2)
    elif len(neighbors) == 1:
        # This node had a single neighbor, add self loop to it
        edges = [[neighbors[0], neighbors[0]]]
    else:
        # This node had no neighbors
        edges = None

    graph.remove_node(node)

    if edges is not None:
        graph.add_edges_from(
            edges, tensor=f'E{node}',
            hash_tag=hash((f'E{node}', tuple(neighbors), random.random())))


def cost_estimator(old_graph):
    """
    Estimates the cost of the bucket elimination algorithm.
    The order of elimination is defined by node order (if ints are
    used as nodes then it will be the number of integers).

    Parameters
    ----------
    old_graph : networkx.Graph or networkx.MultiGraph
               Graph containing the information about the contraction
    Returns
    -------
    memory : list
              Memory cost for steps of the bucket elimination algorithm
    flops : list
              Flop cost for steps of the bucket elimination algorithm
    """
    graph = copy.deepcopy(old_graph)
    nodes = sorted(graph.nodes)

    results = []
    for n, node in enumerate(nodes):
        memory, flops = get_cost_by_node(graph, node)
        results.append((memory, flops))

        eliminate_node(graph, node)

    return tuple(zip(*results))
