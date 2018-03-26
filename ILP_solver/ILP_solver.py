from gurobipy import *
import networkx
from graph_tools.visualization import *
import time as python_time
from collections import defaultdict


def solve_DCSN_instance(graph, existence_for_node_condition, connectivity_demands, detailed_output=False):
	"""
	Given a CSN problem instance:
		- A directed graph with attribute 'weight' on all edges
		- A dictionary from (node, condition) to existence {True, False}
		- A list of connectivity demands (source, target, condition)

	returns a minimum weight subgraph that satisfies the demands.

	Works by reducing to DCSP .
	"""

	def transform_DCSN_to_DCSP(graph, existence_for_node_condition, connectivity_demands, detailed_output=False):
		"""
		Given a DCSN instance:
			- A directed graph with attribute 'weight' on all edges
			- A dictionary from (node, condition) to existence {True, False}
			- A list of connectivity demands (source, target, condition)

		returns a DCSP instance:
			- A directed graph
			- An existence dictionary
			- A list of connectivity demands, all at different conditions
			- A single source node
			- A single target node
		"""
		start_time = time.time()

		# Initialize new graph to original graph
		new_graph = graph.copy()

		# Create a supply of new nodes for reduction
		max_node = len(graph.nodes())  # Ensure we do not overwrite existing node
		new_node_stack = range(max_node + 2 * (len(connectivity_demands) + 1), max_node, -1)

		# Map old conditions to new (all distinct) conditions
		new_conditions = range(len(connectivity_demands))  # [1,...,k]
		original_condition_for_new_condition = {}
		for new_condition, (_, _, original_condition) in enumerate(connectivity_demands):
			original_condition_for_new_condition[new_condition] = original_condition  # Map i --> i-th demand's original condition

		# Add universal source and target
		source = new_node_stack.pop()
		target = new_node_stack.pop()
		new_graph.add_nodes_from([source, target])

		# Add source and target buffer nodes
		buffer_nodes_and_conditions = []
		for new_condition, (original_source, original_target, original_condition) in enumerate(connectivity_demands):
			# universal source --> buffer --> original source
			source_buffer = new_node_stack.pop()
			new_graph.add_edge(source, source_buffer, weight=0)
			new_graph.add_edge(source_buffer, original_source, weight=0)

			# original target --> buffer --> universal target
			target_buffer = new_node_stack.pop()
			new_graph.add_edge(original_target, target_buffer, weight=0)
			new_graph.add_edge(target_buffer, target, weight=0)

			# Record existence condition for buffer nodes
			buffer_nodes_and_conditions += [(source_buffer, new_condition), (target_buffer, new_condition)]

		# Set node existence dictionary for new graph, under new conditions
		new_existence_for_node_condition = {(v, c): 0 for v in new_graph.nodes_iter() for c in new_conditions}
		# Map conditions for nodes in original graph
		for new_condition in new_conditions:
			original_condition = original_condition_for_new_condition[new_condition]
			for node in graph.nodes_iter():
				new_existence_for_node_condition[node, new_condition] = existence_for_node_condition[node, original_condition]
		# Universal source and target exist at all conditions
		for new_condition in new_conditions:
			new_existence_for_node_condition[source, new_condition] = 1
			new_existence_for_node_condition[target, new_condition] = 1
		# Map conditions for buffer nodes
		for buffer_node, new_condition in buffer_nodes_and_conditions:
			new_existence_for_node_condition[buffer_node, new_condition] = 1

		# Create new connectivity demands
		new_connectivity_demands = [(source, target, new_condition) for new_condition in new_conditions]

		# Print information
		print('-----------------------------------------------------------------------')
		print('Reduced DCSN instance to DCSP instance.')
		if detailed_output:
			print('Buffer nodes added:')
			for buffer_node, new_condition in buffer_nodes_and_conditions:
				print(str(buffer_node) + ' at condition ' + str(new_condition))

		end_time = time.time()
		days, hours, minutes, seconds = execution_time(start_time, end_time)
		print('DCSN -> DCSP instance transformation took %s days, %s hours, %s minutes, %s seconds' % (
		days, hours, minutes, seconds))

		return new_graph, new_existence_for_node_condition, new_connectivity_demands, source, target

	def recover_DCSN_solution_from_DCSP_solution(subgraph, source, target, detailed_output=False):
		"""
		Given a solution to an instance of DCSP:
			- A subgraph of the original graph
			- A universal source node
			- A universal target node

		returns the subgraph that is the solution to the original DCSN instance.
		"""
		start_time = time.time()

		# Clean up universal source and target, and buffers
		subgraph.remove_nodes_from([source_buffer for source_buffer in subgraph.successors(source)])
		subgraph.remove_nodes_from([target_buffer for target_buffer in subgraph.predecessors(target)])
		subgraph.remove_nodes_from([source, target])

		# Print information
		print('-----------------------------------------------------------------------')
		print('Recovered DCSN solution from DCSP solution.')
		if detailed_output:
			print('Edges in minimal subgraph:')
			print_edges_in_graph(subgraph)

		end_time = time.time()
		days, hours, minutes, seconds = execution_time(start_time, end_time)
		print('DCSP -> DCSN solution recovery took %s days, %s hours, %s minutes, %s seconds' % (
		days, hours, minutes, seconds))

		return subgraph

	# Reduce to DCSP
	simple_graph, simple_existence_for_node_condition, simple_connectivity_demands, source, target = transform_DCSN_to_DCSP(
		graph, existence_for_node_condition, connectivity_demands, detailed_output)

	simple_subgraph = solve_DCSP_instance(simple_graph, simple_existence_for_node_condition, simple_connectivity_demands,
										  detailed_output)

	if simple_subgraph is not None:
		return recover_DCSN_solution_from_DCSP_solution(simple_subgraph, source, target, detailed_output)
	else:
		return None  # No solution


