"""Successive shortest augmenting path min-cost flow, integer capacities."""
from dataclasses import dataclass
from collections import deque
from .model import Scenario

@dataclass(frozen=True)
class Result:
    shipments: dict[str, int]
    fulfilled: int
    requested: int
    total_cost: int
    unmet: dict[str, int]

class Edge:
    def __init__(self, to, reverse, capacity, cost):
        self.to, self.reverse, self.capacity, self.cost = to, reverse, capacity, cost

def optimize(scenario: Scenario) -> Result:
    scenario.validate()
    sources = sorted(scenario.supply)
    destinations = sorted(scenario.demand)
    n = len(sources) + len(destinations) + 2
    start, end = n - 2, n - 1
    graph = [[] for _ in range(n)]
    def add(u, v, cap, cost):
        a = Edge(v, len(graph[v]), cap, cost)
        b = Edge(u, len(graph[u]), 0, -cost)
        graph[u].append(a); graph[v].append(b)
        return a
    src_index = {name:i for i,name in enumerate(sources)}
    dst_index = {name:i+len(sources) for i,name in enumerate(destinations)}
    for name in sources:
        add(start, src_index[name], scenario.supply[name], 0)
    for name in destinations:
        add(dst_index[name], end, scenario.demand[name], 0)
    edges = {}
    for route in sorted(scenario.routes, key=lambda x:(x.source,x.destination)):
        edges[(route.source,route.destination)] = (add(src_index[route.source],dst_index[route.destination],route.capacity,route.unit_cost),route.capacity)
    flow = cost = 0
    requested = sum(scenario.demand.values())
    while flow < requested:
        dist = [float('inf')]*n
        previous = [None]*n
        dist[start] = 0
        # Bellman-Ford supports negative residual reverse edges.
        for _ in range(n-1):
            changed = False
            for u in range(n):
                if dist[u] == float('inf'): continue
                for j,e in enumerate(graph[u]):
                    if e.capacity and dist[u]+e.cost < dist[e.to]:
                        dist[e.to] = dist[u]+e.cost
                        previous[e.to] = (u,j)
                        changed = True
            if not changed: break
        if previous[end] is None: break
        increment = requested-flow
        node = end
        while node != start:
            u,j = previous[node]
            increment = min(increment,graph[u][j].capacity)
            node = u
        node = end
        while node != start:
            u,j = previous[node]
            edge = graph[u][j]
            edge.capacity -= increment
            graph[node][edge.reverse].capacity += increment
            cost += increment*edge.cost
            node = u
        flow += increment
    shipments = {f"{a}->{b}":initial-edge.capacity for (a,b),(edge,initial) in edges.items()}
    unmet = {name:scenario.demand[name]-sum(shipments.get(f"{s}->{name}",0) for s in sources) for name in destinations}
    return Result(shipments,flow,requested,cost,unmet)
