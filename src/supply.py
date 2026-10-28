"""Task 5 - 0/1 knapsack with O(W) extra memory AND the chosen zones (Hirschberg)."""


def _row(costs, lives, lo, hi, cap):
    """Best lives for items[lo:hi] at every capacity 0..cap, in ONE 1-D array."""
    dp = [0] * (cap + 1)
    for i in range(lo, hi):
        c, v = costs[i], lives[i]
        for w in range(cap, c - 1, -1):          # downward = each zone used once
            if dp[w - c] + v > dp[w]:
                dp[w] = dp[w - c] + v
    return dp


def max_lives(costs, lives, W):
    """Value only: O(nW) time, O(W) space."""
    _validate(costs, lives, W)
    return _row(costs, lives, 0, len(costs), W)[W]


def allocate(costs, lives, W):
    """Returns (max_lives, sorted chosen zone indices).
    Time O(nW) (about 2x the plain DP), extra space O(W + log n) -
    versus O(nW) for the textbook table + backtracking."""
    _validate(costs, lives, W)
    chosen = []
    _solve(costs, lives, 0, len(costs), W, chosen)
    chosen.sort()
    return sum(lives[i] for i in chosen), chosen


def _solve(costs, lives, lo, hi, cap, out):
    if lo >= hi:
        return
    if hi - lo == 1:
        if costs[lo] <= cap and lives[lo] > 0:
            out.append(lo)
        return
    mid = (lo + hi) // 2
    left = _row(costs, lives, lo, mid, cap)
    right = _row(costs, lives, mid, hi, cap)
    best_c = max(range(cap + 1), key=lambda c: left[c] + right[cap - c])
    _solve(costs, lives, lo, mid, best_c, out)
    _solve(costs, lives, mid, hi, cap - best_c, out)


def reference_table(costs, lives, W):
    """Textbook O(nW)-memory DP, used only to cross-check in tests."""
    n = len(costs)
    t = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(W + 1):
            t[i][w] = t[i - 1][w]
            if costs[i - 1] <= w:
                t[i][w] = max(t[i][w], t[i - 1][w - costs[i - 1]] + lives[i - 1])
    return t[n][W]


def _validate(costs, lives, W):
    if len(costs) != len(lives):
        raise ValueError("costs and lives must have equal length")
    if W < 0 or any(c < 0 for c in costs) or any(v < 0 for v in lives):
        raise ValueError("negative values are not allowed")
