"""
This file implements algorithms for generating sample graphs.
"""
import networkx
import random
import pickle


def create_sample_DCSN_instance(graph, condition_count=100, demands_count_per_source = 100, node_active_prob=.75):
	"""
	Generates a sample DCSN problem instance:
		- A directed graph with attribute 'weight' on all edges
		- Number of conditions to generate
		- Number of demands per node
		- Probability a node is active in any condition

	Returns:
		- A directed graph with attribute 'weight' on all edges
		- A dictionary from (node, condition) to existence {True, False}
		- A list of connectivity demands (source, target, condition)

	The graph is created by sampling trees (each on at most tree_span nodes) from a pool of nodes,
	then taking their union.
	"""


	# Map each (node, condition) to its existence, initially 0
	existence_for_node_condition = {(node, condition): 0 if random.uniform(0,1) < node_active_prob else 1 for node in graph.nodes() for condition in range(condition_count)}

	# List of connectivity demands in the form (source, target, condition)
	connectivity_demands = []

	# Sample a tree at each condition point
	nodes = graph.nodes()

	edges = {}
	source = random.choice(nodes)
	reachable_nodes_from_source = networkx.descendants(graph, source)
	while len(reachable_nodes_from_source) < demands_count_per_source:
		source = random.choice(nodes)
		reachable_nodes_from_source = networkx.descendants(graph, source)

	for condition in range(condition_count):
		print "Processing generated graph for c =", condition

		existence_for_node_condition[(source, condition)] = 1

		samples = random.sample(reachable_nodes_from_source, demands_count_per_source)

		for sample in samples:
			shortest_path_source_sample = networkx.shortest_path(graph, source, sample, weight='weight')


			for node in shortest_path_source_sample:
				existence_for_node_condition[(node, condition)] = 1
				nodes.append(node)
			for i in range(0, len(shortest_path_source_sample)-1):
				edge = [shortest_path_source_sample[i], shortest_path_source_sample[i+1]]
				edges[(edge[0],edge[1])] = graph[edge[0]][edge[1]]['weight']
			connectivity_demands += [(source, sample, condition)]


	total = 0
	for x,y in edges.items():
		total += y

	print "Total Cost of SP solution:", total
	return graph, existence_for_node_condition, connectivity_demands



def create_sample_tree(nodes, max_terminal_count=float('infinity')):
	"""
	Given a pool of nodes, samples a directed tree. Returns:
		- The directed tree
		- The source node
		- A list of terminal nodes

	Ensures that the number of terminals is at most max_terminal_count, though it may be fewer.
	"""
	# Copy nodes for safety
	nodes = list(nodes)

	# Build random (undirected) spanning tree
	undirected_tree = create_random_spanning_tree(nodes)

	# Randomly choose a source node
	source = random.choice(nodes)

	# Build directed tree with source as root
	directed_tree = directed_tree_from_undirected_tree(undirected_tree, source)

	# Declare some leaves to be terminals
	leaves = list(filter(lambda v: directed_tree.out_degree(v) == 0, directed_tree.nodes_iter()))
	terminals = leaves[0:min(len(leaves), max_terminal_count)]

	return directed_tree, source, terminals



def create_node_pool(node_count):
	"""
	Returns a list of nodes (integers 0,...,99).
	"""
	return range(node_count)



def create_random_spanning_tree(nodes):
	"""
	Given a list of nodes, returns a Graph object which is a uniform random spanning tree on the nodes.

	Runs a randomized Kruskal's algorithm.
	"""
	components = networkx.utils.UnionFind()
	tree = networkx.Graph()
	tree.add_nodes_from(nodes)
	possible_edges = [(u,v) for u in nodes for v in nodes if u != v]

	# Shuffle edges to make function stochastic
	random.shuffle(possible_edges)

	# Insert all nodes into disjoint sets structure
	[components[node] for node in nodes]

	# Build spanning tree by adding edges that don't induce a cycle
	for u,v in possible_edges:
		if components[u] != components[v]:
			components.union(u,v)
			tree.add_edge(u,v)

	return tree



def directed_tree_from_undirected_tree(undirected_tree, root):
	"""
	Given an undirected tree and a root node in that tree, returns a directed tree where the edges
	are oriented away from the root.
	"""
	directed_tree = networkx.DiGraph()

	def explore_node(u):
		"""
		Performs DFS from the given node of the undirected tree. Along the way, adds directed edges
		to its children in the directed tree.
		"""
		for v in undirected_tree.neighbors(u):
			# If neighbor v is not u's parent, then it should be marked as a child
			if not directed_tree.has_edge(v,u):
				directed_tree.add_edge(u,v)
				explore_node(v)

	explore_node(root)

	return directed_tree







