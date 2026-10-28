import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
import random, unittest
from pq import IncidentQueue
from routing import (Graph, INF, fastest_route_to_hospital, nearest_ambulance,
                     multi_source_dijkstra)
from reachability import reachability_over_closures, naive_reachability
from surge import sliding_window_max, busiest_window_sum
from supply import allocate, max_lives, reference_table
from bonus import PrefixSuggester, HospitalBeds

ROADS = [("A","B",4),("A","C",2),("B","C",1),("B","D",5),("C","D",8),
         ("C","E",10),("D","E",2),("D","H",6),("E","H",3)]

def sample_graph():
    g = Graph()
    for u, v, w in ROADS:
        g.add_edge(u, v, w)
    return g


class Task1(unittest.TestCase):
    def test_sample_order(self):
        q = IncidentQueue()
        for i, s, t in [("I1",3,1),("I2",5,2),("I3",5,0),("I4",2,3)]:
            q.add(i, s, t)
        self.assertEqual([q.serve_next().id for _ in range(4)], ["I3","I2","I1","I4"])
    def test_empty(self):
        self.assertIsNone(IncidentQueue().serve_next())
    def test_upgrade(self):
        q = IncidentQueue()
        q.add("a",1,0); q.add("b",3,1); q.add("c",2,2)
        q.update_severity("a", 5)
        self.assertEqual(q.serve_next().id, "a")
    def test_downgrade_and_tie_keeps_arrival(self):
        q = IncidentQueue()
        q.add("a",5,0); q.add("b",4,1); q.add("c",3,2)
        q.update_severity("a", 3)          # ties with c, but arrived earlier
        self.assertEqual([q.serve_next().id for _ in range(3)], ["b","a","c"])
    def test_errors(self):
        q = IncidentQueue(); q.add("a",1,0)
        with self.assertRaises(ValueError): q.add("a",2,1)
        with self.assertRaises(ValueError): q.add("b",9,1)
        with self.assertRaises(KeyError): q.update_severity("zzz", 3)
        q.serve_next()
        with self.assertRaises(KeyError): q.update_severity("a", 3)   # already served
    def test_random_vs_sorted(self):
        rnd = random.Random(1); q = IncidentQueue(); ref = {}
        for i in range(500):
            ref[i] = (rnd.randint(1,5), rnd.randint(0,50)); q.add(i, *ref[i])
        for i in rnd.sample(range(500), 100):
            s = rnd.randint(1,5); ref[i] = (s, ref[i][1]); q.update_severity(i, s)
        got = [q.serve_next() for _ in range(500)]
        keys = [(-x.severity, x.arrival) for x in got]
        self.assertEqual(keys, sorted(keys))


class Task2(unittest.TestCase):
    def test_query1(self):
        t, p = fastest_route_to_hospital(sample_graph(), "A", {"H"})
        self.assertEqual(t, 13); self.assertEqual(p, ["A","C","B","D","E","H"])
    def test_query2_closure(self):
        g = sample_graph(); g.remove_edge("D","E")
        self.assertEqual(fastest_route_to_hospital(g, "A", {"H"})[0], 14)
    def test_disconnected(self):
        g = sample_graph(); g.add_edge("X","Y",1)
        self.assertEqual(fastest_route_to_hospital(g, "X", {"H"}), (INF, []))
    def test_incident_at_hospital(self):
        self.assertEqual(fastest_route_to_hospital(sample_graph(), "H", {"H"}), (0, ["H"]))
    def test_nearest_of_several_hospitals(self):
        self.assertEqual(fastest_route_to_hospital(sample_graph(), "A", {"H","B"})[0], 3)
    def test_nearest_ambulance_single_search(self):
        t, p = nearest_ambulance(sample_graph(), "H", {"A","E","B"})
        self.assertEqual((t, p[0], p[-1]), (3, "E", "H"))
    def test_no_ambulance(self):
        self.assertEqual(nearest_ambulance(sample_graph(), "A", set())[0], INF)
    def test_multisource_matches_individual(self):
        g = sample_graph(); src = {"A","H"}
        dist, owner = multi_source_dijkstra(g, src)
        for v in g.adj:
            self.assertEqual(dist[v], min(fastest_route_to_hospital(g, v, {s})[0] for s in src))
    def test_directed_ambulance_direction(self):
        g = Graph(directed=True); g.add_edge("amb","inc",5); g.add_edge("inc","far",1)
        self.assertEqual(nearest_ambulance(g, "inc", {"amb"})[0], 5)
        self.assertEqual(nearest_ambulance(g, "inc", {"far"})[0], INF)
    def test_negative_weight_rejected(self):
        with self.assertRaises(ValueError): Graph().add_edge(1,2,-1)


