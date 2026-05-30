class CityNetwork:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, node_id, info=None):
        self.nodes[node_id] = info or {}
        if node_id not in self.edges:
            self.edges[node_id] = {}

    def add_edge(self, from_node, to_node, weight):
        self.add_node(from_node)
        self.add_node(to_node)
        self.edges[from_node][to_node] = weight
        self.edges[to_node][from_node] = weight

    def get_neighbors(self, node_id):
        return list(self.edges.get(node_id, {}).keys())

    def get_weight(self, from_node, to_node):
        return self.edges.get(from_node, {}).get(to_node, float('inf'))

    def dijkstra(self, start, end):
        import heapq
        if start not in self.nodes or end not in self.nodes:
            return None, float('inf')

        dist = {node: float('inf') for node in self.nodes}
        prev = {node: None for node in self.nodes}
        dist[start] = 0
        pq = [(0, start)]

        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            if u == end:
                break
            for v in self.get_neighbors(u):
                w = self.get_weight(u, v)
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], v))

        if dist[end] == float('inf'):
            return None, float('inf')

        path = []
        current = end
        while current is not None:
            path.append(current)
            current = prev[current]
        path.reverse()
        return path, dist[end]

    def update_edge(self, from_node, to_node, new_weight):
        if from_node in self.edges and to_node in self.edges[from_node]:
            self.edges[from_node][to_node] = new_weight
            self.edges[to_node][from_node] = new_weight

    def remove_edge(self, from_node, to_node):
        if from_node in self.edges and to_node in self.edges[from_node]:
            del self.edges[from_node][to_node]
        if to_node in self.edges and from_node in self.edges[to_node]:
            del self.edges[to_node][from_node]

    def remove_node(self, node_id):
        if node_id in self.edges:
            for neighbor in list(self.edges[node_id].keys()):
                if neighbor in self.edges:
                    del self.edges[neighbor][node_id]
            del self.edges[node_id]
        if node_id in self.nodes:
            del self.nodes[node_id]

    def __str__(self):
        lines = [f"Nodes: {list(self.nodes.keys())}"]
        for u in self.edges:
            for v, w in self.edges[u].items():
                if u < v:
                    lines.append(f"  {u} <-> {v}: weight={w}")
        return "\n".join(lines)