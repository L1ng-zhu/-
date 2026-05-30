import random
from city_network import CityNetwork
from order_courier import Order, Courier, OrderStatus, CourierStatus
from dispatch_system import DispatchSystem
from simulation import SimulationModule, Strategy, RevenueFirstStrategy, UrgencyFirstStrategy, BalancedStrategy

random.seed(114514)

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

    import os
    # Clean up previous demo data
    for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
        path = "orders.dat" + ext
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

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

    import os
    # Clean up previous demo data
    for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
        path = "orders.dat" + ext
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

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

    import os
    # Clean up previous demo data
    for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
        path = "orders.dat" + ext
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

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
    import os
    print("\n" + "=" * 60)
    print("Demo 4: System Simulation (Time Unit = Minutes)")
    print("=" * 60)

    # === SCENARIO 1: Normal Simulation ===
    print("\n" + "="*60)
    print("SCENARIO 1: Normal Simulation (20-50 min Time Limits)")
    print("="*60)
    
    # Clean up
    for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
        path = "orders.dat" + ext
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
    
    network1 = create_sample_network()
    system1 = DispatchSystem(network1)
    
    for courier in create_sample_couriers(5):
        system1.add_courier(courier)
    
    sim1 = SimulationModule(system1, verbose=True)
    
    arrival_times1 = [10, 15, 25, 40, 60, 65, 70, 80]
    for i, t in enumerate(arrival_times1):
        order = Order(
            order_id=i + 1,
            start_time=float(t),
            start_node=random.randint(1, 9),
            end_node=random.randint(1, 9),
            amount=random.uniform(20, 80),
            urgency=random.randint(1, 10),
            time_limit=random.randint(20, 50)
        )
        sim1.add_order_arrival_event(float(t), order)

    # Run the simulation
    sim1.run_simulation(200.0)
    
    # Export logs to Excel
    excel_file1 = sim1.export_logs_to_excel('scenario1_normal.xlsx')
    print(f"\n[OK] Detailed logs exported to: {excel_file1}")
    
    results1 = sim1.get_simulation_results()
    stats1 = results1['final_stats']
    
    print("\n--- Scenario 1 Results (Normal) ---")
    print(f"  Completed Orders: {stats1['completed_orders']}")
    print(f"  Pending Orders: {stats1['pending_orders']}")
    print(f"  On-Time Completed: {stats1['on_time_orders']}")
    print(f"  Delayed Orders: {stats1['delayed_orders']}")
    print(f"  Timeout Orders: {stats1['timeout_orders']}")
    print(f"  Avg Wait Time: {stats1['avg_waiting_time']:.1f} min")
    print(f"  Total Penalty: ${stats1['total_penalty']:.2f}")
    print(f"  Net Revenue: ${stats1['total_revenue']:.2f}")
    print(f"  Idle Couriers: {stats1['idle_couriers']}")
    print(f"  Busy Couriers: {stats1['busy_couriers']}")
    
    # SCENARIO 2: Order Surge - 15 orders arriving within 5 time units
    print("\n" + "=" * 60)
    print("SCENARIO 2: ORDER SURGE")
    print("  15 orders arriving within 5 min, 5 couriers (20-50 min Time Limits)")
    print("=" * 60)
    
    # Clean up
    for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
        path = "orders.dat" + ext
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
    
    network2 = create_sample_network()
    system2 = DispatchSystem(network2)
    
    # Add 5 couriers for surge scenario
    for courier in create_sample_couriers(5):
        system2.add_courier(courier)
    
    sim2 = SimulationModule(system2, verbose=False)
    
    # 15 orders arriving at times 100-105 (5 time units)
    base_time = 10
    for i in range(15):
        order = Order(
            order_id=i + 1,
            start_time=float(base_time + i * 0.33),  # Spread within 5 units
            start_node=random.randint(1, 9),
            end_node=random.randint(1, 9),
            amount=random.uniform(30, 100),  # Higher amounts during surge
            urgency=random.randint(5, 10),  # Higher urgency
            time_limit=random.randint(20, 40)  # Tighter time limits
        )
        sim2.add_order_arrival_event(order.start_time, order)
    
    print("\nOrders arriving: 15 orders from T=10 to T=15 (within 5 min)")
    print("Couriers available: 5")
    print("Order amounts: $30-$100 (surge pricing)")
    print("Order urgency: 5-10 (high priority)")
    print("Time limits: 20-50 min")
    
    sim2.run_simulation(200.0)  # Run until T=200
    
    # Export logs to Excel
    excel_file2 = sim2.export_logs_to_excel('scenario2_surge.csv')
    print(f"\n[OK] Detailed logs exported to: {excel_file2}")
    
    results2 = sim2.get_simulation_results()
    stats2 = results2['final_stats']
    
    print("\n--- Scenario 2 Results (Order Surge) ---")
    print(f"  Completed Orders: {stats2['completed_orders']}")
    print(f"  Pending Orders: {stats2['pending_orders']}")
    print(f"  On-Time Completed: {stats2['on_time_orders']}")
    print(f"  Delayed Orders: {stats2['delayed_orders']}")
    print(f"  Timeout Orders: {stats2['timeout_orders']}")
    print(f"  Avg Wait Time: {stats2['avg_waiting_time']:.1f} min")
    print(f"  Total Penalty: ${stats2['total_penalty']:.2f}")
    print(f"  Net Revenue: ${stats2['total_revenue']:.2f}")
    print(f"  Idle Couriers: {stats2['idle_couriers']}")
    print(f"  Busy Couriers: {stats2['busy_couriers']}")
    
    if stats2['timeout_orders'] > 0:
        print(f"\n  [WARNING] {stats2['timeout_orders']} orders TIMED OUT due to surge!")
    
    # SCENARIO 3: Heavy Rain - Edge weights increased
    print("\n" + "=" * 60)
    print("SCENARIO 3: HEAVY RAIN")
    print("  All road weights increased by 1.5x-3x (random) (20-50 min Time Limits)")
    print("=" * 60)
    
    # Clean up
    for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
        path = "orders.dat" + ext
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
    
    network3 = create_sample_network()
    
    # Apply rain effect - increase all edge weights
    print("\nApplying rain effect to roads (time unit = min):")
    rain_multipliers = {}
    for from_node in list(network3.edges.keys()):
        for to_node in list(network3.edges[from_node].keys()):
            if from_node < to_node:  # Only show each edge once
                original_weight = network3.edges[from_node][to_node]
                # Random multiplier between 1.5 and 3.0
                rain_multiplier = random.uniform(1.5, 3.0)
                rain_multipliers[(from_node, to_node)] = rain_multiplier
                new_weight = int(original_weight * rain_multiplier)
                network3.update_edge(from_node, to_node, new_weight)
                print(f"  Road {from_node}-{to_node}: {original_weight} min -> {new_weight} min (×{rain_multiplier:.2f})")
    
    system3 = DispatchSystem(network3)
    
    # Same couriers as scenario 1
    for courier in create_sample_couriers(5):
        system3.add_courier(courier)
    
    sim3 = SimulationModule(system3, verbose=False)
    
    # Same orders as scenario 1
    for i, t in enumerate(arrival_times1):
        order = Order(
            order_id=i + 1,
            start_time=float(t),
            start_node=random.randint(1, 9),
            end_node=random.randint(1, 9),
            amount=random.uniform(30, 100), # Higher amounts during rain
            urgency=random.randint(1, 10),
            time_limit=random.randint(30, 55) # wider time limits for rain
        )
        sim3.add_order_arrival_event(float(t), order)
    
    print(f"\nSame 8 orders and 5 couriers as Scenario 1")
    print(f"But now roads are affected by heavy rain...")
    
    sim3.run_simulation(200.0)
    
    # Export logs to Excel
    excel_file3 = sim3.export_logs_to_excel('scenario3_rain.xlsx')
    print(f"\n[OK] Detailed logs exported to: {excel_file3}")
    
    results3 = sim3.get_simulation_results()
    stats3 = results3['final_stats']
    
    print("\n--- Scenario 3 Results (Heavy Rain) ---")
    print(f"  Completed Orders: {stats3['completed_orders']}")
    print(f"  Pending Orders: {stats3['pending_orders']}")
    print(f"  On-Time Completed: {stats3['on_time_orders']}")
    print(f"  Delayed Orders: {stats3['delayed_orders']}")
    print(f"  Timeout Orders: {stats3['timeout_orders']}")
    print(f"  Avg Wait Time: {stats3['avg_waiting_time']:.1f} min")
    print(f"  Total Penalty: ${stats3['total_penalty']:.2f}")
    print(f"  Net Revenue: ${stats3['total_revenue']:.2f}")
    print(f"  Idle Couriers: {stats3['idle_couriers']}")
    print(f"  Busy Couriers: {stats3['busy_couriers']}")
    
    # COMPARISON SUMMARY
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print(f"{'Metric':<25} {'Normal':<12} {'Surge':<12} {'Rain':<12}")
    print("-" * 70)
    print(f"{'Completed Orders':<25} {stats1['completed_orders']:<12} {stats2['completed_orders']:<12} {stats3['completed_orders']:<12}")
    print(f"{'Pending Orders':<25} {stats1['pending_orders']:<12} {stats2['pending_orders']:<12} {stats3['pending_orders']:<12}")
    print(f"{'Timeout Orders':<25} {stats1['timeout_orders']:<12} {stats2['timeout_orders']:<12} {stats3['timeout_orders']:<12}")
    print(f"{'On-Time Orders':<25} {stats1['on_time_orders']:<12} {stats2['on_time_orders']:<12} {stats3['on_time_orders']:<12}")
    print(f"{'Delayed Orders':<25} {stats1['delayed_orders']:<12} {stats2['delayed_orders']:<12} {stats3['delayed_orders']:<12}")
    print(f"{'Avg Wait Time (min)':<25} {stats1['avg_waiting_time']:<12.1f} {stats2['avg_waiting_time']:<12.1f} {stats3['avg_waiting_time']:<12.1f}")
    print(f"{'Total Penalty ($)':<25} ${stats1['total_penalty']:<11.2f} ${stats2['total_penalty']:<11.2f} ${stats3['total_penalty']:<11.2f}")
    print(f"{'Net Revenue ($)':<25} ${stats1['total_revenue']:<11.2f} ${stats2['total_revenue']:<11.2f} ${stats3['total_revenue']:<11.2f}")