class Task3(unittest.TestCase):
    nodes = list("ABCDEH")
    def test_sample(self):
        cl = [("D","E"),("E","H"),("D","H"),("C","E")]
        self.assertEqual(reachability_over_closures(self.nodes, ROADS, ["H"], cl, "A"),
                         [True, True, False, False])
    def test_no_closures(self):
        self.assertEqual(reachability_over_closures(self.nodes, ROADS, ["H"], [], "A"), [])
    def test_x_is_hospital(self):
        self.assertEqual(reachability_over_closures(self.nodes, ROADS, ["A"], [("A","B"),("A","C")], "A"), [True, True])
    def test_no_hospitals(self):
        self.assertEqual(reachability_over_closures(self.nodes, ROADS, [], [("A","B")], "A"), [False])
    def test_duplicate_and_unknown_closures(self):
        cl = [("D","H"),("H","D"),("A","H"),("E","H")]
        self.assertEqual(reachability_over_closures(self.nodes, ROADS, ["H"], cl, "A"),
                         [True, True, True, False])
    def test_initially_disconnected(self):
        nodes = self.nodes + ["Z"]
        self.assertEqual(reachability_over_closures(nodes, ROADS, ["H"], [("A","B")], "Z"), [False])
    def test_random_vs_naive(self):
        rnd = random.Random(7)
        for _ in range(60):
            n = rnd.randint(2, 15); nodes = list(range(n))
            edges = list({tuple(sorted(rnd.sample(nodes, 2))) for _ in range(rnd.randint(0, 25))})
            hosp = rnd.sample(nodes, rnd.randint(0, min(3, n)))
            cl = [rnd.choice(edges) if edges and rnd.random() < .8 else tuple(rnd.sample(nodes,2))
                  for _ in range(rnd.randint(0, 20))]
            x = rnd.choice(nodes)
            self.assertEqual(reachability_over_closures(nodes, edges, hosp, cl, x),
                             naive_reachability(nodes, edges, hosp, cl, x))


class Task4(unittest.TestCase):
    def test_sample(self):
        a = [2,1,4,3,0,5,2]
        self.assertEqual(sliding_window_max(a, 3), [4,4,4,5,5])
        self.assertEqual(busiest_window_sum(a, 3), 8)
    def test_k_larger_than_array(self):
        self.assertEqual(sliding_window_max([1,2], 5), []); self.assertIsNone(busiest_window_sum([1,2], 5))
    def test_empty(self):
        self.assertEqual(sliding_window_max([], 3), []); self.assertIsNone(busiest_window_sum([], 3))
    def test_k_one_and_k_n(self):
        a = [3,1,2]
        self.assertEqual(sliding_window_max(a, 1), a); self.assertEqual(sliding_window_max(a, 3), [3])
        self.assertEqual(busiest_window_sum(a, 3), 6)
    def test_equal_values_and_negatives(self):
        self.assertEqual(sliding_window_max([5,5,5,5], 2), [5,5,5])
        self.assertEqual(sliding_window_max([-3,-1,-2], 2), [-1,-1])
    def test_invalid_k(self):
        with self.assertRaises(ValueError): sliding_window_max([1], 0)
    def test_random_vs_bruteforce(self):
        rnd = random.Random(3)
        for _ in range(100):
            a = [rnd.randint(-5, 20) for _ in range(rnd.randint(0, 30))]; k = rnd.randint(1, 8)
            exp = [max(a[i:i+k]) for i in range(len(a)-k+1)]
            self.assertEqual(sliding_window_max(a, k), exp)
            if len(a) >= k:
                self.assertEqual(busiest_window_sum(a, k), max(sum(a[i:i+k]) for i in range(len(a)-k+1)))


