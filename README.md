# Dynamic Steiner Network / Dynamic Connectivity

This project implements an algorithm for solving the directed Steiner network problem in time-varying graphs. It also contains tools for generating interesting instances of the problem to test the feasibility of the algorithm in practice.


#### Problem Statement

Formally, the __(Node)-Dynamic Directed Steiner Network (ND-DSN)__ problem is the following: we are given

1. A weighted directed graph _G = (V,E,w)_.

2. An _existence function_ _ρ : V × [T] → {0,1}_ indicating whether each vertex exists at each time.

3. A set of _k_ time-sensitive _connectivity demands_ _D ⊆ V × V × [T]_.

The task is to find a subgraph _H ⊆ G_ of minimum total weight such that every demand _(a,b,t) ∈ D_ is satisfied: there exists an _a → b_ path in _H_ at time _t_.

_Our code often refers to this problem by its previous name, the **Dynamic Connectivity Problem (DCP)**._



---
### Solving Dynamic Steiner Network Instances

The main ND-DSN solver is invoked by calling the following function in `/ILP_solver/ILP_solver.py`:

```python
solve_DCP_instance(graph, existence_for_node_time, connectivity_demands, detailed_output=False)
```

_Note:_ This function works by modeling the instance as an integer linear program (ILP), then solving using an optimization library. Even instances of modest size can take prohibitive resources to solve.



### Generating Artificial Instances

_Coming soon._



