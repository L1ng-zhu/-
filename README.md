[README.md](https://github.com/user-attachments/files/28422392/README.md)
# 城市即时配送平台

一个基于数据结构与算法的城市即时配送平台模拟系统，用于研究订单调度、路径规划、索引优化等核心技术问题。

## 项目概述

本项目实现了一个完整的即时配送模拟系统，包含以下核心功能：

- 城市网络建模与路径规划
- 订单与快递员管理
- 基于优先级的订单调度
- 基于B树的磁盘索引
- 离散事件仿真
- 多种调度策略对比
- 可视化演示

## 项目结构

```
.
├── main.py                # 主程序入口，包含所有演示功能
├── city_network.py        # 城市网络与路径规划实现
├── order_courier.py       # 订单和快递员数据模型
├── dispatch_system.py     # 调度系统核心逻辑
├── order_index.py         # 基于B树的订单索引
├── btree.py               # B树实现
├── simulation.py          # 离散事件仿真与调度策略
├── cleanup.py             # 清理工具
└── cleanup_all.py         # 完整清理工具
```

## 核心功能模块

### 1. 城市网络与路径规划 (city\_network.py)

#### 功能设计

- 使用邻接表表示城市道路网络
- 节点代表配送区域，边代表道路，权重代表通行时间
- 支持动态添加/删除节点和边
- 支持动态更新道路权重（如暴雨天气）

#### 核心算法：Dijkstra最短路径

```python
def dijkstra(self, start, end):
    # 使用优先队列实现的Dijkstra算法
    import heapq
    # 初始化距离字典和前驱字典
    dist = {node: float('inf') for node in self.nodes}
    prev = {node: None for node in self.nodes}
    dist[start] = 0
    pq = [(0, start)]  # (距离, 节点)
    
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == end:
            break  # 提前终止
        # 遍历邻居
        for v in self.get_neighbors(u):
            w = self.get_weight(u, v)
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                heapq.heappush(pq, (dist[v], v))
    
    # 重构路径
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()
    return path, dist[end]
```

#### 时间复杂度分析

- **Dijkstra算法（使用优先队列）**：O((V + E) log V)
  - V为节点数，E为边数
  - 优先队列操作：O(log V)
  - 每个节点松弛操作：O(E log V)
- **空间复杂度**：O(V + E)
  - 邻接表存储：O(E)
  - 距离字典和前驱字典：O(V)
  - 优先队列：O(V)

### 2. 订单与快递员模型 (order\_courier.py)

#### 功能设计

- 订单状态管理：待分配、已分配、配送中、已完成、已取消、超时
- 快递员状态管理：空闲、忙碌、离线
- 优先级计算：综合考虑金额、紧急度、等待时间、时间压力
- 超时惩罚机制：延迟10-15分钟罚款20%，15-20分钟罚款40%，超过20分钟罚款100%

#### 优先级计算公式

```
优先级 = 紧急度 * 20 + 金额 * 0.5 + 等待因子 + 时间压力
其中：
- 等待因子 = min(等待时间/时间限制, 1.0) * 30
- 时间压力 = max(0, 1 - 等待时间/时间限制) * 50
```

### 3. 调度系统 (dispatch\_system.py)

#### 功能设计

- 订单添加/删除/更新
- 快递员添加/删除/状态管理
- 优先级订单查询（Top K）
- 订单分配与路径计算
- 系统状态统计

#### 关键实现

```python
def get_top_k_orders(self, k):
    # 获取优先级最高的K个待处理订单
    all_orders = [o for o in self.order_index.get_all_orders() 
                 if o.status == OrderStatus.PENDING]
    all_orders.sort(key=lambda o: o.calculate_priority(self.current_time), reverse=True)
    return all_orders[:k]
```

#### 时间复杂度分析

- **Top K优先级查询**：O(N log N)
  - 排序操作：O(N log N)
  - 使用堆优化可降至O(N + K log N)
- **系统状态统计**：O(N)
  - 遍历所有订单进行统计

### 4. B树索引 (btree.py)

#### 功能设计

- 32阶B树实现（ORDER=32）
- 支持磁盘持久化存储
- 支持插入、删除、搜索、范围查询
- 节点分裂与合并优化

#### 核心数据结构

```python
class BTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.values = []
        self.children = []

class BTree:
    ORDER = 32
    # 插入、删除、搜索、范围查询
```

#### 时间复杂度分析

- **B树操作（搜索、插入、删除）**：O(log\_t N)
  - t为阶数（此处为32）
  - N为键值对数量
  - 树高度：O(log\_t N)
- **范围查询**：O(K + log\_t N)
  - K为结果数量
- **空间复杂度**：O(N)

### 5. 订单索引管理 (order\_index.py)

#### 功能设计

- 多重索引：ID、金额、紧急度、时间
- 基于B树的磁盘索引
- 支持按金额、紧急度、时间的范围查询
- 数据持久化与恢复

#### 索引结构

```python
class OrderIndex:
    def __init__(self, order_file="orders.dat"):
        self.order_file = order_file
        self.by_id = {}  # 内存哈希索引，用于ID快速查找
        self.by_amount = BTree(order_file + ".idx.amount")  # 按金额的B树索引
        self.by_urgency = BTree(order_file + ".idx.urgency")  # 按紧急度的B树索引
        self.by_time = BTree(order_file + ".idx.time")  # 按时间的B树索引
```

### 6. 离散事件仿真 (simulation.py)

#### 功能设计

- 事件驱动仿真架构
- 订单到达、完成事件处理
- 暴雨天气模拟
- 订单蜂拥场景模拟
- 详细日志记录与导出

#### 仿真事件类型

- ORDER\_ARRIVAL：订单到达
- ORDER\_COMPLETE：订单完成
- COURIER\_ARRIVAL：快递员到达
- EXECUTE\_ORDER：执行订单

#### 调度策略

1. **Revenue First（收益优先）**：优先选择金额高的订单
2. **Urgency First（紧急度优先）**：优先选择紧急度高的订单
3. **Balanced Priority（综合优先级）**：综合考虑金额、紧急度、等待时间

#### 时间复杂度分析

- **仿真运行**：O(E log E)
  - E为事件数量
  - 事件排序：O(E log E)
- **策略分配**：O(P \* C \* (V + E) log V)
  - P为待处理订单数
  - C为空闲快递员数
  - 每个路径计算：O((V + E) log V)

## 演示功能

### 1. 基础操作演示 (demo\_basic\_operations)

#### 功能说明

- 城市网络可视化
- 订单添加/删除
- 快递员添加/删除
- 节点和边的动态增删
- 系统状态对比展示

#### 核心代码

```python
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
    # (a,b,c)代表链接节点a和b的边权重为c
    for from_node, to_node, weight in edges:
        network.add_edge(from_node, to_node, weight)
    return network
```

#### 输出结果

```
============================
Initial City Network
============================

  ----------------------
0 |+ 1-----2   |
1 |            |
2 |3----5----4 |
3 ||    |    | |
4 |6----8----7 |
5 |     |      |
6 |     9      |
7 |            |
8 |            |
  ----------------------

Nodes: [1, 2, 3, 4, 5, 6, 7, 8, 9]
Edges (with weights):
  1 - 2: 5
  1 - 3: 8
  2 - 4: 3
  2 - 5: 6
  ...
```

#### 系统状态对比

```
System Stats Comparison: Adding Initial Orders & Couriers
============================================================
Metric                    Before     After      Change    
------------------------------------------------------------
total_orders              0          5          +5
pending_orders            0          5          +5
idle_couriers             0          3          +3
total_revenue             0          0          +0
```

***

### 2. 优先级计算分析 (demo\_priority\_calculation)

#### 功能说明

- 展示订单优先级的各项因子
- 可视化不同属性对优先级的影响

#### 核心代码

```python
def calculate_priority(self, current_time=None):
    if current_time is None:
        current_time = self.start_time
    waiting_time = max(0, current_time - self.start_time)
    base_urgency = self.urgency * 20      # 紧急度基础分
    base_amount = self.amount * 0.5       # 金额基础分
    wait_factor = min(waiting_time / max(self.time_limit, 1), 1.0) * 30  # 等待时间因子
    time_pressure = max(0, (1.0 - waiting_time / max(self.time_limit, 1))) * 50  # 时间压力
    priority = base_urgency + base_amount + wait_factor + time_pressure
    return priority
```

#### 输出结果

```
Order Priority Breakdown:
----------------------------------------------------------------------
ID   Amount   Urgency  Wait(s)  TimeLimit  Priority
----------------------------------------------------------------------
1    $50.0    5        0        600.0      175.00
2    $100.0   3        200      300.0      146.67
3    $30.0    9        100      200.0      235.00
4    $80.0    1        50       900.0      108.89
```

***

### 3. 订单分配流程 (demo\_order\_assignment)

#### 功能说明

- 订单分配过程可视化
- 路径计算与展示

#### 核心代码

```python
def assign_order_to_courier(self, order, courier):
    if courier.status != CourierStatus.IDLE:
        return False
    path, cost = self.calculate_path(order)  # 使用Dijkstra计算路径
    if path is None:
        return False
    order.path = path
    order.path_cost = cost
    courier.assign_order(order)
    return True
```

#### 输出结果

```
Before Assignment:
  Pending orders: 3
  Idle couriers: 2
  Assigned Order 1 ($61.7, urgency=3) to Courier 1
  Assigned Order 2 ($92.1, urgency=6) to Courier 2

After Assignment:
  Pending orders: 1
  Idle couriers: 0
  Successful assignments: 2
```

***

### 4. 系统仿真 (demo\_simulation)

#### 功能说明

- 正常场景仿真
- 订单蜂拥场景仿真（5分钟内到达15个订单）
- 暴雨天气场景仿真（道路权重上升1.5-3倍）
- 结果对比与分析
- 日志导出（CSV格式）

#### 核心代码

```python
def run_simulation(self, duration):
    end_time = self.current_time + duration
    while self.event_queue and self.current_time < end_time:
        self.run_step()  # 按事件驱动方式处理

def _handle_order_arrival(self, event):
    order = event.data['order']
    self.dispatch_system.add_order(order)
    idle_couriers = self.dispatch_system.get_idle_couriers()
    if idle_couriers:
        courier = idle_couriers[0]
        path, cost = self.dispatch_system.calculate_path(order)
        if path:
            courier.assign_order(order)
            order.status = OrderStatus.IN_PROGRESS
            # 安排订单完成事件
            completion_time = self.current_time + cost
            self.add_order_complete_event(completion_time, courier.courier_id)
```

#### 输出结果

**场景1：正常仿真（详细输出日志见scenario1\_normal\_1780145652.csv）**

```
[T=10] ORDER ARRIVAL: Order 1
  Route: Node 8 -> Node 7
  Amount: $20.22, Urgency: 9
  -> ASSIGNED to Courier 1
  -> Path: 8 -> 7
  -> Estimated completion at T=16

[T=16] ORDER COMPLETE: Order 1
  Original amount: $20.22
  Revenue earned: $20.22
  Courier 1 is now IDLE

--- Scenario 1 Results (Normal) ---
  Completed Orders: 8
  On-Time Completed: 8
  Delayed Orders: 0
  Total Penalty: $0.00
  Net Revenue: $339.40
```

**sce场景2：订单蜂拥（详细输出日志见scenario2\_surge\_1780145658.csv）**

```
Orders arriving: 15 orders from T=10 to T=15 (within 5 min)
Couriers available: 5

--- Scenario 2 Results (Order Surge) ---
  Completed Orders: 15
  On-Time Completed: 14
  Delayed Orders: 1
  Total Penalty: $0.00
  Net Revenue: $917.94
```

**场景3：暴雨天气（详细输出日志见scenario3\_rain\_1780145658.csv）**

```
Applying rain effect to roads (time unit = min):
  Road 1-2: 5 min -> 11 min (×2.27)
  Road 1-3: 8 min -> 16 min (×2.07)
  Road 2-4: 3 min -> 7 min (×2.35)
  ...

--- Scenario 3 Results (Heavy Rain) ---
  Completed Orders: 8
  On-Time Completed: 7
  Delayed Orders: 1
  Total Penalty: $0.00
  Net Revenue: $465.19
```

**对比总结**

```
COMPARISON SUMMARY
============================================================
Metric                     Normal          Surge           Rain
------------------------------------------------------------
Completed Orders           8               15              8
On-Time Orders             8               14              7
Delayed Orders             0               1               1
Total Penalty ($)          $0.00           $0.00           $0.00
Net Revenue ($)            $339.40         $917.94         $465.19
```

***

### 5. 策略对比 (demo\_strategy\_comparison)

#### 功能说明

- 三种调度策略（收益优先、紧急度优先、综合优先级）的对比
- 结果分析与建议

#### 核心代码

```python
class RevenueFirstStrategy(Strategy):
    def name(self):
        return "Revenue First"
    
    def select_order(self, pending_orders):
        # 优先选择高金额订单
        return max(pending_orders, key=lambda o: o.amount * 0.6 + o.urgency * 10)

class UrgencyFirstStrategy(Strategy):
    def name(self):
        return "Urgency First"
    
    def select_order(self, pending_orders):
        # 优先选择高紧急度订单
        return max(pending_orders, key=lambda o: o.urgency * 20 + o.amount * 0.1)

class BalancedStrategy(Strategy):
    def name(self):
        return "Balanced Priority"
    
    def select_order(self, pending_orders):
        # 综合考虑金额、紧急度、等待时间
        return max(pending_orders, key=lambda o: o.calculate_priority(time.time()))
```

#### 输出结果

```
Simulation Setup:
  Duration: 200 min
  Orders: 30
  Time limit range: 20-50 min
  Couriers: 5

Revenue First:
  Completed Orders: 30
  On-Time Completed: 28
  Delayed Orders: 2
  Total Penalty: $15.60
  Net Revenue: $1845.30

Urgency First:
  Completed Orders: 30
  On-Time Completed: 29
  Delayed Orders: 1
  Total Penalty: $8.20
  Net Revenue: $1789.10

Balanced Priority:
  Completed Orders: 30
  On-Time Completed: 29
  Delayed Orders: 1
  Total Penalty: $5.40
  Net Revenue: $1812.60
```

***

### 6. 磁盘索引演示 (demo\_disk\_index)

#### 功能说明

- B树索引的使用示例
- 范围查询功能展示

#### 核心代码

```python
class OrderIndex:
    def __init__(self, order_file="orders.dat"):
        self.order_file = order_file
        self.by_id = {}  # 内存哈希索引
        self.by_amount = BTree(order_file + ".idx.amount")  # 金额索引
        self.by_urgency = BTree(order_file + ".idx.urgency")  # 紧急度索引
        self.by_time = BTree(order_file + ".idx.time")  # 时间索引
    
    def range_query_amount(self, min_amount, max_amount):
        order_ids = self.by_amount.range_query(min_amount, max_amount)
        return [self.by_id[oid] for oid in order_ids if oid in self.by_id]
```

#### 输出结果

```
Inserting 10 test orders...
Total orders in index: 10

Range query by amount (40-70):
  Order 3: amount=$50.0, urgency=3
  Order 4: amount=$60.0, urgency=4
  Order 5: amount=$70.0, urgency=5

Range query by urgency (6-10):
  Order 6: amount=$80.0, urgency=6
  Order 7: amount=$90.0, urgency=7
  Order 8: amount=$100.0, urgency=8
```

## 使用方法

### 运行完整演示

```bash
python main.py
```

### 清理数据文件

```bash
python cleanup_all.py
```

## 算法复杂度总结

| 模块                  | 功能           | 时间复杂度                      | 空间复杂度    |
| ------------------- | ------------ | -------------------------- | -------- |
| city\_network.py    | Dijkstra最短路径 | O((V + E) log V)           | O(V + E) |
| order\_index.py     | B树操作         | O(log\_t N)                | O(N)     |
| order\_index.py     | 范围查询         | O(K + log\_t N)            | O(K)     |
| dispatch\_system.py | Top K订单查询    | O(N log N)                 | O(K)     |
| simulation.py       | 事件仿真         | O(E log E)                 | O(E)     |
| simulation.py       | 策略分配         | O(P \* C \* (V + E) log V) | O(P + C) |

<br />

