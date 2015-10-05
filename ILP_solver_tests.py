"""
This file tests ILP solver functionality.
"""
from graph_tools.generation import *
from graph_tools.visualization import *
from ILP_solver.ILP_solver import *
import matplotlib.pyplot as pyplot


def test_solve_random_instance(detailed_output=False):
	"""
	Tests the DCP ILP solver on a randomly generated instance.
	"""
	graph, existence_for_node_time, connectivity_demands = create_sample_DCP_instance(
		node_count=100,
		tree_count=10,
		tree_span=20
	)

	if detailed_output:
		draw_DCP_instance(graph, existence_for_node_time, connectivity_demands)

	print('Testing random DCP instance.')
	print('Total weight: ' + str(graph.size(weight='weight')))
	if detailed_output:
		print('Connectivity demands: ' + str([(demand[0], demand[1]) for demand in connectivity_demands]))

	solve_DCP_instance(graph, existence_for_node_time, connectivity_demands, detailed_output)


def test_solve_path_instance(feasible=True, detailed_output=False):
	"""
	Tests the DCP ILP solver on a simple path at two time points.
	"""
	print('Testing path instance, should be ' + ('feasible' if feasible else 'infeasible'))

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

	solve_DCP_instance(graph, existence_for_node_time, connectivity_demands, detailed_output)


def test_solve_tree_instance(multiple_times=True, detailed_output=False):
	"""
	Tests the DCP ILP solver on a directed tree at two time points.
	"""
	print('Testing tree instance with ' + ('multiple times' if multiple_times else 'single time'))

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

	solve_DCP_instance(graph, existence_for_node_time, connectivity_demands, detailed_output)


def test_solve_anti_greedy_instance(detailed_output=False):
	"""
	Tests the DCP ILP solver on a small instance that penalizes greedy behavior.
	"""
	print('Testing anti-greedy instance')

	graph = networkx.DiGraph()

	graph.add_edge(1, 2, weight=3)
	graph.add_edge(1, 3, weight=1)
	graph.add_edge(3, 4, weight=5)
	graph.add_edge(4, 2, weight=1)

	existence_for_node_time = {
		(1,1): 1,
		(2,1): 1,
		(3,1): 1,
		(4,1): 1,
		(1,2): 0,
		(2,2): 0,
		(3,2): 1,
		(4,2): 1
	}

	connectivity_demands = [(1,2,1), (3,4,2)]

	solve_DCP_instance(graph, existence_for_node_time, connectivity_demands, detailed_output)




if __name__ == "__main__":
	tests = [
		# (test_solve_path_instance, {'feasible': True}),
		# (test_solve_path_instance, {'feasible': False}),

		# (test_solve_tree_instance, {'multiple_times': True}),
		# (test_solve_tree_instance, {'multiple_times': False}),

		(test_solve_random_instance, {}),

		# (test_solve_anti_greedy_instance, {}),
	]

	for test, kwargs in tests:
		print( '-----------------------------------------------------------------------' )
		test(detailed_output=False, **kwargs)
		print( '-----------------------------------------------------------------------\n\n' )


