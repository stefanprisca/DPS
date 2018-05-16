import numpy as np
import sys
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

x = sys.argv[1]

def f(x):
	return {
		'a' : undirected_graph_1,
		'b' : undirected_graph_2
	}[x]

undirected_graph_1 = csr_matrix([[0, 8, 0, 3],
						[0, 0, 2, 5],
						[0, 0, 0, 6],
						[0, 0, 0, 0]])
						
undirected_graph_2 = csr_matrix([[0, 2, 3, 0, 0, 0, 0, 0],
								[0, 0, 0, 4, 0, 0, 0, 9],
								[0, 0, 0, 6, 0, 0, 8, 0],
								[0, 0, 0, 0, 0, 6, 4, 0],
								[0, 0, 0, 0, 0, 0, 0, 3],
								[0, 0, 0, 0, 0, 0, 0, 2],
								[0, 0, 0, 0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0, 0, 0, 0]])
	
mst = minimum_spanning_tree(f(x))


print ("-----------------------------------------")
print ("----------- Undirected graph ------------")
print ("-----------------------------------------")

print (f(x))

print ("--------------------------------------------")
print ("----------- Minimum Spanning Tree ----------")
print ("--------------------------------------------")

print (mst)