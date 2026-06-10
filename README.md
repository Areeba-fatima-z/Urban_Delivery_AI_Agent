# Intelligent Urban Delivery Robot

A Python-based AI pathfinding project that simulates an autonomous delivery robot navigating a dynamically generated urban grid. Five search algorithms are benchmarked side-by-side across cost, nodes explored, and execution time — with full matplotlib visualization.

---

##  Project Overview

The robot starts at a **base station (0, 0)** on a randomly generated **15×15 city grid** and must complete **5 deliveries** to different locations. The grid contains roads, traffic zones, and blocked buildings — each with different traversal costs.

The simulation runs all five algorithms on the **same grid and delivery points**, making the comparison fair and meaningful.

---

##  Grid Structure

| Cell Type    | Symbol | Cost        | Color  |
|--------------|--------|-------------|--------|
| Road         | —      | 1 – 5       | Grey   |
| Building     | X      | ∞ (blocked) | Black  |
| Traffic Zone | T      | 10 – 20     | Red    |
| Base Station | B      | 0           | Blue   |
| Delivery Point | D    | 1           | Green  |

- Grid size: **15 × 15**
- Buildings: **30** (impassable)
- Traffic zones: **25** (high cost)
- Delivery points: **5**

---

##  Algorithms Implemented

| Algorithm | Type | Heuristic | Optimal? |
|-----------|------|-----------|----------|
| **BFS** | Uninformed | None | Yes (unweighted) |
| **DFS** | Uninformed | None | Not |
| **UCS** | Uninformed | None | Yes (weighted) |
| **GBFS** | Informed | Manhattan / Euclidean | Not |
| **A\*** | Informed | Manhattan / Euclidean | Yes |

For **GBFS** and **A\***, the user selects the heuristic at runtime:
- `1` -> Manhattan Distance: `|r1 - r2| + |c1 - c2|`
- `2` -> Euclidean Distance: `√((r1-r2)² + (c1-c2)²)`

---

##  How to Run

### Prerequisites

```bash
pip install matplotlib numpy
```

### Run the script

```bash
python Ai_Project_Task1.py
```

### On startup, you will be prompted to:

```
Choose heuristic for GBFS 1 or 2 : 
Choose heuristic for A*  1 or 2 : 
```

Enter `1` for Manhattan or `2` for Euclidean.

---

##  Output

### Console Output

After all algorithms finish, a summary table is printed:

```
Algorithm     Cost    Nodes         Time
------------------------------------------
BFS            87      210    0.002100s
DFS           143      198    0.001800s
UCS            62      310    0.003200s
GBFS(Man)      71      145    0.001200s
A*(Man)        62      178    0.002000s

Best Cost  : UCS  (cost  = 62)
Best Nodes : GBFS (nodes = 145)
Best Speed : GBFS (time  = 0.001200s)
```

### Visualization (matplotlib)

A large figure is displayed with:

- **5 grid subplots** (one per algorithm) — each showing the robot's 5 delivery paths in distinct colors (purple, blue, teal, orange, dark red)
- **3 bar charts** comparing all algorithms on:
  - Total Traversal Cost (Path Optimality)
  - Total Nodes Explored (Search Efficiency)
  - Total Execution Time (Speed)
- **Legend panel** for grid elements and delivery path colors

---

##  Metrics Tracked Per Algorithm

| Metric | Description |
|--------|-------------|
| **Total Cost** | Sum of cell traversal costs across all 5 deliveries |
| **Total Nodes Explored** | Total nodes popped/visited during all 5 searches |
| **Total Execution Time** | Wall-clock time in seconds for all 5 searches |

---

##  Key Design Decisions

- Each algorithm uses the **same randomly generated grid** for a fair comparison.
- The robot travels **sequentially** — after each delivery, it starts from the previous delivery point (not back to base).
- Buildings act as **hard obstacles** — never traversable.
- Traffic zones are **passable but expensive**, testing cost-aware algorithms.
- A\* with Manhattan heuristic is expected to perform best overall on this grid type.

---

## Concepts Covered

- Uninformed search: BFS, DFS, UCS
- Informed search: Greedy Best-First Search, A*
- Heuristic functions: Manhattan, Euclidean
- Grid-based pathfinding with weighted cells
- Algorithm benchmarking and visualization

---

##  Author

**Areeba**  
AI / Computer Science Project — Module 1
