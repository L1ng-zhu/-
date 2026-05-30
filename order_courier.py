from enum import IntEnum

class OrderStatus(IntEnum):
    PENDING = 0
    ASSIGNED = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    CANCELLED = 4
    TIMEOUT = 5

class Order:
    def __init__(self, order_id, start_time, start_node, end_node,
                 amount, urgency, time_limit):
        self.order_id = order_id
        self.start_time = float(start_time)
        self.start_node = start_node
        self.end_node = end_node
        self.amount = float(amount)
        self.urgency = int(urgency)
        self.time_limit = float(time_limit)
        self.status = OrderStatus.PENDING
        self.assigned_courier = None
        self.assigned_time = None
        self.start_execute_time = None
        self.completed_time = None
        self.path = None
        self.path_cost = None

    def calculate_priority(self, current_time=None):
        if current_time is None:
            current_time = self.start_time
        waiting_time = max(0, current_time - self.start_time)
        base_urgency = self.urgency * 20
        base_amount = self.amount * 0.5
        wait_factor = min(waiting_time / max(self.time_limit, 1), 1.0) * 30
        time_pressure = max(0, (1.0 - waiting_time / max(self.time_limit, 1))) * 50
        priority = base_urgency + base_amount + wait_factor + time_pressure
        return priority

    def is_timeout(self, current_time):
        if self.status == OrderStatus.COMPLETED:
            return False
        return current_time - self.start_time > self.time_limit
    
    def get_waiting_time(self, current_time):
        return current_time - self.start_time
    
    def calculate_penalty(self, check_time=None):
        if self.status != OrderStatus.COMPLETED:
            return 0.0
        
        if check_time is None:
            check_time = self.completed_time if self.completed_time else self.start_time + self.time_limit + 1
        
        delay = check_time - (self.start_time + self.time_limit)
        
        if delay <= 0:
            return 0.0
        elif delay <= 10:
            return 0.0
        elif delay <= 15:
            return self.amount * 0.20
        elif delay <= 20:
            return self.amount * 0.40
        else:
            return self.amount * 1.00
    
    def calculate_actual_revenue(self, check_time=None):
        if self.status != OrderStatus.COMPLETED:
            return 0.0
        
        penalty = self.calculate_penalty(check_time)
        return max(0, self.amount - penalty)

    def __repr__(self):
        return (f"Order({self.order_id}, status={self.status.name}, "
                f"from={self.start_node}->{self.end_node}, "
                f"amount={self.amount:.1f}, urgency={self.urgency})")

class CourierStatus(IntEnum):
    IDLE = 0
    BUSY = 1
    OFFLINE = 2

class Courier:
    def __init__(self, courier_id, current_node):
        self.courier_id = courier_id
        self.current_node = current_node
        self.status = CourierStatus.IDLE
        self.current_order = None
        self.completed_orders = 0
        self.total_earnings = 0.0

    def assign_order(self, order):
        self.current_order = order
        self.status = CourierStatus.BUSY
        order.status = OrderStatus.ASSIGNED
        order.assigned_courier = self.courier_id
        order.assigned_time = order.start_time

    def complete_order(self, completed_time, apply_penalty=False):
        if self.current_order:
            self.current_order.status = OrderStatus.COMPLETED
            self.current_order.completed_time = completed_time
            
            if apply_penalty:
                actual_revenue = self.current_order.calculate_actual_revenue(completed_time)
                self.total_earnings += actual_revenue
            else:
                self.total_earnings += self.current_order.amount
                
            self.completed_orders += 1
            self.current_order = None
        self.status = CourierStatus.IDLE

    def cancel_order(self):
        if self.current_order:
            self.current_order.status = OrderStatus.CANCELLED
            self.current_order = None
        self.status = CourierStatus.IDLE

    def __repr__(self):
        return (f"Courier({self.courier_id}, status={self.status.name}, "
                f"node={self.current_node})")
