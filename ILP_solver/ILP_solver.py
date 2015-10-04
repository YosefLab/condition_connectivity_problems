from gurobipy import *

def solve_DCP_instance(graph, existence_for_node_time, connectivity_demands):
	"""
	Given a DCP problem instance:
		- A directed graph with attribute 'weight' on all edges
		- A dictionary from (node, time) to existence {True, False}
		- A list of connectivity demands (source, target, time)
			ASSUMPTION: each demand is at a different time
			TODO: remove this assumption

	returns a list of edges of minimal weight that satisfies the demands.
	"""

	# MODEL SETUP
	# Infer a list of times
	times = list(set([time for source, target, time in connectivity_demands]))

	# Sources get +1 sourceflow, targets get -1, other nodes 0
	sourceflow = {(v,t): 0 for v in graph.nodes() for t in times}
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


	print( '======================================================' )
	# SOLVE
	model.optimize()


	# PRINT SOLUTION
	if model.status == GRB.status.OPTIMAL:
		print('Edges in minimal subgraph:')
		value_for_edge = model.getAttr('x', edge_variables)
		for u,v in graph.edges_iter():
			if value_for_edge[u,v] > 0:
				print( '%s -> %s' % (u, v) )

	print( '======================================================\n\n' )



