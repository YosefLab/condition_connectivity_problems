"""
This file tests functionality in other modules.
"""
from graph_generation import *
import matplotlib.pyplot as pyplot


def test_create_sample_DCP_instance():
	graph, node_existence_times, connectivity_demands = create_sample_DCP_instance(node_count=10, tree_count=4)
	visualize_graph(graph)






def visualize_graph(G):
	networkx.draw(G)
	pyplot.savefig("test_graph.png")
	pyplot.show()






if __name__ == "__main__":
	test_create_sample_DCP_instance()