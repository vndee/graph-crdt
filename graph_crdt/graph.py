import json
from .lww import LWWSet
from .utils import get_logger

logger = get_logger("Graph")


class CRDTGraph:
    def __init__(self, bidirection=True):
        self.vertices = LWWSet()
        self.edges = LWWSet()
        self.cluster_table = []
        self.address_set = set()
        self.bidirection = bidirection

    def set_dir(self, dir):
        self.bidirection = dir

    def get_cluster_table(self):
        return self.cluster_table

    def register_cluster_table(self, address):
        if address not in self.address_set:
            self.cluster_table.append(address)
            self.address_set.add(address)
            return True

        return False

    def convert_edge(self, u, v):
        if self.bidirection is True:
            if u > v:
                u, v = v, u
                return u, v

        return u, v

    def list_nodes(self):
        nodes = list()
        for node in list(self.vertices.added.keys()):
            if self.contains_vertex(node)[1]:
                nodes.append(node)

        return nodes

    def get_neighbors(self, u):
        try:
            neighbors = list()
            if self.contains_vertex(u)[1] is False:
                return False, neighbors

            for node in list(self.vertices.added.keys()):
                if node == u:
                    continue

                if self.contains_vertex(node)[1]:
                    _u, _node = u, node
                    u, node = self.convert_edge(u, node)
                    if self.contains_edge(u, node)[1]:
                        neighbors.append(_node)

            return True, sorted(neighbors)
        except Exception as e:
            logger.exception(e)
            return False, []

    def add_vertex(self, u):
        if self.contains_vertex(u)[1]:
            return False, "Duplicated"

        return self.vertices.add(u), ""

    def add_edge(self, u, v):
        # check if u and v exists
        if self.contains_vertex(u)[1] is False or self.contains_vertex(v)[1] is False:
            return False, f"Not valid vertex ({u} - {v})"

        if self.contains_edge(u, v)[1]:
            return False, "Duplicated"

        u, v = self.convert_edge(u, v)
        self.edges.add((u, v))
        return True, ""

    def remove_vertex(self, u):
        if self.contains_vertex(u)[1] is False:
            return False

        self.vertices.remove(u)

        # remove all connected edges of u
        for node in list(self.vertices.added.keys()):
            if self.contains_vertex(node)[1]:
                u, node = self.convert_edge(u, node)
                if self.contains_edge(u, node)[1]:
                    self.remove_edge(u, node)

        return True

    def remove_edge(self, u, v):
        u, v = self.convert_edge(u, v)
        return self.edges.remove((u, v))

    def contains_vertex(self, u):
        added_timestamp, removed_timestamp = None, None
        if u in self.vertices.added:
            added_timestamp = self.vertices.added[u]

        if u in self.vertices.removed:
            removed_timestamp = self.vertices.removed[u]

        if added_timestamp is None:
            return True, False

        if removed_timestamp is None:
            return True, True

        if added_timestamp >= removed_timestamp:
            self.vertices.free_removed(u)
            return True, True
        else:
            self.vertices.free_added(u)
            return True, False

    def contains_edge(self, u, v):
        u, v = self.convert_edge(u, v)
        added_timestamp, removed_timestamp = None, None

        if (u, v) in self.edges.added:
            added_timestamp = self.edges.added[(u, v)]

        if (u, v) in self.edges.removed:
            removed_timestamp = self.edges.removed[(u, v)]

        if added_timestamp is None:
            return True, False

        if removed_timestamp is None:
            return True, True

        if added_timestamp >= removed_timestamp:
            self.edges.free_removed((u, v))
            return True, True
        else:
            self.edges.free_added((u, v))
            return True, False

    def find_path(self, source, target):
        # Breath-first search for the shortest path between u and v

        try:
            q = [source]
            head = 0
            visited, trace = set(), dict()
            trace[source] = source

            while q.__len__() - head > 0:
                u = q[head]
                head = head + 1
                visited.add(u)

                if u == target:
                    break

                logger.debug(self.get_neighbors(u)[1])
                for v in self.get_neighbors(u)[1]:
                    if v in visited:
                        continue

                    trace[v] = u
                    q.append(v)

            if target not in visited:
                return False, []

            path = list()
            while trace[target] != target:
                path.append(target)
                target = trace[target]
            path.append(source)
            return True, path[:: - 1]
        except Exception as e:
            logger.exception(e)
            return False, []

    def clear(self):
        try:
            for node in self.list_nodes():
                self.remove_vertex(node)
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def broadcast(self):
        return {
            "vertices_added": json.dumps(self.vertices.added),
            "vertices_removed": json.dumps(self.vertices.removed),
            "edges_added": json.dumps({f"{k[0]}_{k[1]}": v for k, v in self.edges.added.items()}),
            "edges_removed": json.dumps({f"{k[0]}_{k[1]}": v for k, v in self.edges.removed.items()})
        }

    def merge(self, vertices_added, vertices_removed, edges_added, edges_removed):
        vertices_added = json.loads(vertices_added)
        vertices_removed = json.loads(vertices_removed)
        edges_added = json.loads(edges_added)
        edges_removed = json.loads(edges_removed)

        for k, v in vertices_added.items():
            k = int(k)
            if k in self.vertices.added:
                if self.vertices.added[k] >= v:
                    continue
            self.vertices.added[k] = v

        for k, v in vertices_removed.items():
            k = int(k)
            if k in self.vertices.removed:
                if self.vertices.removed[k] >= v:
                    continue
            self.vertices.removed[k] = v

        for k, z in edges_added.items():
            u, v = int(k.split("_")[0]), int(k.split("_")[1])
            u, v = self.convert_edge(u, v)

            if (u, v) in self.edges.added:
                if self.edges.added[(u, v)] >= z:
                    continue

            self.edges.added[(u, v)] = z

        for k, z in edges_removed.items():
            u, v = int(k.split("_")[0]), int(k.split("_")[1])
            u, v = self.convert_edge(u, v)

            if (u, v) in self.edges.removed:
                if self.edges.removed[(u, v)] >= z:
                    continue

            self.edges.removed[(u, v)] = z


database_instance = CRDTGraph()
