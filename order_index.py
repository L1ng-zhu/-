import json
import os
from btree import BTree

class OrderIndex:
    def __init__(self, order_file="orders.dat"):
        self.order_file = order_file
        self.by_id = {}
        self.by_amount = BTree(order_file + ".idx.amount")
        self.by_urgency = BTree(order_file + ".idx.urgency")
        self.by_time = BTree(order_file + ".idx.time")
        self._load_from_disk()

    def _order_to_dict(self, order):
        return {
            'order_id': order.order_id,
            'start_time': order.start_time,
            'start_node': order.start_node,
            'end_node': order.end_node,
            'amount': order.amount,
            'urgency': order.urgency,
            'time_limit': order.time_limit,
            'status': order.status.value,
            'assigned_courier': order.assigned_courier,
            'assigned_time': order.assigned_time,
            'start_execute_time': order.start_execute_time,
            'completed_time': order.completed_time,
        }

    def _dict_to_order(self, d):
        from order_courier import Order, OrderStatus
        order = Order(
            d['order_id'], d['start_time'], d['start_node'], d['end_node'],
            d['amount'], d['urgency'], d['time_limit']
        )
        order.status = OrderStatus(d['status'])
        order.assigned_courier = d['assigned_courier']
        order.assigned_time = d['assigned_time']
        order.start_execute_time = d['start_execute_time']
        order.completed_time = d['completed_time']
        return order

    def _load_from_disk(self):
        if os.path.exists(self.order_file):
            with open(self.order_file, 'r') as f:
                for line in f:
                    if line.strip():
                        d = json.loads(line)
                        order = self._dict_to_order(d)
                        self.by_id[order.order_id] = order

    def insert(self, order):
        self.by_id[order.order_id] = order
        self.by_amount.insert(order.amount, order.order_id)
        self.by_urgency.insert(order.urgency, order.order_id)
        self.by_time.insert(order.start_time, order.order_id)
        self._save_order(order)

    def _save_order(self, order):
        with open(self.order_file, 'a') as f:
            f.write(json.dumps(self._order_to_dict(order)) + '\n')

    def delete(self, order_id):
        if order_id not in self.by_id:
            return False
        order = self.by_id[order_id]
        self.by_amount.delete(order.amount, order_id)
        self.by_urgency.delete(order.urgency, order_id)
        self.by_time.delete(order.start_time, order_id)
        del self.by_id[order_id]
        return True

    def update(self, order):
        old = self.by_id.get(order.order_id)
        if old:
            self.by_amount.delete(old.amount, order.order_id)
            self.by_urgency.delete(old.urgency, order.order_id)
            self.by_time.delete(old.start_time, order.order_id)
        self.by_id[order.order_id] = order
        self.by_amount.insert(order.amount, order.order_id)
        self.by_urgency.insert(order.urgency, order.order_id)
        self.by_time.insert(order.start_time, order.order_id)

    def search_by_id(self, order_id):
        return self.by_id.get(order_id)

    def range_query_amount(self, min_amount, max_amount):
        order_ids = self.by_amount.range_query(min_amount, max_amount)
        return [self.by_id[oid] for oid in order_ids if oid in self.by_id]

    def range_query_urgency(self, min_urg, max_urg):
        order_ids = self.by_urgency.range_query(min_urg, max_urg)
        return [self.by_id[oid] for oid in order_ids if oid in self.by_id]

    def range_query_time(self, min_time, max_time):
        order_ids = self.by_time.range_query(min_time, max_time)
        return [self.by_id[oid] for oid in order_ids if oid in self.by_id]

    def get_all_orders(self):
        return list(self.by_id.values())

    def __len__(self):
        return len(self.by_id)