"""
This file implements algorithms for generating sample graphs.
"""
import networkx
import random


def create_sample_graph(node_count=100, tree_count=10):
	"""
	Generates a sample graph by
		- defining a pool of nodes,
		- sampling trees on those nodes, and
		- taking the union of those trees.
	"""
	node_pool = create_node_pool(node_count)
	trees = [create_sample_tree(node_pool) for _ in tree_count]
	union_of_trees = networkx.compose_all(trees)


def create_sample_tree(node_pool, terminal_count):
	"""
	Given a pool of nodes, generates a sample tree by sampling
		- a source node
		- internal nodes
		- terminal nodes
	from the pool and building a tree from them.
	"""
	# Ensure at least one source and one internal node
	assert terminal_count + 2 <= len(node_pool)

	# Copy node pool for safety
	nodes = list(node_pool)

	# Sample source, internals, terminals
	random.shuffle(nodes)
	terminal_nodes = nodes[:terminal_count]
	source_node = nodes[terminal_count]
	internal_nodes = nodes[terminal_count+1:]

	# Assemble a tree from nodes
	sample_tree = create_random_spanning_tree(nodes)

	return sample_tree



def create_node_pool(node_count):
	"""
	Returns a list of nodes (integers 0,...,99).
	"""
	return [i for i in range(node_count)]




def create_random_spanning_tree(nodes):
	"""
	Given a list of nodes, returns a Graph object which is a uniform random spanning tree on the nodes.
	"""