class Task5(unittest.TestCase):
    def test_sample(self):
        best, zones = allocate([2,3,4,1], [30,50,60,10], 5)
        self.assertEqual(best, 80); self.assertEqual(zones, [0, 1])
    def test_zero_capacity_and_empty(self):
        self.assertEqual(allocate([1,2],[5,6], 0), (0, [])); self.assertEqual(allocate([], [], 10), (0, []))
    def test_nothing_fits(self):
        self.assertEqual(allocate([9,8],[5,6], 3), (0, []))
    def test_everything_fits_and_free_zone(self):
        self.assertEqual(allocate([0,1,2],[4,5,6], 10), (15, [0,1,2]))
    def test_chosen_is_feasible_and_optimal(self):
        rnd = random.Random(5)
        for _ in range(200):
            n = rnd.randint(0, 9); c = [rnd.randint(0, 8) for _ in range(n)]
            v = [rnd.randint(0, 20) for _ in range(n)]; W = rnd.randint(0, 25)
            best, zones = allocate(c, v, W)
            self.assertEqual(best, reference_table(c, v, W)); self.assertEqual(best, max_lives(c, v, W))
            self.assertLessEqual(sum(c[i] for i in zones), W)
            self.assertEqual(sum(v[i] for i in zones), best); self.assertEqual(len(zones), len(set(zones)))
    def test_invalid(self):
        with self.assertRaises(ValueError): allocate([1],[1,2], 3)


class Task6(unittest.TestCase):
    streets = ["Main St","Maple Ave","Market Rd","Mall Rd","Mango Ln","Marine Dr","Oak St"]
    def test_prefix_top5_sorted(self):
        self.assertEqual(PrefixSuggester(self.streets).suggest("ma"),
                         ["main st","mall rd","mango ln","maple ave","marine dr"])
    def test_fewer_than_five_and_case(self):
        self.assertEqual(PrefixSuggester(self.streets).suggest("OA"), ["oak st"])
    def test_no_match_and_empty_prefix(self):
        s = PrefixSuggester(self.streets); self.assertEqual(s.suggest("zz"), [])
        self.assertEqual(len(s.suggest("")), 5)
    def test_duplicates_ignored(self):
        s = PrefixSuggester(["a","a","a"]); self.assertEqual(s.suggest("a"), ["a"])
    def test_beds_query_and_update(self):
        h = HospitalBeds([5, 2, 9, 9, 1])
        self.assertEqual(h.query(0, 4), (2, 9)); self.assertEqual(h.query(0, 1), (0, 5))
        h.update_beds(3, +3); self.assertEqual(h.query(0, 4), (3, 12))
        h.update_beds(3, -12); self.assertEqual(h.query(0, 4), (2, 9))
    def test_ring_wrap(self):
        self.assertEqual(HospitalBeds([8, 1, 1, 1, 6]).query(4, 1), (0, 8))
    def test_single_and_errors(self):
        h = HospitalBeds([3]); self.assertEqual(h.query(0, 0), (0, 3))
        with self.assertRaises(ValueError): h.update_beds(0, -4)
        with self.assertRaises(IndexError): h.query(0, 1)
    def test_random_vs_bruteforce(self):
        rnd = random.Random(9); n = 13; b = [rnd.randint(0, 9) for _ in range(n)]; h = HospitalBeds(b)
        for _ in range(300):
            if rnd.random() < .4:
                i = rnd.randrange(n); d = rnd.randint(-b[i], 5); b[i] += d; h.update_beds(i, d)
            l, r = rnd.randrange(n), rnd.randrange(n)
            rng = list(range(l, r+1)) if l <= r else list(range(l, n)) + list(range(0, r+1))
            mx = max(b[i] for i in rng)
            idx, got = h.query(l, r)
            self.assertEqual(got, mx); self.assertIn(idx, rng); self.assertEqual(b[idx], mx)

if __name__ == "__main__":
    unittest.main(verbosity=1)
