"""Runs every sample from the case study and prints input -> output -> expected, with a pass mark."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from pq import IncidentQueue
from routing import Graph, fastest_route_to_hospital, nearest_ambulance
from reachability import reachability_over_closures
from surge import sliding_window_max, busiest_window_sum
from supply import allocate
from bonus import PrefixSuggester, HospitalBeds

def check(label, got, expected):
    mark = "PASS" if got == expected else "FAIL"
    print(f"  {label:<34} got: {got!s:<28} expected: {expected!s:<22} [{mark}]")
    assert got == expected

def head(t): print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")

ROADS = [("A","B",4),("A","C",2),("B","C",1),("B","D",5),("C","D",8),
         ("C","E",10),("D","E",2),("D","H",6),("E","H",3)]
def graph():
    g = Graph()
    for u, v, w in ROADS: g.add_edge(u, v, w)
    return g

head("TASK 1 - Incident Priority Queue   (add / serveNext / updateSeverity)")
q = IncidentQueue()
for i, s, t in [("I1",3,1),("I2",5,2),("I3",5,0),("I4",2,3)]: q.add(i, s, t)
print("  Added: I1(sev3,t1) I2(sev5,t2) I3(sev5,t0) I4(sev2,t3)")
check("service order", [q.serve_next().id for _ in range(4)], ["I3","I2","I1","I4"])
q = IncidentQueue()
for i, s, t in [("I1",3,1),("I2",5,2),("I3",5,0),("I4",2,3)]: q.add(i, s, t)
q.update_severity("I4", 5)
check("after updateSeverity(I4 -> 5)", [q.serve_next().id for _ in range(4)], ["I3","I2","I4","I1"])

head("TASK 2 - Fastest Route and Nearest Ambulance   (Dijkstra, early exit)")
t, path = fastest_route_to_hospital(graph(), "A", {"H"})
check("Query 1: A -> H (minutes)", t, 13)
print("  route:", " -> ".join(path))
g = graph(); g.remove_edge("D", "E")
t, path = fastest_route_to_hospital(g, "A", {"H"})
check("Query 2: D-E closed, A -> H", t, 14)
print("  route:", " -> ".join(path))
t, path = nearest_ambulance(graph(), "H", {"A", "E", "B"})
check("Nearest ambulance to H (A,E,B)", (t, path[0]), (3, "E"))
print("  ONE search from the incident, not one per ambulance")

head("TASK 3 - Road Closures and Reachability   (reverse-time Union-Find)")
cl = [("D","E"),("E","H"),("D","H"),("C","E")]
ans = reachability_over_closures(list("ABCDEH"), ROADS, ["H"], cl, "A")
print("  closures in order:", cl)
check("can A reach a hospital, per step", ["Yes" if a else "No" for a in ans], ["Yes","Yes","No","No"])

head("TASK 4 - Surge Monitoring   (monotonic deque + rolling sum)")
a = [2,1,4,3,0,5,2]
print("  calls per minute:", a, " K = 3")
check("part 1: max of every window", sliding_window_max(a, 3), [4,4,4,5,5])
check("part 2: busiest 3-minute total", busiest_window_sum(a, 3), 8)
check("edge: K larger than array", sliding_window_max([1,2], 5), [])

head("TASK 5 - Supply Allocation   (1-D knapsack + Hirschberg)")
cost, lives = [2,3,4,1], [30,50,60,10]
best, zones = allocate(cost, lives, 5)
print("  W = 5, zones (cost, lives):", list(zip(cost, lives)))
check("maximum lives", best, 80)
check("zones chosen (1-based)", [z + 1 for z in zones], [1, 2])

head("TASK 6 (Bonus) - Street Search and Hospital Beds")
s = PrefixSuggester(["Main St","Maple Ave","Market Rd","Mall Rd","Mango Ln","Marine Dr","Oak St"])
check('suggest("ma") -> up to 5', s.suggest("ma"), ["main st","mall rd","mango ln","maple ave","marine dr"])
h = HospitalBeds([5,2,9,9,1])
check("query(0,4) -> (hospital, beds)", h.query(0, 4), (2, 9))
h.update_beds(3, +3)
check("after updateBeds(3,+3)", h.query(0, 4), (3, 12))
check("ring wrap query(4,1) on [8,1,1,1,6]", HospitalBeds([8,1,1,1,6]).query(4, 1), (0, 8))

print("\nAll case-study samples reproduced correctly.")
