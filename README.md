# Directed Condition Steiner Network

This project implements an algorithm for solving the Directed Steiner Network problem in condition-varying graphs. It also contains tools for generating interesting instances of the problem to test the feasibility of the algorithm in practice. We note that although this solver is focused on the node-varying case, it is shown in our theoretical paper that the node varying and edge varying cases are equivalent.


#### Problem Statement

Formally, the __(Node)-Directed Condition Steiner Network (DCSN)__ problem is the following: we are given

1. A series of weighted directed graphs _G<sub>1</sub> = (V<sub>1</sub>, E, w)_ , ...,  _G<sub>n</sub> = (V<sub>n</sub>, E, w)_ .

3. A set of _k_ condition-sensitive _connectivity demands_ _D ⊆ V × V × [C]_.

The task is to find a subgraph _H ⊆ G_ of minimum total weight such that every demand _(a,b,c) ∈ D_ is satisfied: there exists an _a → b_ path in _H_ at time _c_.

Theoretical aspects of this problem, as well as our algorithm, will be detailed in a forthcoming paper.


---
### Solving Directed Condition Steiner Network Instances

The main DCSN solver is invoked by calling the following function in `/ILP_solver/ILP_solver.py`:

```python
# In the following, G is a NetworkX DiGraph, rho is a dictionary corresponding to whether v is in V_c, and D is a list of triples. See the docstring for details.
solve_DCSN_instance(graph=G, existence_for_node_time=rho, connectivity_demands=D, detailed_output=False)
```

The single source DCSN solver is invoked similarly, by calling the following function in `/ILP_solver/ILP_solver.py`:

```python
# In the following, G is a NetworkX DiGraph, rho is a dictionary corresponding to whether v is in V_c, and D is a list of triples where the source is unique per condition. See the docstring for details.
solve_single_source_DCSN_instance(graph=G, existence_for_node_time=rho, connectivity_demands=D, detailed_output=False)
```


_Note_: This function works by modeling the instance as an integer linear program (ILP), then solving using an optimization library.



### Generating Artificial Instances

We implement the following procedure for generating highly-structured random DCSN instances given parameters __G__, _β_, _γ_, and __p__:

1. Give an underlying graph _G_, such as the human protein-protein interaction network, and fix a source node _s_.

2. Independently sample _β_ nodes reachable from _s_. Activate all nodes on the shortest path from _s_ to the node. Demands are added from _s_ to each demand.

3. Repeat this process for _γ_ conditions.

4. For all other nodes, set v to be included in V<sub>c</sub> with probability _p_.

This procedure is implemented in the following function in `/graph_tools/generation.py`:

```python
create_sample_DCSN_instance(graph, condition_count=100, demands_count_per_source = 100, node_active_prob=.75)
```

To view example instances and run the algorithm, please view `ILP_solver_tests.py`:
