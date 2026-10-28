"""Task 3 - offline reverse processing with Union-Find (DSU).

Deleting edges is hard for DSU, ADDING edges is easy. So run the closure
schedule BACKWARDS: start from the graph after all closures, then re-open
roads in reverse order, answering as we go.  O((V + E + Q) * alpha(V)).
"""


class DSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.size = [1] * n
        self.hosp = [0] * n          # hospitals in this component (valid at roots)

    def find(self, x):               # iterative path compression
        root = x
        while self.p[root] != root:
            root = self.p[root]
        while self.p[x] != root:
            self.p[x], x = root, self.p[x]
        return root

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.p[b] = a
        self.size[a] += self.size[b]
        self.hosp[a] += self.hosp[b]


def reachability_over_closures(nodes, edges, hospitals, closures, x):
    """Returns list of Q booleans: can x reach a hospital after closure t?
    Closing a non-existent road, or the same road twice, is a harmless no-op.
    """
    idx = {u: i for i, u in enumerate(nodes)}
    if x not in idx:
        raise KeyError(f"unknown junction {x!r}")
    norm = lambda u, v: (min(idx[u], idx[v]), max(idx[u], idx[v]))
    edge_set = {norm(e[0], e[1]) for e in edges}

    first_close = {}                              # edge -> first step it really closes
    closed_at = {}                                # step -> edge
    for t, (u, v) in enumerate(closures):
        e = norm(u, v)
        if e in edge_set and e not in first_close:
            first_close[e] = t
            closed_at[t] = e

    dsu = DSU(len(nodes))
    for h in set(hospitals):
        dsu.hosp[idx[h]] += 1
    for e in edge_set:                            # graph after ALL closures
        if e not in first_close:
            dsu.union(*e)

    q = len(closures)
    ans = [False] * q
    xi = idx[x]
    for t in range(q - 1, -1, -1):
        ans[t] = dsu.hosp[dsu.find(xi)] > 0
        if t in closed_at:                        # undo closure t
            dsu.union(*closed_at[t])
    return ans


def naive_reachability(nodes, edges, hospitals, closures, x):
    """Baseline O(Q (V+E)) used for cross-checking and benchmarking."""
    adj = {u: set() for u in nodes}
    for e in edges:
        adj[e[0]].add(e[1]); adj[e[1]].add(e[0])
    hosp, out = set(hospitals), []
    for u, v in closures:
        adj.get(u, set()).discard(v); adj.get(v, set()).discard(u)
        seen, stack = {x}, [x]
        while stack:
            a = stack.pop()
            for b in adj[a]:
                if b not in seen:
                    seen.add(b); stack.append(b)
        out.append(bool(seen & hosp))
    return out
