import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
"""Integration demo: 100 incidents through Task 1 -> Task 2 -> Task 3 (seeded, reproducible)."""
import random
from collections import deque
from pq import IncidentQueue
from routing import Graph, INF, fastest_route_to_hospital, nearest_ambulance
from reachability import reachability_over_closures, naive_reachability
from bonus import HospitalBeds

R = random.Random(2026)
SIDE = 12                                          # 12x12 grid = 144 junctions
nodes = [r * SIDE + c for r in range(SIDE) for c in range(SIDE)]
roads = []
for r in range(SIDE):
    for c in range(SIDE):
        u = r * SIDE + c
        if c + 1 < SIDE: roads.append((u, u + 1, R.randint(1, 9)))
        if r + 1 < SIDE: roads.append((u, u + SIDE, R.randint(1, 9)))
for _ in range(25):                                # a few diagonal shortcuts
    u, v = R.sample(nodes, 2); roads.append((u, v, R.randint(5, 15)))
G = Graph()
for u, v, w in roads:
    G.add_edge(u, v, w)

hospital_nodes = R.sample(nodes, 6)
beds = HospitalBeds([R.randint(3, 6) for _ in hospital_nodes])
ambulance_at = {a: R.choice(nodes) for a in range(10)}
busy = deque()                                     # (release_step, id, new_junction)

# ---- Task 1: incidents arrive, some get upgraded ---------------------------
Q = IncidentQueue()
where = {}
for i in range(100):
    where[i] = R.choice(nodes)
    Q.add(i, R.randint(1, 5), arrival=i)
for i in R.sample(range(100), 15):
    Q.update_severity(i, 5)

# ---- Task 2 per incident, in service order ---------------------------------
served, total_response = [], 0
step = 0
while len(Q):
    def release():
        _, a, loc, h = busy.popleft()
        ambulance_at[a] = loc
        beds.update_beds(h, +1)                    # patient handed over, bed turns over
    while busy and busy[0][0] <= step:
        release()
    if not ambulance_at:                           # everyone busy: wait for the earliest
        release()
    inc = Q.serve_next()
    j = where[inc.id]
    junction_to_amb = {}
    for a, loc in ambulance_at.items():
        junction_to_amb.setdefault(loc, a)
    t_amb, p = nearest_ambulance(G, j, junction_to_amb.keys())      # ONE search
    amb = junction_to_amb[p[0]]
    open_h = [h for h, n in enumerate(hospital_nodes) if beds.beds[h] > 0]
    node_to_h = {hospital_nodes[h]: h for h in open_h}
    t_hosp, path = fastest_route_to_hospital(G, j, node_to_h.keys())
    dest = path[-1]
    del ambulance_at[amb]
    busy.append((step + 3, amb, dest, node_to_h[dest]))
    beds.update_beds(node_to_h[dest], -1)
    served.append((inc, j, amb, t_amb, dest, t_hosp))
    total_response += t_amb + t_hosp
    step += 1

print("First 5 dispatches (incident sev@junction | ambulance, pickup min | hospital junction, trip min)")
for inc, j, amb, ta, dest, th in served[:5]:
    print(f"  I{inc.id:<3} sev{inc.severity}@{j:<3} | amb{amb} {ta:>2} min | hospital@{dest:<3} {th:>2} min")
sev = [s[0].severity for s in served]
print("Service order is non-increasing in severity:", all(sev[i] >= sev[i+1] for i in range(99)))
print(f"Dispatched {len(served)} incidents, mean total time {total_response/len(served):.1f} min")

# ---- Task 3: flood schedule of 60 closures, check every incident junction --
flood = R.sample(roads, 230)
closures = [(u, v) for u, v, _ in flood]
cut_off, first_loss = 0, []
for inc, j, *_ in served:
    ans = reachability_over_closures(nodes, roads, hospital_nodes, closures, j)
    if not ans[-1]:
        cut_off += 1
    first_loss.append(ans.index(False) if False in ans else None)
check = served[0][1]
assert reachability_over_closures(nodes, roads, hospital_nodes, closures, check) == \
       naive_reachability(nodes, roads, hospital_nodes, closures, check)
print(f"After {len(closures)} flood closures, {cut_off}/100 incident junctions cannot reach any hospital")
print("Task 3 answer cross-checked against naive BFS rerun: OK")
