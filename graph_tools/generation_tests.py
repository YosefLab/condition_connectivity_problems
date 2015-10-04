"""
This file tests graph generation functionality.
"""
from generation import *
from visualization import *


def test_create_sample_DCP_instance():
	graph, existence_for_node_time, connectivity_demands = create_sample_DCP_instance(node_count=1000, tree_count=10, tree_span=100)

	print("Graph has total weight " + str(graph.size()))

	draw_DCP_instance(graph, existence_for_node_time, connectivity_demands)






if __name__ == "__main__":
	test_create_sample_DCP_instance()