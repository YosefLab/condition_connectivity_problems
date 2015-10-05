from gurobipy import *
import networkx
from graph_tools.visualization import *


def solve_DCP_instance(graph, existence_for_node_time, connectivity_demands):
	"""
	Given a DCP problem instance:
		- A directed graph with attribute 'weight' on all edges
		- A dictionary from (node, time) to existence {True, False}
		- A list of connectivity demands (source, target, time)

	returns a minimum weight subgraph that satisfies the demands.

	Works by reducing to simple DCP (sDCP).
	"""

	def transform_DCP_to_sDCP(graph, existence_for_node_time, connectivity_demands):
		"""
		Given a DCP instance:
			- A directed graph with attribute 'weight' on all edges
			- A dictionary from (node, time) to existence {True, False}
			- A list of connectivity demands (source, target, time)

		returns a simple DCP (sDCP) instance:
			- A directed graph
			- An existence dictionary
			- A list of connectivity demands, all at different times
			- A single source node
			- A single target node
		"""
		# Initialize new graph to original graph
		new_graph = graph.copy()

		# Create a supply of new nodes for reduction
		max_node = max(graph.nodes_iter()) # Ensure we do not overwrite existing node
		new_node_stack = range(max_node + 2 * (len(connectivity_demands) + 1), max_node, -1)

		# Map old times to new (all distinct) times
		new_times = range(len(connectivity_demands)) # [1,...,k]
		original_time_for_new_time = {}
		for new_time, (_, _, original_time) in enumerate(connectivity_demands):
			original_time_for_new_time[new_time] = original_time # Map i --> i-th demand's original time

		# Add universal source and target
		source = new_node_stack.pop()
		target = new_node_stack.pop()
		new_graph.add_nodes_from([source, target])

		# Add source and target buffer nodes
		buffer_nodes_and_times = []
		for new_time, (original_source, original_target, original_time) in enumerate(connectivity_demands):
			# universal source --> buffer --> original source
			source_buffer = new_node_stack.pop()
			new_graph.add_edge(source, source_buffer, weight=0)
			new_graph.add_edge(source_buffer, original_source, weight=0)

			# original target --> buffer --> universal target
			target_buffer = new_node_stack.pop()
			new_graph.add_edge(original_target, target_buffer, weight=0)
			new_graph.add_edge(target_buffer, target, weight=0)

			# Record existence time for buffer nodes
			buffer_nodes_and_times += [(source_buffer, new_time), (target_buffer, new_time)]

		# Set node existence dictionary for new graph, under new time points
		new_existence_for_node_time = {(v,t): 0 for v in new_graph.nodes_iter() for t in new_times}
		# Map times for nodes in original graph
		for new_time in new_times:
			original_time = original_time_for_new_time[new_time]
			for node in graph.nodes_iter():
				new_existence_for_node_time[node, new_time] = existence_for_node_time[node, original_time]
		# Universal source and target exist at all times
		for new_time in new_times:
			new_existence_for_node_time[source, new_time] = 1
			new_existence_for_node_time[target, new_time] = 1
		# Map times for buffer nodes
		for buffer_node, new_time in buffer_nodes_and_times:
			new_existence_for_node_time[buffer_node, new_time] = 1

		# Create new connectivity demands
		new_connectivity_demands = [(source, target, new_time) for new_time in new_times]

		print( '-----------------------------------------------------------------------' )
		print('Reduced DCP instance to sDCP instance. Buffer nodes added:')
		for buffer_node, new_time in buffer_nodes_and_times:
			print( str(buffer_node) + ' at time ' + str(new_time) )

		return new_graph, new_existence_for_node_time, new_connectivity_demands, source, target

	def recover_DCP_solution_from_sDCP_solution(subgraph, source, target):
		"""
		Given a solution to an instance of sDCP:
			- A subgraph of the original graph
			- A universal source node
			- A universal target node

		returns the subgraph that is the solution to the original DCP instance.
		"""
		# Clean up universal source and target, and buffers
		subgraph.remove_nodes_from([source_buffer for source_buffer in subgraph.successors(source)])
		subgraph.remove_nodes_from([target_buffer for target_buffer in subgraph.predecessors(target)])
		subgraph.remove_nodes_from([source, target])

		print( '-----------------------------------------------------------------------' )
		print('Recovered DCP solution from sDCP solution. Edges in minimal subgraph:')
		print_edges_in_graph(subgraph)

		return subgraph

	# Reduce to sDCP
	simple_graph, simple_existence_for_node_time, simple_connectivity_demands, source, target = transform_DCP_to_sDCP(graph, existence_for_node_time, connectivity_demands)
	simple_subgraph = solve_sDCP_instance(simple_graph, simple_existence_for_node_time, simple_connectivity_demands)
	if simple_subgraph is not None:
		return recover_DCP_solution_from_sDCP_solution(simple_subgraph, source, target)
	else:
		return None # No solution



