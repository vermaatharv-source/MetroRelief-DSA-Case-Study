"""Task 6 (bonus) - street-name autocomplete (trie) and hospital beds (segment tree)."""


class PrefixSuggester:
    """Trie; every node caches the 5 lexicographically smallest words below it.
    insert O(L * 5), suggest O(L) where L = word / prefix length."""
    LIMIT = 5

    class _Node:
        __slots__ = ("kids", "top")
        def __init__(self):
            self.kids, self.top = {}, []

    def __init__(self, streets=()):
        self.root = self._Node()
        self._seen = set()
        for s in streets:
            self.insert(s)

    def insert(self, street):
        w = street.strip().lower()
        if not w or w in self._seen:
            return
        self._seen.add(w)
        node = self.root
        self._offer(node, w)
        for ch in w:
            node = node.kids.setdefault(ch, self._Node())
            self._offer(node, w)

    def _offer(self, node, w):
        node.top.append(w)
        node.top.sort()
        del node.top[self.LIMIT:]

    def suggest(self, prefix):
        node = self.root
        for ch in prefix.strip().lower():
            node = node.kids.get(ch)
            if node is None:
                return []
        return list(node.top)


class HospitalBeds:
    """Iterative segment tree over (free_beds, -index): range max, point update.
    update O(log n), query O(log n). Ring road: query(l, r) with l > r wraps."""

    def __init__(self, beds):
        self.n = len(beds)
        if self.n == 0:
            raise ValueError("need at least one hospital")
        if any(b < 0 for b in beds):
            raise ValueError("beds cannot be negative")
        self.beds = list(beds)
        self.t = [None] * (2 * self.n)
        for i, b in enumerate(beds):
            self.t[self.n + i] = (b, -i)
        for i in range(self.n - 1, 0, -1):
            self.t[i] = max(self.t[2 * i], self.t[2 * i + 1])

    def update_beds(self, i, delta):
        self._chk(i)
        if self.beds[i] + delta < 0:
            raise ValueError("free beds would go negative")
        self.beds[i] += delta
        p = i + self.n
        self.t[p] = (self.beds[i], -i)
        p >>= 1
        while p >= 1:
            self.t[p] = max(self.t[2 * p], self.t[2 * p + 1])
            p >>= 1

    def query(self, l, r):
        """Returns (hospital_index, free_beds); ties -> smallest index in the
        order walked. If l > r the range wraps round the ring: [l..n-1] + [0..r]."""
        self._chk(l); self._chk(r)
        if l <= r:
            b, negi = self._range(l, r)
            return -negi, b
        a = self._range(l, self.n - 1)
        c = self._range(0, r)
        b, negi = max(a, c)
        return -negi, b

    def _range(self, l, r):
        res = (-1, 0)
        lo, hi = l + self.n, r + self.n + 1
        while lo < hi:
            if lo & 1:
                res = max(res, self.t[lo]); lo += 1
            if hi & 1:
                hi -= 1; res = max(res, self.t[hi])
            lo >>= 1; hi >>= 1
        return res

    def _chk(self, i):
        if not 0 <= i < self.n:
            raise IndexError("hospital index out of range")
