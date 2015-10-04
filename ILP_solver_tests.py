"""
This file tests ILP solver functionality.
"""
from graph_generation.graph_generation import *
from ILP_solver.ILP_solver import *
import matplotlib.pyplot as pyplot


def test_solve_random_DCP_instance():
	graph, existence_for_node_time, connectivity_demands = create_sample_DCP_instance(node_count=10, tree_count=2, tree_span=7)

	print("Graph has total weight " + str(graph.size()))

	solve_DCP_instance(graph, existence_for_node_time, connectivity_demands)


def test_solve_path_instance(feasible=True):
	"""
	Tests the DCP ILP solver on a simple path at two time points.
	"""
	graph = networkx.DiGraph()

	graph.add_path([1,2,3,4])
	for u,v in graph.edges_iter():
		graph[u][v]['weight'] = 1
	
	existence_for_node_time = {
		(1,1): 1,
		(2,1): 1,
		(3,1): 1,
		(4,1): 1,
		(1,2): 1,
		(2,2): 1,
		(3,2): 1,
		(4,2): 1 if feasible else 0
	}

	connectivity_demands = [(1,4,1), (1,4,2)]

	solve_DCP_instance(graph, existence_for_node_time, connectivity_demands)


def test_solve_tree_instance(multiple_times=True):
	"""
	Tests the DCP ILP solver on a directed tree at two time points.
	"""
	graph = networkx.DiGraph()

	graph.add_path([1,2,3])
	graph.add_path([1,2,4])
	for u,v in graph.edges_iter():
		graph[u][v]['weight'] = 1

	existence_for_node_time = {
		(1,1): 1,
		(2,1): 1,
		(3,1): 1,
		(4,1): 1,
		(1,2): 1,
		(2,2): 1,
		(3,2): 1,
		(4,2): 1
	}

	connectivity_demands = [(1,3,1), (1,4,2 if multiple_times else 1)]

	solve_DCP_instance(graph, existence_for_node_time, connectivity_demands)



if __name__ == "__main__":
	print('Testing path instance, should be feasible')
	test_solve_path_instance(feasible=True)
	print('Testing path instance, should be infeasible')
	test_solve_path_instance(feasible=False)

	print('Testing tree instance with multiple times')
	test_solve_tree_instance(multiple_times=True)
	print('Testing tree instance with single time')
	test_solve_tree_instance(multiple_times=False)

	test_solve_random_DCP_instance()


