from .lww import LWWSet


class CRDTGraph:
    def __init__(self, bidirection=True):
        self.vertices = LWWSet()
        self.edges = LWWSet()
        self.cluster_table = []
        self.bidirection = bidirection

    def convert_edge(self, u, v):
        if self.bidirection is True:
            if u > v:
                u, v = v, u
                return u, v

        return u, v

    def list_nodes(self):
        nodes = list()
        for node in list(self.vertices.added_set):
            if self.contains_vertex(node):
                nodes.append(node)

        return nodes

    def get_neighbors(self, u):
        neighbors = list()
        if self.contains_vertex(u) is False:
            return neighbors

        for node in list(self.vertices.added_set):
            if self.contains_vertex(node):
                u, node = self.convert_edge(u, node)
                if self.contains_edge(u, node):
                    neighbors.append(node)

        return neighbors

    def add_vertex(self, u):
        self.vertices.add(u)

    def add_edge(self, u, v):
        # check if u and v exists
        if self.contains_vertex(u) is False or self.contains_vertex(v) is False:
            return False

        u, v = self.convert_edge(u, v)
        self.edges.add((u, v))
        return True

    def remove_vertex(self, u):
        if self.contains_vertex(u) is False:
            return False

        self.vertices.remove(u)

        # remove all connected edges of u
        for node in list(self.vertices.added_set):
            if self.contains_vertex(node):
                u, node = self.convert_edge(u, node)
                if self.contains_edge(u, node):
                    self.remove_edge(u, node)

        return True

    def remove_edge(self, u, v):
        u, v = self.convert_edge(u, v)
        self.edges.remove((u, v))

    def contains_vertex(self, u):
        added_timestamp, removed_timestamp = None, None
        if u in self.vertices.added_set:
            added_timestamp = self.vertices.added_timestamp[u]

        if u in self.vertices.removed_set:
            removed_timestamp = self.vertices.removed_timestamp[u]

        if added_timestamp is None:
            return False

        if removed_timestamp is None:
            return True

        if added_timestamp >= removed_timestamp:
            self.vertices.free_removed(u)
            return True
        else:
            self.vertices.free_added(u)
            return False

    def contains_edge(self, u, v):
        u, v = self.convert_edge(u, v)
        added_timestamp, removed_timestamp = None, None

        if (u, v) in self.edges.added_set:
            added_timestamp = self.edges.added_timestamp[(u, v)]

        if (u, v) in self.edges.removed_set:
            removed_timestamp = self.edges.removed_timestamp[(u, v)]

        if added_timestamp is None:
            return False

        if removed_timestamp is None:
            return True

        if added_timestamp >= removed_timestamp:
            self.edges.free_removed((u, v))
            return True
        else:
            self.edges.free_added((u, v))
            return False

    def find_path(self, u, v):
        pass

    def merge(self):
        pass
