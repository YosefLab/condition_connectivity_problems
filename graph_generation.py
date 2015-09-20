"""
This file implements algorithms for generating sample graphs.
"""
import networkx
import random


def create_sample_DCP_instance(node_count=100, tree_count=10):
	"""
	Generates a sample DCP problem instance:
		- A directed graph
		- A dictionary specifying node existence times
		- A list of connectivity demands

	The graph is created by sampling trees from a pool of nodes, then taking their union.
	"""
	node_pool = create_node_pool(node_count)

	# Map from each node to a set of time indices at which it is active
	node_existence_times = {node : set() for node in node_pool}

	# List of connectivity demands in the form (source, target, time)
	connectivity_demands = []

	# Sample a tree at each time point
	trees = []
	for time in range(tree_count):

		# TODO: CHOOSE A RANDOM SUBSET OF NODES TO BUILD TREE FROM

		# Sample a tree
		tree, source, terminals = create_sample_tree(node_pool)

		# Record existence of tree nodes at the current time
		for node in tree.nodes_iter():
			node_existence_times[node].add(time)

		# Record connectivity demands for this tree/time
		for target in terminals:
			connectivity_demands += [(source, target, time)]


	union_of_trees = networkx.compose_all(trees)

	return union_of_trees, node_existence_times, connectivity_demands



# TODO: ALLOW UPPER LIMIT ON NUMBER OF TERMINALS IN TREE
def create_sample_tree(node_pool):
	"""
	Given a pool of nodes, samples a directed tree. Returns:
		- The directed tree
		- The source node
		- A list of terminal nodes
	"""
	# Copy node pool for safety
	nodes = list(node_pool)

	# Build random (undirected) spanning tree
	undirected_tree = create_random_spanning_tree(nodes)

	# Randomly choose a source node
	source = random.choice(nodes)

	# Build directed tree with source as root
	directed_tree = directed_tree_from_undirected_tree(undirected_tree, source)

	# Declare all leaves to be terminals
	terminals = list(filter(lambda v: directed_tree.out_degree(v) == 0, directed_tree.nodes_iter()))

	return directed_tree, source, terminals



def create_node_pool(node_count):
	"""
	Returns a list of nodes (integers 0,...,99).
	"""
	return [i for i in range(node_count)]




def create_random_spanning_tree(nodes):
	"""
	Given a list of nodes, returns a Graph object which is a uniform random spanning tree on the nodes.
	"""






