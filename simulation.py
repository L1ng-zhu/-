import time
import random
from dispatch_system import DispatchSystem
from order_courier import Order, Courier, OrderStatus, CourierStatus
from city_network import CityNetwork

class SimulationEvent:
    def __init__(self, event_time, event_type, data=None):
        self.event_time = event_time
        self.event_type = event_type
        self.data = data or {}

    def __lt__(self, other):
        return self.event_time < other.event_time

class SimulationModule:
    def __init__(self, dispatch_system=None):
        self.dispatch_system = dispatch_system or DispatchSystem()
        self.event_queue = []
        self.history = []
        self.current_time = 0
        self.simulation_speed = 1.0

    def add_order_arrival_event(self, event_time, order):
        event = SimulationEvent(event_time, 'ORDER_ARRIVAL', {'order': order})
        self.event_queue.append(event)

    def add_order_complete_event(self, event_time, courier_id):
        event = SimulationEvent(event_time, 'ORDER_COMPLETE', {'courier_id': courier_id})
        self.event_queue.append(event)

    def add_courier_arrival_event(self, event_time, courier_id, node_id):
        event = SimulationEvent(event_time, 'COURIER_ARRIVAL', 
                                {'courier_id': courier_id, 'node_id': node_id})
        self.event_queue.append(event)

    def run_step(self):
        if not self.event_queue:
            return False

        self.event_queue.sort()
        event = self.event_queue.pop(0)
        self.current_time = event.event_time
        self.dispatch_system.set_time(self.current_time)

        if event.event_type == 'ORDER_ARRIVAL':
            self._handle_order_arrival(event)
        elif event.event_type == 'ORDER_COMPLETE':
            self._handle_order_complete(event)
        elif event.event_type == 'COURIER_ARRIVAL':
            self._handle_courier_arrival(event)
        elif event.event_type == 'EXECUTE_ORDER':
            self._handle_execute_order(event)

        self._record_history(event)
        return True

    def _handle_order_arrival(self, event):
        order = event.data['order']
        self.dispatch_system.add_order(order)
        
        # Try to assign this order to an idle courier
        idle_couriers = self.dispatch_system.get_idle_couriers()
        if idle_couriers:
            # Use first idle courier for simplicity
            courier = idle_couriers[0]
            path, cost = self.dispatch_system.calculate_path(order)
            if path:
                order.path = path
                order.path_cost = cost
                courier.assign_order(order)
                order.status = OrderStatus.IN_PROGRESS
                order.start_execute_time = self.current_time
                
                # Schedule completion event
                completion_time = self.current_time + cost
                self.add_order_complete_event(completion_time, courier.courier_id)

    def _handle_order_complete(self, event):
        courier_id = event.data['courier_id']
        courier = self.dispatch_system.couriers.get(courier_id)
        if courier and courier.current_order:
            order = courier.current_order
            order.status = OrderStatus.COMPLETED
            order.completed_time = self.current_time
            courier.total_earnings += order.amount
            courier.completed_orders += 1
            courier.current_order = None
            courier.status = CourierStatus.IDLE
            self.dispatch_system.order_index.update(order)

    def _handle_courier_arrival(self, event):
        courier_id = event.data['courier_id']
        node_id = event.data['node_id']
        courier = self.dispatch_system.couriers.get(courier_id)
        if courier:
            courier.current_node = node_id

    def _handle_execute_order(self, event):
        courier_id = event.data['courier_id']
        order_id = event.data['order_id']
        courier = self.dispatch_system.couriers.get(courier_id)
        order = self.dispatch_system.order_index.search_by_id(order_id)
        if courier and order:
            self.dispatch_system.execute_order(order, courier)

    def _record_history(self, event):
        stats = self.dispatch_system.get_system_stats()
        self.history.append({
            'time': self.current_time,
            'event_type': event.event_type,
            'stats': stats.copy()
        })

    def run_until(self, end_time):
        while self.event_queue and self.current_time < end_time:
            self.run_step()

    def run_simulation(self, duration):
        end_time = self.current_time + duration
        self.run_until(end_time)

    def get_simulation_results(self):
        return {
            'history': self.history,
            'final_stats': self.dispatch_system.get_system_stats()
        }

class Strategy:
    def name(self):
        return "Base Strategy"

    def select_order(self, pending_orders):
        if not pending_orders:
            return None
        return max(pending_orders, key=lambda o: o.calculate_priority(time.time()))

    def select_courier(self, order, idle_couriers):
        if not idle_couriers:
            return None
        return idle_couriers[0]

    def assign_orders(self, dispatch_system):
        pending = dispatch_system.get_pending_orders()
        idle = dispatch_system.get_idle_couriers()
        assignments = []

        for order in pending:
            courier = self.select_courier(order, idle)
            if courier:
                path, cost = dispatch_system.calculate_path(order)
                if path:
                    order.path = path
                    order.path_cost = cost
                    courier.assign_order(order)
                    order.status = OrderStatus.IN_PROGRESS
                    order.start_execute_time = dispatch_system.current_time
                    order.completed_time = dispatch_system.current_time + cost
                    order.status = OrderStatus.COMPLETED
                    courier.total_earnings += order.amount
                    courier.completed_orders += 1
                    courier.current_order = None
                    courier.status = CourierStatus.IDLE
                    dispatch_system.order_index.update(order)
                    idle.remove(courier)
                    assignments.append((order, courier))

        return assignments

class RevenueFirstStrategy(Strategy):
    def name(self):
        return "Revenue First"

    def select_order(self, pending_orders):
        if not pending_orders:
            return None
        return max(pending_orders, key=lambda o: o.amount * 0.6 + o.urgency * 10)

    def select_courier(self, order, idle_couriers):
        if not idle_couriers:
            return None
        return min(idle_couriers, 
                   key=lambda c: dispatch_system.city_network.dijkstra(c.current_node, order.start_node)[1]
                   if hasattr(dispatch_system, 'city_network') else 0)

class UrgencyFirstStrategy(Strategy):
    def name(self):
        return "Urgency First"

    def select_order(self, pending_orders):
        if not pending_orders:
            return None
        return max(pending_orders, key=lambda o: o.urgency * 20 + o.amount * 0.1)

    def select_courier(self, order, idle_couriers):
        if not idle_couriers:
            return None
        return min(idle_couriers, key=lambda c: c.current_node == order.start_node)

def run_strategy_simulation(strategy, city_network, orders_data, couriers_data, duration):
    dispatch_system = DispatchSystem(city_network)

    for courier_data in couriers_data:
        courier = Courier(**courier_data)
        dispatch_system.add_courier(courier)

    simulation = SimulationModule(dispatch_system)

    for order_data in orders_data:
        order = Order(**order_data)
        simulation.add_order_arrival_event(order.start_time, order)

    for i in range(len(orders_data)):
        simulation.add_order_complete_event(duration + i * 100, i + 1)

    strategy.assign_orders(dispatch_system)
    simulation.run_simulation(duration)

    return simulation.get_simulation_results()

dispatch_system = None

class BalancedStrategy(Strategy):
    def name(self):
        return "Balanced Priority"

    def select_order(self, pending_orders):
        if not pending_orders:
            return None
        current_time = time.time()
        return max(pending_orders, key=lambda o: o.calculate_priority(current_time))

    def select_courier(self, order, idle_couriers):
        if not idle_couriers:
            return None
        if hasattr(dispatch_system, 'city_network'):
            return min(idle_couriers,
                      key=lambda c: dispatch_system.city_network.dijkstra(c.current_node, order.start_node)[1])
        return idle_couriers[0]