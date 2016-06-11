# Dynamic Steiner Network / Dynamic Connectivity

This project implements an algorithm for solving the directed Steiner network problem in time-varying graphs. It also contains tools for generating interesting instances of the problem to test the feasibility of the algorithm in practice.


#### Problem Statement

Formally, the __(Node)-Dynamic Directed Steiner Network (ND-DSN)__ problem is the following: we are given

1. A weighted directed graph _G = (V,E,w)_.

2. An _existence function_ _ρ : V × [T] → {0,1}_ indicating whether each vertex exists at each time.

3. A set of _k_ time-sensitive _connectivity demands_ _D ⊆ V × V × [T]_.

The task is to find a subgraph _H ⊆ G_ of minimum total weight such that every demand _(a,b,t) ∈ D_ is satisfied: there exists an _a → b_ path in _H_ at time _t_.

_Note: Our code often refers to this problem by its previous name, the **Dynamic Connectivity Problem (DCP)**._

Theoretical aspects of this problem, as well as our algorithm, will be detailed in a forthcoming paper.


---
### Solving Dynamic Steiner Network Instances

The main ND-DSN solver is invoked by calling the following function in `/ILP_solver/ILP_solver.py`:

```python
# In the following, G is a NetworkX DiGraph, rho is a dictionary, and D is a list of triples. See the docstring for details.
solve_DCP_instance(graph=G, existence_for_node_time=rho, connectivity_demands=D, detailed_output=False)
```

_Note: This function works by modeling the instance as an integer linear program (ILP), then solving using an optimization library. Even instances of modest size can take prohibitive resources to solve._



### Generating Artificial Instances

We implement the following procedure for generating highly-structured random ND-DSN instances given parameters _|V|_, _β_, and _γ_:

1. Instantiate a pool of nodes _V_.

2. Independently sample _β_ directed trees. The _i_-th tree is built by uniformly sampling _γ_ nodes from _V_, making those nodes active at a new time _t<sub>i</sub>_, generating a random spanning tree on the nodes, and directing the edges so that a designated root node has a path to each leaf. A demand is then created from the root to each leaf at time _t<sub>i</sub>_.

3. Let the graph _G_ be the union of all the directed trees, with all edges having unit weight.

This procedure is implemented in the following function in `/graph_tools/generation.py`:

```python
# In the following, node_count = |V|, tree_count = β, and tree_span = γ
create_sample_DCP_instance(node_count=100, tree_count=10, tree_span=20)
```

To generate an instance and run the algorithm on it all at once, call the following function in `ILP_solver_tests.py`:

```python
test_solve_random_instance(node_count=100, tree_count=10, tree_span=20, detailed_output=False)
```


