import random
from city_network import CityNetwork
from order_courier import Order, Courier, OrderStatus, CourierStatus
from dispatch_system import DispatchSystem
from simulation import SimulationModule, Strategy, RevenueFirstStrategy, UrgencyFirstStrategy, BalancedStrategy

def create_sample_network():
    network = CityNetwork()
    for i in range(1, 10):
        network.add_node(i, {'name': f'Zone_{i}'})
    edges = [
        (1, 2, 5), (1, 3, 8), (2, 4, 3), (2, 5, 6),
        (3, 5, 2), (3, 6, 7), (4, 5, 4), (4, 7, 5),
        (5, 6, 1), (5, 8, 9), (6, 8, 3), (7, 8, 6),
        (7, 9, 2), (8, 9, 4)
    ]
    for from_node, to_node, weight in edges:
        network.add_edge(from_node, to_node, weight)
    return network

def create_sample_orders(count=20, base_time=1000):
    orders = []
    for i in range(count):
        order = Order(
            order_id=i + 1,
            start_time=base_time + i * 60,
            start_node=random.randint(1, 9),
            end_node=random.randint(1, 9),
            amount=random.uniform(10, 100),
            urgency=random.randint(1, 10),
            time_limit=random.randint(300, 1800)
        )
        orders.append(order)
    return orders

def create_sample_couriers(count=5):
    couriers = []
    for i in range(count):
        courier = Courier(
            courier_id=i + 1,
            current_node=random.randint(1, 9)
        )
        couriers.append(courier)
    return couriers

