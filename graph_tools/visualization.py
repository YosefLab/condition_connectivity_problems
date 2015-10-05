"""
This file implements algorithms for generating sample graphs.
"""
import networkx
import matplotlib.pyplot as pyplot


def draw_DCP_instance(graph, existence_for_node_time, connectivity_demands):
	# Assign non-terminals red, terminals green
	color_for_node = {node : 'r' for node in graph.nodes()}
	for source, target, time in connectivity_demands:
		color_for_node[source] = 'g'
		color_for_node[target] = 'g'

	node_sequence = []
	color_sequence = []
	for node, color in color_for_node.iteritems():
		node_sequence += [node]
		color_sequence += [color]

	networkx.draw(graph, nodelist=node_sequence, node_color=color_sequence)

	# Finer control over spring layout
	# networkx.draw(G, pos=networkx.spring_layout(G, iterations=20), nodelist=node_sequence, node_color=color_sequence)

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