def solve_DCSP_instance(graph, existence_for_node_condition, connectivity_demands, detailed_output=False):
	"""
	Given a DCSP problem instance:
		- A directed graph with attribute 'weight' on all edges
		- A dictionary from (node, condition) to existence {True, False}
		- A list of connectivity demands (source, target, condition)
			ASSUMPTION: each demand is at a different condition

	returns a minimum weight subgraph that satisfies the demands.
	"""
	print 'Attempting to solve instance'
	start_time = python_time.time()

	# MODEL SETUP
	# Infer a list of conditions
	conditions = list(set([condition for source, target, condition in connectivity_demands]))

	# Sources get +1 sourceflow, targets get -1, other nodes 0
	sourceflow = {(v, c): 0 for v in graph.nodes_iter() for c in conditions}
	for source, target, condition in connectivity_demands:
		sourceflow[source, condition] = 1
		sourceflow[target, condition] = -1

	# Create empty optimization model
	model = Model('Directed_Condition_Shortest_Path')

	print 'Attempting to solve instance'
	# Create variables d_{uvt}
	edge_condition_variables = {}
	for c in conditions:
		for u, v in graph.edges_iter():
			edge_condition_variables[u, v, c] = model.addVar(vtype=GRB.BINARY, name='edge_condition_%s_%s_%s' % (u, v, c))

	# Create variables d_{uv}
	edge_variables = {}
	for u, v in graph.edges_iter():
		edge_variables[u, v] = model.addVar(vtype=GRB.BINARY, name='edge_%s_%s' % (u, v))

	model.update()

	# CONSTRAINTS
	# Edge decision constraints (an edge is chosen if it is chosen at any condition)
	for c in conditions:
		for u, v in graph.edges_iter():
			model.addConstr(edge_variables[u, v] >= edge_condition_variables[u, v, c])

	# Existence constraints (can only route flow through active nodes)
	for c in conditions:
		for u, v in graph.edges_iter():
			model.addConstr(edge_condition_variables[u, v, c] <= existence_for_node_condition[u, c])
			model.addConstr(edge_condition_variables[u, v, c] <= existence_for_node_condition[v, c])

	# Flow conservation constraints
	for c in conditions:
		for v in graph.nodes_iter():
			model.addConstr(
				quicksum(edge_condition_variables[u, v, c] for u in graph.predecessors_iter(v)) + sourceflow[v, c] ==
				quicksum(edge_condition_variables[v, w, c] for w in graph.successors_iter(v))
			)

	print 'Attempting to solve instance'

	# OBJECTIVE
	# Minimize total subgraph weight
	objective_expression = quicksum(edge_variables[u, v] * graph[u][v]['weight'] for u, v in graph.edges_iter())
	model.setObjective(objective_expression, GRB.MINIMIZE)

	# SOLVE AND RECOVER SOLUTION
	print('-----------------------------------------------------------------------')
	model.optimize()

	# Recover minimal subgraph
	subgraph = networkx.DiGraph()
	if model.status == GRB.status.OPTIMAL:
		value_for_edge = model.getAttr('x', edge_variables)
		for u, v in graph.edges_iter():
			if value_for_edge[u, v] > 0:
				subgraph.add_edge(u, v, weight=graph[u][v]['weight'])

		# Print solution
		print('-----------------------------------------------------------------------')
		print('Solved DCSP instance.')
		if detailed_output:
			print('Edges in minimal subgraph:')
			print_edges_in_graph(subgraph)

	end_time = python_time.time()
	days, hours, minutes, seconds = execution_time(start_time, end_time)
	print('DCSP solving took %s days, %s hours, %s minutes, %s seconds' % (days, hours, minutes, seconds))

	# Return solution iff found
	return subgraph if model.status == GRB.status.OPTIMAL else None


