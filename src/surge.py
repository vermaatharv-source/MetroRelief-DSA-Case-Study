"""Task 4 - monotonic deque (window max) and rolling sum."""
from collections import deque


def _check(a, k):
    if k <= 0:
        raise ValueError("K must be positive")


def sliding_window_max(a, k):
    """Max of every full window of k minutes. O(n) time, O(k) space.
    Deque holds indices whose values are strictly decreasing; front = window max.
    If k > len(a) there is no complete window -> []."""
    _check(a, k)
    dq, out = deque(), []
    for i, v in enumerate(a):
        while dq and a[dq[-1]] <= v:      # smaller/equal elements can never be a max again
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:                # front slid out of the window
            dq.popleft()
        if i >= k - 1:
            out.append(a[dq[0]])
    return out


def busiest_window_sum(a, k):
    """Largest sum over any k consecutive minutes. O(n) time, O(1) space.
    Returns None if k > len(a)."""
    _check(a, k)
    if k > len(a):
        return None
    s = sum(a[:k]); best = s
    for i in range(k, len(a)):
        s += a[i] - a[i - k]
        best = max(best, s)
    return best