def demo_strategy_comparison():
    print("\n" + "=" * 60)
    print("Demo 5: Strategy Comparison (Time Unit = Minutes)")
    print("=" * 60)

    import os
    # Clean up previous demo data
    for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
        path = "orders.dat" + ext
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

    duration = 200.0  # Simulation runs for 200 minutes
    base_time = 10.0  # Start from minute 10

    strategies = [
        RevenueFirstStrategy(),
        UrgencyFirstStrategy(),
        BalancedStrategy()
    ]

    print("\nSimulation Setup:")
    print(f"  Duration: {duration} min")
    print(f"  Orders: 15")
    print(f"  Time limit range: 20-50 min")
    print(f"  Couriers: 5")
    print("\nRunning simulations with different strategies...")
    print("-" * 70)

    for strategy in strategies:
        network = create_sample_network()
        system = DispatchSystem(network)
        system.set_time(base_time)

        for courier in create_sample_couriers(5):
            system.add_courier(courier)

        for i in range(30):
            order = Order(
                order_id=i + 1,
                start_time=base_time + random.randint(0, 80),  # Arrives between 10-90 min
                start_node=random.randint(1, 9),
                end_node=random.randint(1, 9),
                amount=random.uniform(15, 100),
                urgency=random.randint(1, 10),
                time_limit=random.randint(20, 50)  # 20-50 min time limit
            )
            system.add_order(order)

        strategy.assign_orders(system)
        stats = system.get_system_stats()

        print(f"\n{strategy.name()}:")
        print(f"  Completed Orders: {stats['completed_orders']}")
        print(f"  Pending Orders: {stats['pending_orders']}")
        print(f"  On-Time Completed: {stats['on_time_orders']}")
        print(f"  Delayed Orders: {stats['delayed_orders']}")
        print(f"  Timeout Orders: {stats['timeout_orders']}")
        print(f"  Avg Wait Time: {stats['avg_waiting_time']:.1f} min")
        print(f"  Total Penalty: ${stats['total_penalty']:.2f}")
        print(f"  Net Revenue: ${stats['total_revenue']:.2f}")
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