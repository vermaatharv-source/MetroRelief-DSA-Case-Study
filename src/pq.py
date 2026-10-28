"""Task 1 - Incident priority queue: indexed binary min-heap.

Key = (-severity, arrival_time, seq). Smallest key is served first, so:
  * higher severity first, then earlier arrival, then insertion order (deterministic).
A dict `pos` maps incident id -> current heap index, which is what makes
updateSeverity O(log n): find in O(1), change key, sift up or down.
"""
from collections import namedtuple

Incident = namedtuple("Incident", "id severity arrival")


class IncidentQueue:
    def __init__(self):
        self._heap = []      # entries: [(-sev, arrival, seq), id]
        self._pos = {}       # id -> index in heap
        self._info = {}      # id -> Incident
        self._seq = 0

    def __len__(self):
        return len(self._heap)

    def __contains__(self, inc_id):
        return inc_id in self._pos

    # ---- public API -------------------------------------------------
    def add(self, inc_id, severity, arrival):
        """O(log n)."""
        self._check_severity(severity)
        if inc_id in self._pos:
            raise ValueError(f"duplicate incident id {inc_id!r}")
        self._seq += 1
        self._heap.append([(-severity, arrival, self._seq), inc_id])
        i = len(self._heap) - 1
        self._pos[inc_id] = i
        self._info[inc_id] = Incident(inc_id, severity, arrival)
        self._sift_up(i)

    def serve_next(self):
        """O(log n). Returns the Incident served, or None if empty."""
        if not self._heap:
            return None
        top = self._heap[0]
        last = self._heap.pop()
        del self._pos[top[1]]
        if self._heap:
            self._heap[0] = last
            self._pos[last[1]] = 0
            self._sift_down(0)
        return self._info.pop(top[1])

    def update_severity(self, inc_id, new_severity):
        """O(log n). Works for upgrades and downgrades."""
        self._check_severity(new_severity)
        if inc_id not in self._pos:
            raise KeyError(f"incident {inc_id!r} not waiting")
        i = self._pos[inc_id]
        _, arrival, seq = self._heap[i][0]
        self._heap[i][0] = (-new_severity, arrival, seq)
        old = self._info[inc_id]
        self._info[inc_id] = Incident(inc_id, new_severity, old.arrival)
        self._sift_up(i)
        self._sift_down(self._pos[inc_id])

    def peek(self):
        return self._info[self._heap[0][1]] if self._heap else None

    # ---- internals --------------------------------------------------
    @staticmethod
    def _check_severity(s):
        if not (isinstance(s, int) and 1 <= s <= 5):
            raise ValueError("severity must be an integer 1..5")

    def _swap(self, i, j):
        h = self._heap
        h[i], h[j] = h[j], h[i]
        self._pos[h[i][1]] = i
        self._pos[h[j][1]] = j

    def _sift_up(self, i):
        h = self._heap
        while i > 0:
            p = (i - 1) // 2
            if h[i][0] < h[p][0]:
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i):
        h, n = self._heap, len(self._heap)
        while True:
            l, r, m = 2 * i + 1, 2 * i + 2, i
            if l < n and h[l][0] < h[m][0]:
                m = l
            if r < n and h[r][0] < h[m][0]:
                m = r
            if m == i:
                return
            self._swap(i, m)
            i = m
