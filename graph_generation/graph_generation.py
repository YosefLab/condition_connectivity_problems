"""
This file implements algorithms for generating sample graphs.
"""
import networkx
import random


def create_sample_DCP_instance(node_count=100, tree_count=10, tree_span=float('infinity')):
	"""
	Generates a sample DCP problem instance:
		- A directed graph with attribute 'weight' on all edges
		- A dictionary from (node, time) to existence {True, False}
		- A list of connectivity demands (source, target, time)

	The graph is created by sampling trees (each on at most tree_span nodes) from a pool of nodes,
	then taking their union.
	"""
	nodes = create_node_pool(node_count)

	# Map each (node, time) to its existence, initially 0
	existence_for_node_time = {(node,time): 0 for node in nodes for time in range(tree_count)}

	# List of connectivity demands in the form (source, target, time)
	connectivity_demands = []

	# Sample a tree at each time point
	trees = []
	for time in range(tree_count):

		# Choose a random subset of the nodes from which to build the tree
		tree_nodes = random.sample(nodes, min(len(nodes), tree_span))

		# Sample a tree
		tree, source, terminals = create_sample_tree(tree_nodes)

		# Record tree
		trees += [tree]

		# Record existence of tree nodes at the current time
		for node in tree.nodes_iter():
			existence_for_node_time[node,time] = 1

		# Record connectivity demands for this tree/time
		for target in terminals:
			connectivity_demands += [(source, target, time)]


	# Union of trees
	graph = networkx.compose_all(trees)

	return graph, existence_for_node_time, connectivity_demands



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
	return [i for i in range(node_count)]



def create_random_spanning_tree(nodes):
	"""
	Given a list of nodes, returns a Graph object which is a uniform random spanning tree on the nodes.

	Runs a randomized Kruskal's algorithm.
	"""
	components = networkx.utils.UnionFind()
	tree = networkx.Graph()
	possible_edges = [(u,v) for u in nodes for v in nodes]

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






