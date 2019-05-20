"""
Here we will collect functions to interact with the web visualization
code
"""
import src.operators as ops
import src.optimizer as opt
import src.graph_model as gm
import json
from networkx.readwrite import json_graph
import networkx as nx


def graph_to_d3json(graph):
    """
    Converts a graph to json node-link file

    Parameters
    ----------
    graph : networkx.MultiGraph
             Graph to convert

    Returns
    -------
    res: string
            converted json string
    """
    data = json_graph.node_link_data(graph)
    res = json.dumps(data)
    return res


def read_graph_from_circfile(filename):
    """
    Reads the expression graph from circuit file

    Parameters
    ----------
    filename : str
              File containing the circuit in Boixo's format

    Returns
    -------
    graph : networkx.MultiGraph
            Graph representing the contraction
    """
    # load circuit
    n_qubits, circuit = ops.read_circuit_file(filename)

    # get contraction graph (node order is arbitrary)
    buckets, _ = opt.circ2buckets(circuit)
    graph = opt.buckets2graph(buckets)
    return graph


def copy_to_simple(graph):
    """
    Makes a copy of graph and removes from it all duplicate edges
    and self loops

    Parameters
    ----------
    graph : networkx.Graph or networkx.MultiGraph

    Returns
    -------
    sgraph : networkx.Graph or networkx.MultiGraph
    """
    g = graph.copy()
    g.remove_edges_from(graph.selfloop_edges())
    sg = nx.Graph(g)
    return sg

def quickBB_ordering(graph):
    """
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
    peo,tw = gm.get_peo(graph)
    print("QBB returned:",peo,tw)
    return peo,tw

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
    return gm.get_cost_by_node(graph, node)


def get_contraction_expression(graph, node):
    """
    For a given node returns a corresponding contraction expression

    Parameters
    ----------
    graph : networkx.Graph or networkx.MultiGraph
            Graph containing the information about the contraction
    node : node to contract (such that graph can be indexed by it)

    Returns
    -------
    expr : str
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
        tensors_with_hash_tags = [
            (edge['hash_tag'], edge['tensor'])
            for edges_of_neighbor in edges_from_node
            for edge in edges_of_neighbor]
    else:
        tensors_with_hash_tags = [
            (graph[node][neighbor]['hash_tag'],
             graph[node][neighbor]['tensor'])
            for neighbor in neighbors]

    # This will remove any duplicates in the list of tuples
    tensor_by_hash_tag = dict(tensors_with_hash_tags)

    # Collect tensor indices
    indices_by_hash_tag = {hash_tag: [node, ] for hash_tag
                           in tensor_by_hash_tag.keys()}
    if graph.is_multigraph():
        for neighbor in neighbors:
            edges_from_node = list(graph[node][neighbor].values())
            for edge in edges_from_node:
                hash_tag = edge['hash_tag']
                if neighbor != node:  # ignore self loops
                    indices_by_hash_tag[hash_tag].append(neighbor)
    else:
        for neighbor in neighbors:
            hash_tag = graph[node][neighbor]['hash_tag']
            if neighbor != node:  # ignore self loops
                indices_by_hash_tag[hash_tag].append(neighbor)

    # Finally find alphanumeric names of indices
    node_names = {node: graph.node[node]['name']}
    for neighbor in neighbors:
        node_names.update({neighbor: graph.node[neighbor]['name']})

    # Build the expression string
    # First build what the resulting tensor will be
    expr = f'E{node}(' + ','.join(node_names[neighbor]
                                  for neighbor in neighbors) + ')'
    expr = expr + ' = ' + expr + ' + '

    # Build contraction terms
    terms = []
    for hash_tag, tensor in tensor_by_hash_tag.items():
        term = tensor + '(' + ','.join(
            node_names[index]
            for index in indices_by_hash_tag[hash_tag]) + ')'
        terms.append(term)

    expr += '*'.join(terms)

    return expr


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
    gm.eliminate_node(graph, node)


if __name__ == "__main__":
    # Test API
    graph = read_graph_from_circfile('inst_2x2_7_0.txt')
    node = 2
    mem, flop = get_cost_by_node(graph, node)
    expr = get_contraction_expression(graph, node)

    print(f'Memory for contraction of node {node}: {mem}')
    print(f'Flops for contraction of node {node}: {flop}')
    print('Expression:')
    print(expr)
