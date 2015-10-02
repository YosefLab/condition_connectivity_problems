"""
This file tests ILP solver functionality.
"""
from graph_generation.graph_generation import *
from ILP_solver.ILP_solver import *
import matplotlib.pyplot as pyplot


def test_solve_DCP_instance():
	graph, existence_for_node_time, connectivity_demands = create_sample_DCP_instance(node_count=10, tree_count=2, tree_span=7)

	print("Graph has total weight " + str(graph.size()))

	solve_DCP_instance(graph, existence_for_node_time, connectivity_demands)







if __name__ == "__main__":
	test_solve_DCP_instance()