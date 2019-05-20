"""
This module implements interface to QuickBB program.
QuickBB is quite cranky to its input
"""
import networkx as nx
import subprocess
import os

from src.logger_setup import log


def gen_cnf(filename, old_graph):
    """
    Genarate QuickBB input file for the graph.
    We always convert MultiGraph's to Graph' and remove self loops,
    because QuickBB does not understand these situations.

    Parameters
    ----------
    filename : str
           Output file name
    graph : networkx.Graph or networkx.MultiGraph
           Undirected graphical model
    """
    graph = nx.Graph(old_graph)
    v = graph.number_of_nodes()
    e = graph.number_of_edges() - graph.number_of_selfloops()
    log.info(f"generating config file {filename}")
    cnf = "c a configuration of -qtree simulator\n"
    cnf += f"p cnf {v} {e}\n"

    # Convert possible MultiGraph to Graph (avoid repeated edges)
    for edge in graph.edges():
        u, v = edge
        # print only if this is not a self-loop
        if u != v:
            cnf += '{} {} 0\n'.format(u, v)

    # print("cnf file:",cnf)
    with open(filename, 'w+') as fp:
        fp.write(cnf)


def run_quickbb(cnffile,
                command='./quickbb_64',
                outfile='output/quickbb_out.qbb',
                statfile='output/quickbb_stat.qbb'):
    """
    Run QuickBB program and collect its output

    Parameters
    ----------
    cnffile : str
         Path to the QuickBB input file
    command : str, optional
         QuickBB command name
    outfile : str, optional
         QuickBB output file
    statfile : str, optional
         QuickBB stat file
    Returns
    -------
    output : str
         Process output
    """
    # try:
    #     os.remove(outfile)
    #     os.remove(statfile)
    # except FileNotFoundError as e:
    #     log.warn(e)
    #     pass

    sh = command + " "
    sh += "--min-fill-ordering "
    sh += "--time 60 "
    # this makes Docker process too slow and sometimes fails
    # sh += f"--outfile {outfile} --statfile {statfile} "
    sh += f"--cnffile {cnffile} "
    log.info("excecuting quickbb: "+sh)
    process = subprocess.Popen(
        sh.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        log.error(error)
    log.info(output)
    # with open(outfile, 'r') as fp:
    #     log.info("OUTPUT:\n"+fp.read())
    # with open(statfile, 'r') as fp:
    #     log.info("STAT:\n"+fp.read())

    return output
