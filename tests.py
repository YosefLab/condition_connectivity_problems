"""
This file tests functionality in other modules.
"""
from graph_generation import *
import matplotlib.pyplot as pyplot


def test_create_sample_DCP_instance():
	graph, node_existence_times, connectivity_demands = create_sample_DCP_instance(node_count=100, tree_count=5, tree_span=30)

	print("Graph has total weight " + str(graph.size()))

	# Assign non-terminals red, terminals green
	color_for_node = {node : 'r' for node in graph.nodes()}
	for source, target, time in connectivity_demands:
		color_for_node[source] = 'g'
		color_for_node[target] = 'g'

	visualize_graph(graph, color_for_node)




def visualize_graph(G, color_for_node):
	node_sequence = []
	color_sequence = []
	for node, color in color_for_node.items():
		node_sequence += [node]
		color_sequence += [color]

	networkx.draw(G, nodelist=node_sequence, node_color=color_sequence)

	# Finer control over spring layout
	# networkx.draw(G, pos=networkx.spring_layout(G, iterations=20), nodelist=node_sequence, node_color=color_sequence)

	pyplot.savefig("test_graph.png")
	pyplot.show()






if __name__ == "__main__":
	test_create_sample_DCP_instance()