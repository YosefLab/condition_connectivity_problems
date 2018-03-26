"""
This file tests ILP solver functionality.
"""

from ILP_solver.ILP_solver import *

def test_solve_path_instance(feasible=True, detailed_output=False):
	"""
	Tests the DCSN ILP solver on a simple path at two conditions .
	"""
	print 'Testing path instance, should be ' + ('feasible' if feasible else 'infeasible')

	graph = networkx.DiGraph()

	graph.add_path([1,2,3,4])
	for u,v in graph.edges_iter():
		graph[u][v]['weight'] = 1
	
	existence_for_node_condition = {
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

	solve_DCSN_instance(graph, existence_for_node_condition, connectivity_demands, detailed_output)


def test_solve_tree_instance(multiple_conditions=True, detailed_output=False):
	"""
	Tests the DCSN ILP solver on a directed tree at two conditions.
	"""
	print 'Testing tree instance with ' + ('multiple conditions' if multiple_conditions else 'single condition')

	graph = networkx.DiGraph()

	graph.add_path([1,2,3])
	graph.add_path([1,2,4])
	for u,v in graph.edges_iter():
		graph[u][v]['weight'] = 1

	existence_for_node_condition = {
		(1,1): 1,
		(2,1): 1,
		(3,1): 1,
		(4,1): 1,
		(1,2): 1,
		(2,2): 1,
		(3,2): 1,
		(4,2): 1
	}

	connectivity_demands = [(1,3,1), (1,4,2 if multiple_conditions else 1)]

	solve_DCSN_instance(graph, existence_for_node_condition, connectivity_demands, detailed_output)


def test_solve_anti_greedy_instance(detailed_output=False):
	"""
	Tests the DCSN ILP solver on a small instance that penalizes greedy behavior.
	"""
	print 'Testing anti-greedy instance'

	graph = networkx.DiGraph()

	graph.add_edge(1, 2, weight=3)
	graph.add_edge(1, 3, weight=1)
	graph.add_edge(3, 4, weight=5)
	graph.add_edge(4, 2, weight=1)

	existence_for_node_condition = {
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

	solve_DCSN_instance(graph, existence_for_node_condition, connectivity_demands, detailed_output)


def test_solve_single_source_instance(detailed_output=False):
	"""
	Tests the DCSN ILP solver on a simple path at two conditions .
	"""
	print 'Testing single source instance'

	graph = networkx.DiGraph()

	graph.add_path([1, 2, 3])
	graph.add_path([1, 2, 4])
	for u, v in graph.edges_iter():
		graph[u][v]['weight'] = 1

	existence_for_node_condition = {
		(1, 1): 1,
		(2, 1): 1,
		(3, 1): 1,
		(4, 1): 1,
		(1, 2): 1,
		(2, 2): 1,
		(3, 2): 1,
		(4, 2): 1
	}

	connectivity_demands = [(1, 4, 1), (1, 3, 1), (1,4,2), (1,3,2)]

	solve_single_source_DCSN_instance(graph, existence_for_node_condition, connectivity_demands, detailed_output)


if __name__ == "__main__":
	tests = [
		 #(test_solve_path_instance, {'feasible': True}),
		 #(test_solve_path_instance, {'feasible': False}),

		 #(test_solve_tree_instance, {'multiple_conditions': True}),
		 #(test_solve_tree_instance, {'multiple_conditions': False}),

		#(test_solve_random_instance, {'node_count': 100, 'tree_count': 10, 'tree_span': 20}),

		 #(test_solve_anti_greedy_instance, {}),
	]

	for test, kwargs in tests:
		print '-----------------------------------------------------------------------'
		test(detailed_output=False, **kwargs)
		print '-----------------------------------------------------------------------\n\n'


