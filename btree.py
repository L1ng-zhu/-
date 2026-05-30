import os
import json

class BTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.values = []
        self.children = []

    def serialize(self):
        return json.dumps({
            'leaf': self.leaf,
            'keys': self.keys,
            'values': self.values,
            'children': self.children
        })

    @staticmethod
    def deserialize(data):
        d = json.loads(data)
        node = BTreeNode(leaf=d['leaf'])
        node.keys = d['keys']
        node.values = d['values']
        node.children = d['children']
        return node

class BTree:
    ORDER = 32

    def __init__(self, index_file):
        self.index_file = index_file
        self.root_file = index_file + ".root"
        self.t = self.ORDER
        self._node_counter = 0
        self._load_or_create_root()

    def _get_next_node_id(self):
        nid = self._node_counter
        self._node_counter += 1
        return nid

    def _load_or_create_root(self):
        if os.path.exists(self.root_file):
            try:
                with open(self.root_file, 'r') as f:
                    data = json.load(f)
                    self.root = BTreeNode.deserialize(data['node_data'])
                    self._node_counter = data.get('node_counter', 0)
            except:
                self.root = BTreeNode(leaf=True)
                self._node_counter = 0
        else:
            self.root = BTreeNode(leaf=True)
            self._node_counter = 0

    def _save_root(self):
        with open(self.root_file, 'w') as f:
            json.dump({
                'node_data': json.loads(self.root.serialize()),
                'node_counter': self._node_counter
            }, f)

    def _child_file(self, node_id):
        return f"{self.index_file}.child.{node_id}"

    def _load_child(self, node_id):
        path = self._child_file(node_id)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return BTreeNode.deserialize(f.read())
        return BTreeNode()

    def _save_child(self, node, node_id):
        with open(self._child_file(node_id), 'w') as f:
            f.write(node.serialize())

    def search(self, key):
        return self._search_node(self.root, key)

    def _search_node(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return node.values[i]
        if node.leaf:
            return None
        return self._search_node(self._load_child(node.children[i]), key)

    def insert(self, key, value):
        root = self.root
        if len(root.keys) == self.t - 1:
            new_root = BTreeNode(leaf=False)
            old_id = self._get_next_node_id()
            self._save_child(root, old_id)
            new_root.children = [old_id]
            self.root = new_root
            self._split_child(new_root, 0, old_id)
        self._insert_non_full(self.root, key, value)
        self._save_root()

    def _insert_non_full(self, node, key, value):
        if node.leaf:
            i = len(node.keys) - 1
            while i >= 0 and key < node.keys[i]:
                i -= 1
            node.keys.insert(i + 1, key)
            node.values.insert(i + 1, value)
        else:
            i = len(node.keys) - 1
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            child_id = node.children[i]
            child = self._load_child(child_id)
            if len(child.keys) == self.t - 1:
                self._split_child(node, i, child_id)
                if key > node.keys[i]:
                    i += 1
                    child_id = node.children[i]
                    child = self._load_child(child_id)
            self._insert_non_full(child, key, value)
            self._save_child(child, child_id)

    def _split_child(self, parent, i, child_id):
        t = self.t
        child = self._load_child(child_id)
        new_child = BTreeNode(leaf=child.leaf)
        mid = (t - 1) // 2

        new_child.keys = child.keys[mid + 1:]
        new_child.values = child.values[mid + 1:]
        if not child.leaf:
            new_child.children = child.children[mid + 1:]
            child.children = child.children[:mid + 1]

        new_child_id = self._get_next_node_id()
        parent.keys.insert(i, child.keys[mid])
        parent.values.insert(i, child.values[mid])
        parent.children.insert(i + 1, new_child_id)

        child.keys = child.keys[:mid]
        child.values = child.values[:mid]

        self._save_child(child, child_id)
        self._save_child(new_child, new_child_id)

    def delete(self, key, value):
        self.root = self._delete(self.root, key, value)
        self._save_root()

    def _delete(self, node, key, value):
        if node.leaf:
            for i, (k, v) in enumerate(zip(node.keys, node.values)):
                if k == key and v == value:
                    node.keys.pop(i)
                    node.values.pop(i)
                    return node
            return node
        for i, k in enumerate(node.keys):
            if k == key:
                return node
        child_idx = 0
        while child_idx < len(node.keys) and key > node.keys[child_idx]:
            child_idx += 1
        child_id = node.children[child_idx]
        child = self._load_child(child_id)
        child = self._delete(child, key, value)
        self._save_child(child, child_id)
        return node

    def range_query(self, min_key, max_key):
        results = []
        self._range_query(self.root, min_key, max_key, results)
        return [v for _, v in results]

    def _range_query(self, node, min_key, max_key, results):
        for i, key in enumerate(node.keys):
            if min_key <= key <= max_key:
                results.append((key, node.values[i]))
        if not node.leaf:
            for child_id in node.children:
                self._range_query(self._load_child(child_id), min_key, max_key, results)

    def get_all(self):
        results = []
        self._get_all(self.root, results)
        return results

    def _get_all(self, node, results):
        for i, key in enumerate(node.keys):
            results.append((key, node.values[i]))
        if not node.leaf:
            for child_id in node.children:
                self._get_all(self._load_child(child_id), results)