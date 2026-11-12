"""Dependency DAG validation and impacted downstream contract discovery."""
def impacted(edges, changed):
    graph = {}
    nodes = set()
    for upstream, downstream in edges:
        if upstream == downstream: raise ValueError("self dependency")
        graph.setdefault(upstream, set()).add(downstream)
        nodes.update((upstream, downstream))
    visiting, visited = set(), set()
    def visit(n):
        if n in visiting: raise ValueError("dependency cycle")
        if n in visited: return
        visiting.add(n)
        for child in graph.get(n, ()): visit(child)
        visiting.remove(n)
        visited.add(n)
    for n in sorted(nodes): visit(n)
    result = set()
    def walk(n):
        for child in graph.get(n, ()):
            if child not in result:
                result.add(child)
                walk(child)
    walk(changed)
    return sorted(result)