def solve_single_source_DCSN_instance(graph, existence_for_node_condition, connectivity_demands, detailed_output=False):
	"""
	Given a single source DCSN problem instance (ie one source per condition):
		- A directed graph with attribute 'weight' on all edges
		- A dictionary from (node, condition) to existence {True, False}
		- A list of connectivity demands (source, target, condition)

	returns a minimum weight subgraph that satisfies the demands.
	"""
	print 'Attempting to solve instance'
	start_time = python_time.time()

	# MODEL SETUP
	# Infer a list of conditions
	conditions = list(set([condition for source, target, condition in connectivity_demands]))

	flow_per_condition = defaultdict(int)
	for source, target, condition in connectivity_demands:
		flow_per_condition[condition] += 1

	# Sources get +1 sourceflow, targets get -1, other nodes 0
	sourceflow = {(v, c): 0 for v in graph.nodes_iter() for c in conditions}
	for source, target, condition in connectivity_demands:
		print source, target
		sourceflow[source, condition] = flow_per_condition[condition]
		sourceflow[target, condition] = -1

	# Create empty optimization model
	model = Model('single_source_directed_condition_steiner_network')
	model.params.Threads = 1

	print 'Attempting to solve instance'
	# Create variables d_{uvc}
	edge_condition_variables = {}
	for c in conditions:
		for u, v in graph.edges_iter():
			edge_condition_variables[u, v, c] = model.addVar(vtype=GRB.INTEGER, lb=0, ub=flow_per_condition[c],
														name='edge_time_%s_%s_%s' % (u, v, c))

	# Create variables d_{uv}
	edge_variables = {}
	for u, v in graph.edges_iter():
		edge_variables[u, v] = model.addVar(vtype=GRB.BINARY, name='edge_%s_%s' % (u, v))

	model.update()

	# CONSTRAINTS
	# Edge decision constraints (an edge is chosen if it is chosen at any time)
	for c in conditions:
		for u, v in graph.edges_iter():
			model.addConstr(edge_variables[u, v] >= (
					edge_condition_variables[u, v, c] / (max(flow_per_condition.items(), key=lambda k: k[1])[1])))

	# Existence constraints (can only route flow through active nodes)
	for c in conditions:
		for u, v in graph.edges_iter():
			model.addConstr(edge_condition_variables[u, v, c] <= flow_per_condition[c] * existence_for_node_condition[u, c])
			model.addConstr(edge_condition_variables[u, v, c] <= flow_per_condition[c] * existence_for_node_condition[v, c])

	# Flow conservation constraints
	for c in conditions:
		for v in graph.nodes_iter():
			model.addConstr(
				quicksum(edge_condition_variables[u, v, c] for u in graph.predecessors_iter(v)) + sourceflow[v, c] ==
				quicksum(edge_condition_variables[v, w, c] for w in graph.successors_iter(v))
			)
			pass

	print 'Attempting to solve instance'

	# OBJECTIVE
	# Minimize total subgraph weight
	objective_expression = quicksum(edge_variables[u, v] * graph[u][v]['weight'] for u, v in graph.edges_iter())
	model.setObjective(objective_expression, GRB.MINIMIZE)

	# SOLVE AND RECOVER SOLUTION
	print('-----------------------------------------------------------------------')
	model.optimize()

	# Recover minimal subgraph
	subgraph = networkx.DiGraph()
	if model.status == GRB.status.OPTIMAL:
		value_for_edge = model.getAttr('x', edge_variables)
		for u, v in graph.edges_iter():
			if value_for_edge[u, v] > 0:
				subgraph.add_edge(u, v, weight=graph[u][v]['weight'])

		# Print solution
		print('-----------------------------------------------------------------------')
		print('Solved single source DCSN instance.')
		if detailed_output:
			print('Edges in minimal subgraph:')
			print_edges_in_graph(subgraph)

	end_time = python_time.time()
	days, hours, minutes, seconds = execution_time(start_time, end_time)
	print('Single source DCSN solving took %s days, %s hours, %s minutes, %s seconds' % (days, hours, minutes, seconds))

	# Return solution iff found
	return subgraph if model.status == GRB.status.OPTIMAL else None