def solve_sDCP_instance(graph, existence_for_node_time, connectivity_demands):
	"""
	Given a simple DCP (sDCP) problem instance:
		- A directed graph with attribute 'weight' on all edges
		- A dictionary from (node, time) to existence {True, False}
		- A list of connectivity demands (source, target, time)
			ASSUMPTION: each demand is at a different time

	returns a minimum weight subgraph that satisfies the demands.
	"""
	# MODEL SETUP
	# Infer a list of times
	times = list(set([time for source, target, time in connectivity_demands]))

	# Sources get +1 sourceflow, targets get -1, other nodes 0
	sourceflow = {(v,t): 0 for v in graph.nodes_iter() for t in times}
	for source, target, time in connectivity_demands:
		sourceflow[source,time] = 1
		sourceflow[target,time] = -1

	# Create empty optimization model
	model = Model('dynamic_connectivity')

	# Create variables d_{uvt}
	edge_time_variables = {}
	for t in times:
		for u,v in graph.edges_iter():
			edge_time_variables[u,v,t] = model.addVar(vtype=GRB.BINARY, name='edge_time_%s_%s_%s' % (u,v,t))

	# Create variables d_{uv}
	edge_variables = {}
	for u,v in graph.edges_iter():
		edge_variables[u,v] = model.addVar(vtype=GRB.BINARY, name='edge_%s_%s' % (u,v))

	model.update()


	# CONSTRAINTS
	# Edge decision constraints (an edge is chosen if it is chosen at any time)
	for t in times:
		for u,v in graph.edges_iter():
			model.addConstr(edge_variables[u,v] >= edge_time_variables[u,v,t])


	# Existence constraints (can only route flow through active nodes)
	for t in times:
		for u,v in graph.edges_iter():
			model.addConstr(edge_time_variables[u,v,t] <= existence_for_node_time[u,t])
			model.addConstr(edge_time_variables[u,v,t] <= existence_for_node_time[v,t])

	# Flow conservation constraints
	for t in times:
		for v in graph.nodes_iter():
			model.addConstr(
				quicksum(edge_time_variables[u,v,t] for u in graph.predecessors_iter(v)) + sourceflow[v,t] ==
				quicksum(edge_time_variables[v,w,t] for w in graph.successors_iter(v))
			)


	# OBJECTIVE
	# Minimize total subgraph weight
	objective_expression = quicksum(edge_variables[u,v] * graph[u][v]['weight'] for u,v in graph.edges_iter())
	model.setObjective(objective_expression, GRB.MINIMIZE)


	# SOLVE AND RECOVER SOLUTION
	print( '-----------------------------------------------------------------------' )
	model.optimize()

	# Recover minimal subgraph
	subgraph = networkx.DiGraph()
	if model.status == GRB.status.OPTIMAL:
		value_for_edge = model.getAttr('x', edge_variables)
		for u,v in graph.edges_iter():
			if value_for_edge[u,v] > 0:
				subgraph.add_edge(u, v, weight=graph[u][v]['weight'])

		# Print solution
		print( '-----------------------------------------------------------------------' )
		print('Solved sDCP instance. Edges in minimal subgraph:')
		print_edges_in_graph(subgraph)

	# Return solution iff found
	return subgraph if model.status == GRB.status.OPTIMAL else None


