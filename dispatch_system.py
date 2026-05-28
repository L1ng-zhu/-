import time
from city_network import CityNetwork
from order_courier import Order, Courier, OrderStatus, CourierStatus
from order_index import OrderIndex
from queue import PriorityQueue

class DispatchSystem:
    def __init__(self, city_network=None):
        self.city_network = city_network or CityNetwork()
        self.order_index = OrderIndex()
        self.couriers = {}
        self.pending_orders = PriorityQueue()
        self.current_time = 0

    def add_order(self, order):
        self.order_index.insert(order)
        self.pending_orders.put((-order.calculate_priority(self.current_time), order.order_id))

    def remove_order(self, order_id):
        order = self.order_index.search_by_id(order_id)
        if order:
            self.order_index.delete(order_id)
            return True
        return False

    def update_order(self, order):
        self.order_index.update(order)

    def add_courier(self, courier):
        self.couriers[courier.courier_id] = courier

    def remove_courier(self, courier_id):
        if courier_id in self.couriers:
            del self.couriers[courier_id]
            return True
        return False

    def update_courier_status(self, courier_id, status):
        if courier_id in self.couriers:
            self.couriers[courier_id].status = status
            return True
        return False

    def calculate_path(self, order):
        path, cost = self.city_network.dijkstra(order.start_node, order.end_node)
        return path, cost

    def get_top_k_orders(self, k):
        all_orders = [o for o in self.order_index.get_all_orders() 
                     if o.status == OrderStatus.PENDING]
        all_orders.sort(key=lambda o: o.calculate_priority(self.current_time), reverse=True)
        return all_orders[:k]

    def get_next_priority_order(self):
        top = self.get_top_k_orders(1)
        return top[0] if top else None

    def assign_order_to_courier(self, order, courier):
        if courier.status != CourierStatus.IDLE:
            return False
        path, cost = self.calculate_path(order)
        if path is None:
            return False
        order.path = path
        order.path_cost = cost
        courier.assign_order(order)
        return True

    def execute_order(self, order, courier):
        order.status = OrderStatus.IN_PROGRESS
        order.start_execute_time = self.current_time
        courier.current_node = order.end_node

    def complete_order(self, courier):
        if courier.current_order:
            courier.complete_order(self.current_time)
            self.order_index.update(courier.current_order)

    def get_idle_couriers(self):
        return [c for c in self.couriers.values() if c.status == CourierStatus.IDLE]

    def get_pending_orders(self):
        return [o for o in self.order_index.get_all_orders() 
                if o.status == OrderStatus.PENDING]

    def advance_time(self, delta):
        self.current_time += delta

    def set_time(self, t):
        self.current_time = t

    def get_system_stats(self):
        orders = self.order_index.get_all_orders()
        completed = [o for o in orders if o.status == OrderStatus.COMPLETED]
        pending = [o for o in orders if o.status == OrderStatus.PENDING]
        in_progress = [o for o in orders if o.status == OrderStatus.IN_PROGRESS]
        idle_couriers = self.get_idle_couriers()
        busy_couriers = [c for c in self.couriers.values() if c.status == CourierStatus.BUSY]

        total_revenue = sum(o.amount for o in completed)
        timeout_orders = [o for o in orders if o.is_timeout(self.current_time)]

        return {
            'current_time': self.current_time,
            'total_orders': len(orders),
            'completed_orders': len(completed),
            'pending_orders': len(pending),
            'in_progress_orders': len(in_progress),
            'total_couriers': len(self.couriers),
            'idle_couriers': len(idle_couriers),
            'busy_couriers': len(busy_couriers),
            'total_revenue': total_revenue,
            'timeout_orders': len(timeout_orders)
        }

    def reset(self):
        self.order_index = OrderIndex()
        self.couriers = {}
        self.current_time = 0
        while not self.pending_orders.empty():
            self.pending_orders.get()