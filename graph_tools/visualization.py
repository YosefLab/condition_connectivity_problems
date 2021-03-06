"""
This file implements algorithms for generating sample graphs.
"""
import networkx
import matplotlib.pyplot as pyplot
import time, datetime


def draw_DCSN_instance(graph, existence_for_node_conditions, connectivity_demands):
	# Assign non-terminals red, terminals green
	color_for_node = {node : 'r' for node in graph.nodes()}
	for source, target, condition in connectivity_demands:
		color_for_node[source] = 'g'
		color_for_node[target] = 'g'

	node_sequence = []
	color_sequence = []
	for node, color in color_for_node.iteritems():
		node_sequence += [node]
		color_sequence += [color]

	# Label each node with its name
	node_labels = {node: node for node in graph.nodes_iter()}

	# Draw graph and save image
	networkx.draw(graph, nodelist=node_sequence, node_color=color_sequence, labels=node_labels)
	pyplot.savefig("test_graph.png")
	pyplot.show()


def print_edges_in_graph(graph, edges_per_line=5):
	edges_string = ''
	edges_printed_in_line = 0

	for u,v in graph.edges_iter():
		edges_string += '%s -> %s        ' % (u, v)
		edges_printed_in_line += 1
		if edges_printed_in_line >= edges_per_line:
			edges_printed_in_line = 0
			edges_string += '\n'

	print edges_string


def execution_time(start_time, end_time):
	execution_delta = datetime.timedelta(seconds=end_time - start_time)
	return execution_delta.days, execution_delta.seconds // 3600, (execution_delta.seconds // 60) % 60, execution_delta.seconds % 60