def visualize_city_network(network, title="City Network"):
    """Visualize the city network in ASCII format"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    
    node_layout = {
        1: (2, 0), 2: (8, 0), 3: (0, 2), 4: (10, 2), 5: (5, 2),
        6: (0, 4), 7: (10, 4), 8: (5, 4), 9: (5, 6), 10: (5, 8)
    }
    
    grid = [[' ' for _ in range(12)] for _ in range(9)]
    for node, (x, y) in node_layout.items():
        if node in network.nodes:
            grid[y][x] = str(node)
    
    for from_node in network.edges:
        for to_node in network.edges[from_node]:
            if from_node in node_layout and to_node in node_layout:
                weight = network.edges[from_node][to_node]
                fx, fy = node_layout[from_node]
                tx, ty = node_layout[to_node]
                
                if fx == tx:
                    for y in range(min(fy, ty) + 1, max(fy, ty)):
                        if grid[y][fx] == ' ':
                            grid[y][fx] = '|'
                elif fy == ty:
                    for x in range(min(fx, tx) + 1, max(fx, tx)):
                        if grid[fy][x] == ' ':
                            grid[fy][x] = '-'
                else:
                    if grid[min(fy, ty)][min(fx, tx)] == ' ':
                        grid[min(fy, ty)][min(fx, tx)] = '+'
    
    print("\n  " + "-" * 22)
    for y, row in enumerate(grid):
        print(f"{y} |", end="")
        print("".join(row), end="")
        print("|")
    print("  " + "-" * 22)
    
    print("\nNodes:", list(network.nodes.keys()))
    print("Edges (with weights):")
    edge_display = []
    for from_node in sorted(network.edges):
        for to_node in sorted(network.edges[from_node]):
            if from_node < to_node:
                edge_display.append(f"  {from_node} - {to_node}: {network.edges[from_node][to_node]}")
    print("\n".join(edge_display))


def compare_system_stats(before, after, description="Change"):
    """Compare system stats before and after change"""
    print("\n" + "=" * 60)
    print(f"System Stats Comparison: {description}")
    print("=" * 60)
    print(f"{'Metric':<25} {'Before':<10} {'After':<10} {'Change':<10}")
    print("-" * 60)
    
    all_keys = set(before.keys()).union(set(after.keys()))
    for key in sorted(all_keys):
        val_before = before.get(key, 'N/A')
        val_after = after.get(key, 'N/A')
        if isinstance(val_before, (int, float)) and isinstance(val_after, (int, float)):
            change = val_after - val_before
            change_str = f"{change:+}"
        else:
            change_str = 'N/A'
        print(f"{key:<25} {val_before:<10} {val_after:<10} {change_str:<10}")


def demo_basic_operations():
    print("=" * 60)
    print("Demo 1: Basic Operations")
    print("=" * 60)

    # Create and visualize initial network
    network = create_sample_network()
    visualize_city_network(network, "Initial City Network")

    system = DispatchSystem(network)

    # Add initial orders and couriers, record stats
    orders = create_sample_orders(5, base_time=1000)
    couriers = create_sample_couriers(3)
    
    print(f"\nAdding 5 orders and 3 couriers...")
    stats_before = system.get_system_stats()
    
    for order in orders:
        system.add_order(order)
    
    for courier in couriers:
        system.add_courier(courier)
    
    stats_after = system.get_system_stats()
    compare_system_stats(stats_before, stats_after, "Adding Initial Orders & Couriers")

    system.set_time(1050)
    print("\n--- Top Priority Orders (at time 1050) ---")
    top_orders = system.get_top_k_orders(3)
    for order in top_orders:
        print(f"  {order} Priority: {order.calculate_priority(system.current_time):.2f}")

    print("\n--- Path Calculation ---")
    if top_orders:
        order = top_orders[0]
        path, cost = system.calculate_path(order)
        print(f"  Order {order.order_id}: {order.start_node} -> {order.end_node}")
        print(f"  Path: {path}, Cost: {cost}")

    # Add a new node and edge
    print("\n" + "=" * 60)
    print("Adding Node 10 and Edge 9-10 (weight=3)")
    print("=" * 60)
    network.add_node(10, {'name': 'Zone_10'})
    network.add_edge(9, 10, 3)
    visualize_city_network(network, "Network After Adding Node 10 & Edge 9-10")

    # Delete an edge
    print("\n" + "=" * 60)
    print("Removing Edge 8-9")
    print("=" * 60)
    network.remove_edge(8, 9)
    visualize_city_network(network, "Network After Removing Edge 8-9")

    # Add a new order
    print("\n" + "=" * 60)
    print("Adding Order 6")
    print("=" * 60)
    stats_before = system.get_system_stats()
    new_order = Order(
        order_id=6,
        start_time=1050,
        start_node=10,
        end_node=5,
        amount=120.0,
        urgency=10,
        time_limit=200
    )
    system.add_order(new_order)
    stats_after = system.get_system_stats()
    compare_system_stats(stats_before, stats_after, "Adding High Priority Order 6")

    # Add a new courier
    print("\n" + "=" * 60)
    print("Adding Courier 4")
    print("=" * 60)
    stats_before = system.get_system_stats()
    new_courier = Courier(4, 10)
    system.add_courier(new_courier)
    stats_after = system.get_system_stats()
    compare_system_stats(stats_before, stats_after, "Adding Courier 4")

    # Remove an order
    print("\n" + "=" * 60)
    print("Removing Order 3")
    print("=" * 60)
    stats_before = system.get_system_stats()
    system.remove_order(3)
    stats_after = system.get_system_stats()
    compare_system_stats(stats_before, stats_after, "Removing Order 3")

    # Remove a courier
    print("\n" + "=" * 60)
    print("Removing Courier 2")
    print("=" * 60)
    stats_before = system.get_system_stats()
    system.remove_courier(2)
    stats_after = system.get_system_stats()
    compare_system_stats(stats_before, stats_after, "Removing Courier 2")

    print(f"\n--- Final System Stats ---")
    final_stats = system.get_system_stats()
    for k, v in final_stats.items():
        print(f"  {k}: {v}")

def demo_priority_calculation():
    print("\n" + "=" * 60)
    print("Demo 2: Priority Calculation Analysis")
    print("=" * 60)

    network = create_sample_network()
    system = DispatchSystem(network)
    base_time = 1000.0
    system.set_time(base_time)

    test_orders = [
        Order(1, base_time, 1, 5, 50, 5, 600),
        Order(2, base_time - 200, 2, 6, 100, 3, 300),
        Order(3, base_time - 100, 3, 7, 30, 9, 200),
        Order(4, base_time - 50, 4, 8, 80, 1, 900),
    ]

    for order in test_orders:
        system.add_order(order)

    print("\nOrder Priority Breakdown:")
    print("-" * 70)
    print(f"{'ID':<4} {'Amount':<8} {'Urgency':<8} {'Wait(s)':<8} {'TimeLimit':<10} {'Priority':<8}")
    print("-" * 70)
    for order in test_orders:
        waiting = system.current_time - order.start_time
        priority = order.calculate_priority(system.current_time)
        print(f"{order.order_id:<4} ${order.amount:<7.1f} {order.urgency:<8} {waiting:<8.0f} {order.time_limit:<10} {priority:<8.2f}")

def demo_order_assignment():
    print("\n" + "=" * 60)
    print("Demo 3: Order Assignment Process")
    print("=" * 60)

    network = create_sample_network()
    system = DispatchSystem(network)
    base_time = 1000.0
    system.set_time(base_time)

    orders = create_sample_orders(3, base_time=base_time)
    for order in orders:
        system.add_order(order)

    couriers = create_sample_couriers(2)
    for courier in couriers:
        system.add_courier(courier)

    print(f"\nBefore Assignment:")
    print(f"  Pending orders: {len(system.get_pending_orders())}")
    print(f"  Idle couriers: {len(system.get_idle_couriers())}")

    pending = system.get_pending_orders()
    idle = system.get_idle_couriers()

    assignments = []
    for i, order in enumerate(pending[:len(idle)]):
        courier = idle[i]
        if system.assign_order_to_courier(order, courier):
            assignments.append((order, courier))
            print(f"  Assigned Order {order.order_id} (${order.amount:.1f}, urgency={order.urgency}) to Courier {courier.courier_id}")

    print(f"\nAfter Assignment:")
    print(f"  Pending orders: {len(system.get_pending_orders())}")
    print(f"  Idle couriers: {len(system.get_idle_couriers())}")
    print(f"  Successful assignments: {len(assignments)}")

def demo_simulation():
    print("\n" + "=" * 60)
    print("Demo 4: System Simulation")
    print("=" * 60)

    import os
    # Clean up previous simulation data
    for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
        path = "orders.dat" + ext
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

    network = create_sample_network()
    system = DispatchSystem(network)

    for courier in create_sample_couriers(4):
        system.add_courier(courier)

    sim = SimulationModule(system)

    arrival_times = [100, 150, 200, 300, 350, 400, 500, 600]
    for i, t in enumerate(arrival_times):
        order = Order(
            order_id=i + 1,
            start_time=float(t),
            start_node=random.randint(1, 9),
            end_node=random.randint(1, 9),
            amount=random.uniform(20, 80),
            urgency=random.randint(1, 10),
            time_limit=random.randint(300, 1200)
        )
        sim.add_order_arrival_event(float(t), order)

    print("\nSimulation Setup:")
    print(f"  Couriers: 4")
    print(f"  Orders: 8 (arriving at times: {arrival_times})")
    print(f"  Duration: 1000 time units")

    sim.run_simulation(1000.0)

    results = sim.get_simulation_results()
    stats = results['final_stats']

    print("\n--- Simulation Results ---")
    print(f"  Completed Orders: {stats['completed_orders']}")
    print(f"  Pending Orders: {stats['pending_orders']}")
    print(f"  Total Revenue: ${stats['total_revenue']:.2f}")
    print(f"  Timeout Orders: {stats['timeout_orders']}")

def demo_strategy_comparison():
    print("\n" + "=" * 60)
    print("Demo 5: Strategy Comparison")
    print("=" * 60)

    duration = 800.0
    base_time = 1000.0

    strategies = [
        RevenueFirstStrategy(),
        UrgencyFirstStrategy(),
        BalancedStrategy()
    ]

    print("\nRunning simulations with different strategies...")
    print("-" * 70)

    for strategy in strategies:
        network = create_sample_network()
        system = DispatchSystem(network)
        system.set_time(base_time)

        for courier in create_sample_couriers(5):
            system.add_courier(courier)

        for i in range(15):
            order = Order(
                order_id=i + 1,
                start_time=base_time + random.randint(0, 400),
                start_node=random.randint(1, 9),
                end_node=random.randint(1, 9),
                amount=random.uniform(15, 100),
                urgency=random.randint(1, 10),
                time_limit=random.randint(200, 1000)
            )
            system.add_order(order)

        strategy.assign_orders(system)
        stats = system.get_system_stats()

        print(f"\n{strategy.name()}:")
        print(f"  Completed: {stats['completed_orders']}")
        print(f"  Pending: {stats['pending_orders']}")
        print(f"  Revenue: ${stats['total_revenue']:.2f}")
        print(f"  Busy Couriers: {stats['busy_couriers']}")

def demo_disk_index():
    print("\n" + "=" * 60)
    print("Demo 6: Disk-based Order Index")
    print("=" * 60)

    from order_index import OrderIndex
    from order_courier import Order
    import os

    test_file = "test_orders.dat"
    for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
        path = test_file + ext
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
    for i in range(10):
        path = f"{test_file}.idx.amount.child.{i}"
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

    index = OrderIndex(test_file)
    base_time = 1000.0

    print("\nInserting 10 test orders...")
    for i in range(10):
        order = Order(
            order_id=i + 1,
            start_time=base_time + i * 100,
            start_node=i % 9 + 1,
            end_node=(i + 3) % 9 + 1,
            amount=20 + i * 10,
            urgency=i % 10 + 1,
            time_limit=500 + i * 50
        )
        index.insert(order)

    print(f"Total orders in index: {len(index)}")

    print("\nRange query by amount (40-70):")
    results = index.range_query_amount(40, 70)
    for o in results:
        print(f"  Order {o.order_id}: amount=${o.amount}, urgency={o.urgency}")

    print("\nRange query by urgency (6-10):")
    results = index.range_query_urgency(6, 10)
    for o in results:
        print(f"  Order {o.order_id}: amount=${o.amount}, urgency={o.urgency}")

    for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
        path = test_file + ext
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
    for i in range(20):
        path = f"{test_file}.idx.amount.child.{i}"
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

def main():
    print("\n" + "#" * 60)
    print("# City Instant Service Platform - System Demonstration")
    print("#" * 60)

    demo_basic_operations()
    demo_priority_calculation()
    demo_order_assignment()
    demo_simulation()
    demo_strategy_comparison()
    demo_disk_index()

    print("\n" + "#" * 60)
    print("# All demonstrations completed!")
    print("#" * 60 + "\n")

if __name__ == "__main__":
    main()