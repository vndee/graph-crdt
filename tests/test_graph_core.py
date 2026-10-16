"""In-process graph invariants; these tests do not require running peer servers."""
import copy
import itertools
import json
import unittest
from unittest.mock import patch
from graph_crdt.graph import CRDTGraph


def state(graph):
    return {name: json.loads(value) for name, value in graph.broadcast().items()}


def graph_with_edges(vertices, edges, bidirection=True):
    graph = CRDTGraph(bidirection=bidirection)
    with patch('graph_crdt.lww.time.time', return_value=10):
        for vertex in vertices:
            graph.add_vertex(vertex)
        for left, right in edges:
            graph.add_edge(left, right)
    return graph


class GraphCoreTests(unittest.TestCase):
    def test_neighbors_do_not_change_source_after_normalizing_edge(self):
        graph = graph_with_edges([1, 2, 3, 4], [(3, 1), (3, 2), (3, 4)])
        self.assertEqual(graph.get_neighbors(3), (True, [1, 2, 4]))

    def test_remove_vertex_tombstones_all_incident_edges(self):
        graph = graph_with_edges([1, 2, 3, 4], [(3, 1), (3, 2), (3, 4), (1, 2)])
        with patch('graph_crdt.lww.time.time', return_value=20):
            self.assertTrue(graph.remove_vertex(3))
        self.assertEqual(set(graph.edges.removed), {(1, 3), (2, 3), (3, 4)})
        self.assertTrue(graph.contains_edge(1, 2)[1])
        with patch('graph_crdt.lww.time.time', return_value=30):
            graph.add_vertex(3)
        self.assertEqual(graph.get_neighbors(3), (True, []))

    def test_directed_remove_covers_incoming_and_outgoing_edges(self):
        graph = graph_with_edges([1, 2, 3], [(1, 2), (2, 3), (3, 1)], False)
        with patch('graph_crdt.lww.time.time', return_value=20):
            graph.remove_vertex(2)
        self.assertEqual(set(graph.edges.removed), {(1, 2), (2, 3)})
        self.assertTrue(graph.contains_edge(3, 1)[1])
        self.assertFalse(graph.contains_edge(1, 3)[1])

    def test_edge_requires_live_endpoints_after_remote_merge(self):
        graph = graph_with_edges([1, 2], [(1, 2)])
        graph.merge('{}', '{"2": 20}', '{}', '{}')
        self.assertFalse(graph.contains_edge(1, 2)[1])
        self.assertEqual(graph.get_neighbors(1), (True, []))
        self.assertEqual(graph.find_path(1, 2), (False, []))

    def test_queries_leave_all_replicated_history_unchanged(self):
        graph = graph_with_edges([1, 2, 3], [(1, 3)])
        graph.vertices.removed = {1: 5, 2: 20}
        graph.edges.removed = {(1, 3): 5}
        before = state(graph)
        graph.contains_vertex(1)
        graph.contains_vertex(2)
        graph.contains_edge(1, 3)
        graph.list_nodes()
        graph.get_neighbors(1)
        graph.find_path(1, 3)
        self.assertEqual(state(graph), before)

    def test_equal_timestamp_add_wins_without_mutating_history(self):
        graph = graph_with_edges([1, 2], [(1, 2)])
        graph.vertices.removed[1] = 10
        graph.edges.removed[(1, 2)] = 10
        before = state(graph)
        self.assertTrue(graph.contains_vertex(1)[1])
        self.assertTrue(graph.contains_edge(1, 2)[1])
        self.assertEqual(state(graph), before)

    def test_bfs_keeps_shortest_parent_when_another_parent_is_queued(self):
        graph = graph_with_edges([1, 2, 3, 4], [(1, 2), (1, 3), (2, 3), (3, 4)])
        self.assertEqual(graph.find_path(1, 4), (True, [1, 3, 4]))

    def test_path_to_self_requires_a_visible_vertex(self):
        graph = graph_with_edges([1], [])
        self.assertEqual(graph.find_path(99, 99), (False, []))
        self.assertEqual(graph.find_path(1, 1), (True, [1]))
        with patch('graph_crdt.lww.time.time', return_value=20):
            graph.remove_vertex(1)
        self.assertEqual(graph.find_path(1, 1), (False, []))

    def test_merge_is_commutative_associative_and_idempotent_for_fixed_states(self):
        replicas = [CRDTGraph() for _ in range(3)]
        replicas[0].vertices.added = {1: 10, 2: 10}
        replicas[0].edges.added = {(1, 2): 10}
        replicas[1].vertices.added = {1: 12, 3: 12}
        replicas[1].vertices.removed = {2: 11}
        replicas[1].edges.added = {(1, 3): 12}
        replicas[2].vertices.added = {2: 15, 3: 12}
        replicas[2].edges.removed = {(1, 2): 14}
        expected = None
        for order in itertools.permutations(replicas):
            merged = CRDTGraph()
            for replica in order:
                merged.merge(**replica.broadcast())
                # Reads must not change the state that the next merge sees.
                merged.list_nodes()
                merged.get_neighbors(1)
            merged.merge(**order[0].broadcast())
            current = state(merged)
            if expected is None:
                expected = current
            self.assertEqual(current, expected)
            self.assertEqual(merged.get_neighbors(1), (True, [3]))
        left = copy.deepcopy(replicas[0])
        left.merge(**replicas[1].broadcast())
        left.merge(**replicas[2].broadcast())
        right = copy.deepcopy(replicas[1])
        right.merge(**replicas[2].broadcast())
        combined = copy.deepcopy(replicas[0])
        combined.merge(**right.broadcast())
        self.assertEqual(state(left), state(combined))

    def test_replayed_old_snapshot_does_not_resurrect_removed_edge(self):
        graph = graph_with_edges([1, 2], [(1, 2)])
        old = graph.broadcast()
        with patch('graph_crdt.lww.time.time', return_value=20):
            graph.remove_edge(1, 2)
        graph.contains_edge(1, 2)
        graph.merge(**old)
        self.assertFalse(graph.contains_edge(1, 2)[1])


if __name__ == '__main__':
    unittest.main()
