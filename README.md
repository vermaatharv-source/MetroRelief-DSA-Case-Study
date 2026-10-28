# MetroRelief: City Emergency Dispatch Engine

![tests](https://github.com/<YOUR-USERNAME>/<YOUR-REPO>/actions/workflows/tests.yml/badge.svg)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![deps](https://img.shields.io/badge/dependencies-none-brightgreen)

Data Structures and Algorithms case study. A dispatch engine for the city of Rivergate
(50,000 junctions, 120,000 roads, 300 ambulances, 40 hospitals, about 2,000 calls/hour).
All algorithms are written from scratch. No shortest-path or connectivity library is used;
only built-in lists, dicts, `heapq` and `deque`.

**Author:** Atharv Verma, B.Tech CSE, SRM Institute of Science and Technology

## Run it (no installs)

```bash
python tests/test_metrorelief.py -v   # 44 unit tests
python run_samples.py                 # every sample from the case study, with PASS marks
python demo.py                        # 100 incidents through Tasks 1 -> 2 -> 3
```

## What is solved and how

| Task | Problem | Data structure / algorithm | Time | Extra space | File |
|---|---|---|---|---|---|
| 1 | Incident priority queue with severity upgrades | Indexed binary heap (heap + id to position map) | add, serveNext, update: O(log n) | O(n) | `src/pq.py` |
| 2 | Fastest route, nearest ambulance, best hospital | Dijkstra with early exit. Nearest ambulance = ONE search from the incident (super-source argument) | O((V+E) log V) | O(V+E) | `src/routing.py` |
| 3 | Reachability after road closures | Union-Find, closures processed in reverse (deletions become unions) | O((V+E+Q) a(V)) | O(V+E+Q) | `src/reachability.py` |
| 4 | Surge monitoring | Monotonic deque for window max, rolling sum for busiest total | O(n) | O(K) / O(1) | `src/surge.py` |
| 5 | Supply allocation | 0/1 knapsack, 1-D DP + Hirschberg divide and conquer to recover zones | O(nW) | O(W + log n) | `src/supply.py` |
| 6 | Street search, hospital beds (bonus) | Trie with top-5 cache, segment tree with ring wrap | O(L), O(log n) | O(n) | `src/bonus.py` |

### Key ideas in one line each
- **Task 1:** a hash map from incident id to heap index makes `updateSeverity` O(log n).
- **Task 2:** Dijkstra settles junctions in increasing distance, so the first ambulance popped is the nearest. This replaces 300 searches with one.
- **Task 3:** a union-find cannot delete edges, so run the known closure schedule backwards and re-add roads.
- **Task 4:** each index enters and leaves the deque at most once, so the total is O(n).
- **Task 5:** keep one DP array and recover the chosen zones by splitting the zones in halves, so memory is O(W) instead of O(nW).

## Output 1. Case-study samples (`python run_samples.py`)

Full file: [`outputs/1_samples_output.txt`](outputs/1_samples_output.txt)

```text
TASK 1  service order                 ['I3', 'I2', 'I1', 'I4']        [PASS]
TASK 2  Query 1: A -> H               13 minutes (A-C-B-D-E-H)         [PASS]
TASK 2  Query 2: D-E closed           14 minutes (A-C-B-D-H)           [PASS]
TASK 3  reachability per step         ['Yes', 'Yes', 'No', 'No']       [PASS]
TASK 4  window maximum                [4, 4, 4, 5, 5], busiest = 8     [PASS]
TASK 5  max lives, zones (1-based)    80, zones [1, 2]                 [PASS]
TASK 6  ring wrap query(4,1)          hospital 0 with 8 beds           [PASS]
```

## Output 2. Unit tests (`python tests/test_metrorelief.py -v`)

Full verbose file: [`outputs/2_tests_output.txt`](outputs/2_tests_output.txt)

```text
Ran 44 tests in 0.027s

OK
```

| Task | Tests | Edge cases covered |
|---|---|---|
| 1 | 6 | empty queue, tie on severity, downgrade, duplicate id, unknown id, 500-incident random check |
| 2 | 10 | disconnected graph, incident at hospital, no ambulance, directed roads, negative weight, multi-source |
| 3 | 7 | no closures, X is a hospital, no hospitals, duplicate and unknown closures, 60 random graphs vs naive BFS |
| 4 | 7 | K larger than array, empty input, K = 1, K = n, equal values, negatives, random vs brute force |
| 5 | 6 | W = 0, nothing fits, zero-cost zone, empty input, 200 random instances vs textbook table |
| 6 | 8 | no match, ring wrap, ties, single hospital, out-of-range, 300 random operations vs brute force |

## Output 3. Integration demo (`python demo.py`)

100 incidents flow through Task 1 (priority queue), Task 2 (ambulance and hospital search) and
Task 3 (flood closures). The run is seeded, so it is reproducible.
Full file: [`outputs/3_demo_output.txt`](outputs/3_demo_output.txt)

```text
First 5 dispatches (incident sev@junction | ambulance, pickup min | hospital junction, trip min)
  I0   sev5@9   | amb7  5 min | hospital@7    4 min
  I1   sev5@67  | amb4  0 min | hospital@56   5 min
  I4   sev5@62  | amb3 10 min | hospital@107 15 min
  I8   sev5@59  | amb0  7 min | hospital@46  10 min
  I12  sev5@117 | amb9 13 min | hospital@107 14 min
Service order is non-increasing in severity: True
Dispatched 100 incidents, mean total time 24.2 min
After 230 flood closures, 96/100 incident junctions cannot reach any hospital
Task 3 answer cross-checked against naive BFS rerun: OK
```

## Measured speed-up (Task 3)

On 20,000 junctions, about 40,000 roads and 300 closures: reverse Union-Find **0.055 s** vs rerunning
BFS after every closure **4.1 s** (about 75x faster, identical answers).

## Repository layout

```text
src/            pq.py  routing.py  reachability.py  surge.py  supply.py  bonus.py
tests/          test_metrorelief.py        (44 tests, at least 5 per task)
outputs/        1_samples_output.txt  2_tests_output.txt  3_demo_output.txt
run_samples.py  demo.py
.github/workflows/tests.yml                (runs everything on every push)
```

## Reflection: what changes at 100x scale

The one decision I would change is running a fresh Dijkstra over the raw road graph for every query.
At about 5 million junctions that can cost around 10^8 steps per search. I would store the graph in
CSR arrays, add Contraction Hierarchies or ALT landmarks (with closures re-weighting only the affected part),
and partition the city into regions with their own fleet index. The other tasks already scale well.
