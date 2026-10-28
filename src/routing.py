"""Task 2 - Fastest route, nearest ambulance (single traversal), best hospital."""
import heapq
from itertools import count

INF = float("inf")


class Graph:
    """Weighted graph, adjacency map. Junction labels can be any hashable."""

    def __init__(self, directed=False):
        self.directed = directed
        self.adj = {}

    def add_node(self, u):
        self.adj.setdefault(u, {})

    def add_edge(self, u, v, w):
        if w < 0:
            raise ValueError("Dijkstra needs non-negative travel times")
        self.add_node(u); self.add_node(v)
        self.adj[u][v] = w
        if not self.directed:
            self.adj[v][u] = w

    def remove_edge(self, u, v):
        """Road closure. O(1)."""
        self.adj.get(u, {}).pop(v, None)
        if not self.directed:
            self.adj.get(v, {}).pop(u, None)

    def copy(self):
        g = Graph(self.directed)
        g.adj = {u: dict(nb) for u, nb in self.adj.items()}
        return g

    def reversed(self):
        if not self.directed:
            return self
        g = Graph(True)
        for u in self.adj:
            g.add_node(u)
        for u, nb in self.adj.items():
            for v, w in nb.items():
                g.add_edge(v, u, w)
        return g


def nearest_target(graph, start, targets):
    """Dijkstra from `start`, STOP at the first target popped.
    Returns (time, path). (INF, []) if no target is reachable.
    Time O((V+E) log V) worst case; space O(V+E) (lazy-deletion heap).
    """
    targets = set(targets)
    if start not in graph.adj:
        return INF, []
    tie = count()
    dist, parent = {start: 0}, {start: None}
    heap = [(0, next(tie), start)]
    done = set()
    while heap:
        d, _, u = heapq.heappop(heap)
        if u in done:
            continue                      # stale entry (lazy deletion)
        done.add(u)
        if u in targets:                  # first popped target = nearest
            path = []
            while u is not None:
                path.append(u); u = parent[u]
            return d, path[::-1]
        for v, w in graph.adj[u].items():
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                parent[v] = u
                heapq.heappush(heap, (nd, next(tie), v))
    return INF, []


def fastest_route_to_hospital(graph, incident, hospitals):
    """Task 2a."""
    return nearest_target(graph, incident, hospitals)


def nearest_ambulance(graph, incident, ambulance_junctions):
    """Task 2b: ONE traversal from the incident, not one per ambulance.
    On a directed graph we need ambulance->incident times, so search the
    reversed graph from the incident (undirected: reversed() is the graph).
    Returns (time, path ambulance->incident).
    """
    t, path = nearest_target(graph.reversed(), incident, ambulance_junctions)
    return t, path[::-1]   # reorder so it reads ambulance -> incident


def multi_source_dijkstra(graph, sources):
    """Alternative view of 2b: all ambulances start at distance 0.
    Returns (dist, owner): dist[v] = time to nearest source, owner[v] = which one.
    Great when many incidents are queried against the same fleet snapshot.
    """
    tie = count()
    dist, owner, heap = {}, {}, []
    for s in sources:
        dist[s] = 0; owner[s] = s
        heap.append((0, next(tie), s))
    heapq.heapify(heap)
    done = set()
    while heap:
        d, _, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        for v, w in graph.adj[u].items():
            if d + w < dist.get(v, INF):
                dist[v] = d + w
                owner[v] = owner[u]
                heapq.heappush(heap, (d + w, next(tie), v))
    return dist, owner
