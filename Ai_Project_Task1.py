#========================================================================================
#                                    Module 1
#                      Intelligent Urban Delivery Robot
# When we run the Project first it asks what heuristic we want to choose for GBFS abd A*
# search. 
# Then it runs all the searches on 5 grids that are same 
# In Each Search robot copletes 5 deliveries that are on same spots for all searches.
# On base of that their costs , total nodes explored and time of execution is calculted
# Then these things are used to compare each algorithm
# At the end when all algorithms are executed successfully it gives the best one that 
# has best or lowest cost , time of execution and nodes explored for that grid
# On visulaized Figure we can see 5 grids for all 5 searches that has done their 5 deliveries
# with colored path (Each delivery is shown with seperate colored path).
# 3 Bar charts represents the time of execution , Total costs of all deliveries and total
# nodes explored by each algorithm.
#==============================================================================================
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
import heapq
from collections import deque
import math
import time

ROWS = 15       # no of rows
COLS = 15       # no of cols
NUM_BUILDINGS = 30   # no of blocked cells
NUM_TRAFFIC   = 25   # no of traffic cells
NUM_DELIVERIES = 5   # no of delivery places

# colors dictionary for grid
COLOR_MAP = {
    "road":     [0.91, 0.90, 0.87],   # grey
    "building": [0.17, 0.17, 0.16],   # black
    "traffic":  [0.97, 0.76, 0.76],   # red
    "base":     [0.71, 0.83, 0.96],   # blue
    "delivery": [0.75, 0.87, 0.59],   # green
}

# This function make a cell which is actually a dictionary
# For this project I have stored a cell as an dictionary 1 cell = 1 dictionary
def make_cell(row, col, cell_type="road", cost=1):

    cell = {
        "row":  row,
        "col":  col,
        "type": cell_type,
        "cost": cost
    }
    return cell

# This function builds a 15 x 15 grid
# The grid is a nested list (list of lists)
#==========================================================================
# road cost = 1 to 5
# buldings cost = infinity
# traffic cost = 10 to 20
# delivery point cost = 1
#==========================================================================

def create_grid():

    # first fill every cell as a road first
    grid = []

    for r in range(ROWS):

        row = []

        for c in range(COLS):
            cost = random.randint(1, 5)   # normal road cost is between 1 to 5
            cell = make_cell(r, c, "road", cost)
            row.append(cell)     # add cell to this row

        grid.append(row)         # add completed row to grid

    # mark the starting position / base

    grid[0][0]["type"] = "base"   # This is a base from where robot will start
    grid[0][0]["cost"] = 0        # no cost at starting point

    # mark occupied positions so they can not be overwritten with anything else

    occupied = set()
    occupied.add((0, 0))    # mark base position as taken

    # Placing buildings on grid
    placed = 0

    while placed < NUM_BUILDINGS:

        r = random.randint(0, 14)
        c = random.randint(0, 14)

        if (r, c) not in occupied:    # only place if that spot is free
            grid[r][c]["type"] = "building"
            grid[r][c]["cost"] = float('inf')   # In infinity cost robot can never enter
            occupied.add((r, c))
            placed += 1

    # Placing Traffic zones means their cost will be high

    placed = 0

    while placed < NUM_TRAFFIC:

        r = random.randint(0, 14)
        c = random.randint(0, 14)

        if (r, c) not in occupied:
            grid[r][c]["type"] = "traffic"
            grid[r][c]["cost"] = random.randint(10, 20)  # cost can be between 10 to 20
            occupied.add((r, c))
            placed += 1

    # Placing delivery points

    deliveries = []
    placed = 0

    while placed < NUM_DELIVERIES:

        r = random.randint(0, 14)
        c = random.randint(0, 14)

        if (r, c) not in occupied:
            grid[r][c]["type"] = "delivery"
            grid[r][c]["cost"] = 1          # cheap to enter delivery point
            occupied.add((r, c))
            deliveries.append((r, c))       # save this position
            placed += 1

    return grid, (0, 0), deliveries
# This Function visulaizes the grid

def visualize_grid(grid, deliveries, title="City Grid"):

    # numpy lets us create a 15x15 grid of RGB colors
    # shape (15, 15, 3) means: 15 rows, 15 cols, 3 color values each

    image = np.zeros((ROWS, COLS, 3))   # start with all black

    for r in range(ROWS):
        for c in range(COLS):
            cell_type = grid[r][c]["type"]       # get the type of this cell
            image[r][c] = COLOR_MAP[cell_type]   # assign its color

    fig, ax = plt.subplots(figsize=(8, 8))
    # fig = the whole window
    # ax  = the drawing area inside the window
    # figsize=(8,8) = 8 inches wide, 8 inches tall

    ax.imshow(image, interpolation='nearest')
    # imshow draws the numpy color array as an image
    # 'nearest' means no blurring between cells — sharp edges

    # Draw grid lines
    # These are the thin lines separating each cell

    for x in range(COLS + 1):                       # vertical lines
        ax.axvline(x - 0.5, color='gray', linewidth=0.4)

    for y in range(ROWS + 1):                       # horizontal lines
        ax.axhline(y - 0.5, color='gray', linewidth=0.4)

    # axvline draws a vertical line at position x
    # axhline draws a horizontal line at position y
    # We use x-0.5 because cell centers are at whole numbers,
    # so borders fall between them (at 0.5, 1.5, 2.5, ...)

    # symbols dictionary
    symbols = {
        "road":     "",
        "building": "X",
        "traffic":  "T",
        "base":     "B",
        "delivery": "D"
    }

    # text colors for each type
    text_colors = {
        "building": "#aaaaaa",   # gray
        "traffic":  "#A32D2D",   # red
        "base":     "#0C447C",   # blue
        "delivery": "#27500A",   # green
    }

    for r in range(ROWS):
        for c in range(COLS):
            cell_type = grid[r][c]["type"]
            label = symbols.get(cell_type, "")   # get label, "" if not found

            if label != "":      # only draw if there is a label
                color = text_colors.get(cell_type, "black")
                ax.text(
                    c, r,            # x position = col, y position = row
                    label,           # the text to show
                    ha='center',     # horizontal alignment: center
                    va='center',     # vertical alignment: center
                    fontsize=7,
                    fontweight='bold',
                    color=color
                )

    patches = [
        mpatches.Patch(color=COLOR_MAP["road"],     label="Road (cost 1-5)"),
        mpatches.Patch(color=COLOR_MAP["building"], label="Building (Blocked path)"),
        mpatches.Patch(color=COLOR_MAP["traffic"],  label="Traffic (cost 10-20)"),
        mpatches.Patch(color=COLOR_MAP["base"],     label="Base Station (B)"),
        mpatches.Patch(color=COLOR_MAP["delivery"], label="Delivery Point (D)"),
    ]

    ax.legend(
        handles=patches,
        loc='lower center',
        bbox_to_anchor=(0.5, -0.08),  # legend neeche, grid ke bahar
        ncol=3,                        # 3 columns mein show karo
        fontsize=9,
        framealpha=0.9
    )

    ax.set_title(title, fontsize=13, pad=10)

    # Show row and column numbers on the axes
    ax.set_xticks(range(COLS))
    ax.set_yticks(range(ROWS))
    ax.set_xticklabels(range(COLS), fontsize=7)
    ax.set_yticklabels(range(ROWS), fontsize=7)

    plt.tight_layout()    # auto-adjust spacing so nothing gets cut off
    plt.show()            # open the window and display the grid

# Finds valid neighbours on left right up and down
def get_neighbors(grid, row, col):

    directions = [(-1, 0),   # up (row -1)
                  ( 1, 0),   # down(row +1)
                  ( 0,-1),   # left (col -1)
                  ( 0, 1)]   # right(col +1)

    neighbors = []

    for dr, dc in directions:
        new_r = row + dr    # new row
        new_c = col + dc    # new col

        # check if calculted neighbour is in grid
        if 0 <= new_r < ROWS and 0 <= new_c < COLS:

            # check if the neighbour is building or not and then add to neighbour
            if grid[new_r][new_c]["type"] != "building":
                neighbors.append((new_r, new_c))

    return neighbors

# ============================================================
# BFS (Breadth First Search)
# How it works :
# Queue mein start daalo
# Level by level explore karo (pehle sab neighbors,phir unke neighbors, aur aage)
# Jab goal mile, ruk jao
# Weakness: Cost ignore karta hai — traffic aur road same samajhta hai
# ============================================================

def bfs(grid, start, goal):
    nodes_explored = 0
    start_time = time.time()

    queue = deque()
    queue.append(start)

    visited = set()
    visited.add(start)

    # {child_position : parent_position}
    parent = {}
    parent[start] = None

    while queue:
        current = queue.popleft()
        nodes_explored += 1

        if current == goal:
            break

        for neighbor in get_neighbors(grid, current[0], current[1]):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = parent.get(current)

    path.reverse()

    total_cost = 0
    for pos in path:
        total_cost += grid[pos[0]][pos[1]]["cost"]

    end_time = time.time()
    exec_time = round(end_time - start_time, 6)

    return path, total_cost, nodes_explored, exec_time

# ============================================================
# DFS Depth First Search
# Kaise kaam karta hai:
# Stack mein start daalo
# Ek direction mein jitna ho sake deep jao
# Jab goal mile, ruk jao
# Weakness: Can give expensive and long path
# ============================================================

def dfs(grid, start, goal):

    nodes_explored = 0
    start_time = time.time()

    stack = deque()
    stack.append(start)

    visited = set()
    visited.add(start)

    parent = {}
    parent[start] = None

    while stack:
        current = stack.pop()
        nodes_explored += 1

        if current == goal:
            break

        for neighbor in get_neighbors(grid, current[0], current[1]):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()

    total_cost = 0
    for pos in path:
        total_cost += grid[pos[0]][pos[1]]["cost"]

    end_time = time.time()
    exec_time = round(end_time - start_time, 6)

    return path, total_cost, nodes_explored, exec_time


# ============================================================
# UCS Uniform Cost Search
# Kaise kaam karta hai:
# Priority Queue use karta hai
# Hamesha lowest path pehle explore karta hai
# It uses Priority Queue:
# (total_cost_so_far, position, path_so_far)
# ============================================================

def ucs(grid, start, goal):

    nodes_explored = 0
    start_time = time.time()

    priority_queue = []
    heapq.heappush(priority_queue, (0, start, [start]))

    visited = set()

    while priority_queue:
        cost, current, path = heapq.heappop(priority_queue)
        nodes_explored += 1

        if current == goal:
            end_time = time.time()
            exec_time = round(end_time - start_time, 6)
            return path, cost, nodes_explored, exec_time

        if current in visited:
            continue
        visited.add(current)

        for neighbor in get_neighbors(grid, current[0], current[1]):
            if neighbor not in visited:
                neighbor_cost = grid[neighbor[0]][neighbor[1]]["cost"]
                new_cost = cost + neighbor_cost

                heapq.heappush(priority_queue,
                               (new_cost, neighbor, path + [neighbor]))

    return [], float('inf'), nodes_explored, 0

# manathan = |x1 - x2| +|y1 - y2|
def manhattan(pos1, pos2):
    # pos1 aur pos2 dono (row, col) tuples hain
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# Eucilidian = sqrt( (r1-r2)^2 + (c1-c2)^2 )
def euclidean(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

# ============================================================
# GBFS Greedy Best First Search
# Kaise kaam karta hai:
# Sirf heuristic checkk krta hai
# It is fast but not optimal
# heuristic type = "manhattan" or "euclidean"
# ============================================================

def gbfs(grid, start, goal, heuristic_type="manhattan"):

    nodes_explored = 0
    start_time = time.time()

    if heuristic_type == "manhattan":
        h = manhattan(start, goal)
    else:
        h = euclidean(start, goal)

    priority_queue = []
    heapq.heappush(priority_queue, (h, start, [start]))

    visited = set()

    while priority_queue:
        h_val, current, path = heapq.heappop(priority_queue)
        nodes_explored += 1

        if current == goal:
            total_cost = 0
            for pos in path:
                total_cost += grid[pos[0]][pos[1]]["cost"]

            end_time = time.time()
            exec_time = round(end_time - start_time, 6)
            return path, total_cost, nodes_explored, exec_time

        if current in visited:
            continue
        visited.add(current)

        for neighbor in get_neighbors(grid, current[0], current[1]):
            if neighbor not in visited:

                if heuristic_type == "manhattan":
                    h_neighbor = manhattan(neighbor, goal)
                else:
                    h_neighbor = euclidean(neighbor, goal)

                heapq.heappush(priority_queue,
                               (h_neighbor, neighbor, path + [neighbor]))

    return [], float('inf'), nodes_explored, 0


# ============================================================
# A* Search
# f(n) = g(n) + h(n)
# g(n) = actual cost so far
# h(n) = estimated cost to goal (heuristic)
# ============================================================

def a_star(grid, start, goal, heuristic_type="manhattan"):

    nodes_explored = 0
    start_time = time.time()

    if heuristic_type == "manhattan":
        h_start = manhattan(start, goal)
    else:
        h_start = euclidean(start, goal)

    priority_queue = []
    heapq.heappush(priority_queue, (h_start, 0, start, [start]))

    visited = set()

    while priority_queue:
        f_cost, g_cost, current, path = heapq.heappop(priority_queue)
        nodes_explored += 1

        if current == goal:
            end_time = time.time()
            exec_time = round(end_time - start_time, 6)
            return path, g_cost, nodes_explored, exec_time

        if current in visited:
            continue
        visited.add(current)

        for neighbor in get_neighbors(grid, current[0], current[1]):
            if neighbor not in visited:
                neighbor_cost = grid[neighbor[0]][neighbor[1]]["cost"]
                new_g = g_cost + neighbor_cost

                if heuristic_type == "manhattan":
                    h_n = manhattan(neighbor, goal)
                else:
                    h_n = euclidean(neighbor, goal)

                new_f = new_g + h_n

                heapq.heappush(priority_queue,
                               (new_f, new_g, neighbor, path + [neighbor]))

    return [], float('inf'), nodes_explored, 0


# It makes a dictionary of robot
def make_robot(start_position):
    robot = {
        "current_pos" : start_position,  # abhi kahan hai
        "completed"   : [],               # kon si deliveries ho gayi
        "total_cost"  : 0,                # abhi tak kitna cost hua
        "total_nodes" : 0,                # abhi tak kitne nodes explore hue
        "total_time"  : 0.0,              # abhi tak kitna time laga
        "all_paths"   : []                # har delivery ka path save karo
    }
    return robot


# for a delivery from one position to the delivery point
def do_one_delivery(robot, grid, goal, delivery_num,algo="a_star", heuristic="manhattan"):

    start = robot["current_pos"]   # current position of robot

    # choose algo
    if algo == "bfs":
        path, cost, nodes, t = bfs(grid, start, goal)
    elif algo == "dfs":
        path, cost, nodes, t = dfs(grid, start, goal)
    elif algo == "ucs":
        path, cost, nodes, t = ucs(grid, start, goal)
    elif algo == "gbfs":
        path, cost, nodes, t = gbfs(grid, start, goal, heuristic)
    else:                           # default: A*
        path, cost, nodes, t = a_star(grid, start, goal, heuristic)

    # if path not found
    if not path or len(path) == 0:
        return False

    # Robot update karo
    robot["current_pos"] = goal          # robot goal pe pohonch gaya
    robot["completed"].append(goal)      # yeh delivery complete
    robot["total_cost"]  += cost         # total cost mein add karo
    robot["total_nodes"] += nodes        # total nodes mein add karo
    robot["total_time"]  += t            # total time mein add karo
    robot["all_paths"].append({          # is delivery ki info save karo
        "delivery_num" : delivery_num,
        "start"        : start,
        "goal"         : goal,
        "path"         : path,
        "cost"         : cost,
        "nodes"        : nodes,
        "time"         : t
    })

    return True



# sumilation of robot for one algorithm
def run_simulation(grid, base, deliveries, algo="a_star", heuristic="manhattan"):
    robot = make_robot(base)

    for i, goal in enumerate(deliveries):
        do_one_delivery(robot, grid, goal, i + 1,algo, heuristic)

    return robot


# ============================================================
# MAIN VISUALIZATION
# Har algorithm ka apna subplot
# legend and 3 bar charts (cost, nodes, time)
# 5 delivery paths ke liye 5 alag colors:
# D1 = purple, D2 = blue, D3 = teal, D4 = orange, D5 = dark red
# ============================================================

def visualize_all_simulations(all_robots, grid, base, deliveries, algo_names):

    # 5 delivery paths ke liye 5 alag colors
    path_colors = [
        [0.53, 0.12, 0.47],   # D1 - purple
        [0.13, 0.37, 0.68],   # D2 - blue
        [0.07, 0.53, 0.38],   # D3 - teal
        [0.85, 0.33, 0.10],   # D4 - orange
        [0.65, 0.16, 0.16],   # D5 - dark red
    ]

    num_algos = len(algo_names)   # 5 algorithms

# figure layout
    fig = plt.figure(figsize=(55, 42))   
    outer = gridspec.GridSpec(
        2, 1,
        figure=fig,
        height_ratios=[5.5, 2.0],
        hspace=0.25        
    )

    # Row 0: 5 algorithm grids side by side
    top_grid = gridspec.GridSpecFromSubplotSpec(
        1, num_algos,
        subplot_spec=outer[0],
        wspace=1.1         
    )

    # Row 1: 3 bar charts side by side and legend
    bot_grid = gridspec.GridSpecFromSubplotSpec(
        1, 4,
        subplot_spec=outer[1],
        wspace=0.55,
        width_ratios=[1.2, 1.2, 1.2, 0.8] 
    )
# Matrices for bar charts
    total_costs  = []
    total_nodes  = []
    total_times  = []

    # draws grid of each algorithm

    for ai, algo_name in enumerate(algo_names):

        robot = all_robots[ai]
        ax = fig.add_subplot(top_grid[ai])

        # Base image banao  grid ke colors
        image = np.zeros((ROWS, COLS, 3))
        for r in range(ROWS):
            for c in range(COLS):
                image[r][c] = COLOR_MAP[grid[r][c]["type"]]

        # Har delivery ka path draw karo
        for i, delivery_info in enumerate(robot["all_paths"]):
            path  = delivery_info["path"]
            color = path_colors[i]

            # Path cells ko us delivery ka color do
            for j, pos in enumerate(path):
                r, c = pos
                if j == 0 and i == 0:
                    # Sabse pehla start = base station
                    image[r][c] = [0.15, 0.15, 0.15]  # dark gray
                elif j == len(path) - 1:
                    # Goal cell — bright green
                    image[r][c] = [0.10, 0.65, 0.10]
                else:
                    # Beech ka path — us delivery ka color
                    image[r][c] = color

            # Path pe line draw karo (colored line connecting cells)
            if len(path) > 1:
                px = [p[1] for p in path]   # col = x axis
                py = [p[0] for p in path]   # row = y axis
                ax.plot(px, py,
                        color=color,
                        linewidth=1.8,
                        alpha=0.75,
                        zorder=3)

            # Goal cell pe delivery number likho
            gr, gc = delivery_info["goal"]
            ax.text(gc, gr,
                    f"D{delivery_info['delivery_num']}",
                    ha='center', va='center',
                    fontsize=7, fontweight='bold',
                    color='white', zorder=4)

        # Base station pe B likho
        br, bc = base
        image[br][bc] = [0.15, 0.15, 0.15]
        ax.text(bc, br, "B",
                ha='center', va='center',
                fontsize=8, fontweight='bold',
                color='white', zorder=4)

        ax.imshow(image, interpolation='nearest', zorder=1)

        # Grid lines (patli)
        for x in range(COLS + 1):
            ax.axvline(x - 0.5, color='gray', linewidth=0.25, zorder=2)
        for y in range(ROWS + 1):
            ax.axhline(y - 0.5, color='gray', linewidth=0.25, zorder=2)

        # Building aur Traffic labels
        for r in range(ROWS):
            for c in range(COLS):
                ct = grid[r][c]["type"]
                if ct == "building":
                    ax.text(c, r, "X", ha='center', va='center',
                            fontsize=5, color='#999999', zorder=2)
                elif ct == "traffic":
                    ax.text(c, r, "T", ha='center', va='center',
                            fontsize=5, color='#cc4444', zorder=2)

        # Axis ticks  har 3rd number dikhao (jagah bachane ke liye)
        ax.set_xticks(range(0, COLS, 3))
        ax.set_yticks(range(0, ROWS, 3))
        ax.tick_params(labelsize=6)

        # Title: algorithm name + total metrics for all 5 deliveries
        tc = robot["total_cost"]
        tn = robot["total_nodes"]
        tt = robot["total_time"]

        ax.set_title(
            f"{algo_name}\n"
            f"Cost:{tc}  Nodes:{tn}\nTime:{tt:.4f}s",
            fontsize=8,
            pad=10,
            linespacing=1.6
        )

        # Metrics save karo bar charts ke liye
        total_costs.append(tc)
        total_nodes.append(tn)
        total_times.append(tt)


    legend_patches = [
        mpatches.Patch(color=COLOR_MAP["road"],    label="Road"),
        mpatches.Patch(color=COLOR_MAP["building"],label="Building (X)"),
        mpatches.Patch(color=COLOR_MAP["traffic"], label="Traffic (T)"),
        mpatches.Patch(color=[0.15, 0.15, 0.15],  label="Base (B)"),
        mpatches.Patch(color=[0.10, 0.65, 0.10],  label="Delivery Goal"),
    ]

    # Har delivery ka color aur label
    for i in range(5):
        legend_patches.append(
            mpatches.Patch(color=path_colors[i],
                           label=f"D{i+1} Path")
        )

     
    ax_legend = fig.add_subplot(bot_grid[3])   
    ax_legend.axis('off')                      
    ax_legend.legend(
        handles=legend_patches,
        loc='center left',
        bbox_to_anchor=(0.0, 0.5),
        fontsize=9,
        framealpha=0.9,
        title="Legend",
        title_fontsize=10,
        borderpad=1.2
    )

    # -------------------------------------------------------
    # Bar charts
    # 1. Path Optimality: Total traversal cost
    # 2. Search Efficiency: Number of nodes explored
    # 3. Execution Time: Time required to compute the path
    # -------------------------------------------------------

    bar_colors = [
        '#378ADD',   # BFS   — blue
        '#639922',   # DFS   — green
        '#BA7517',   # UCS   — amber
        '#D85A30',   # GBFS  — coral
        '#534AB7',   # A*    — purple
    ]

    x = range(num_algos)   # 0, 1, 2, 3, 4

    # Chart 1: Path Optimality (Total Traversal Cost)
    ax1 = fig.add_subplot(bot_grid[0])
    ax1.bar(x, total_costs, color=bar_colors, width=0.5)
    ax1.set_title("Path Optimality\n(Total Traversal Cost — 5 Deliveries)", fontsize=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(algo_names, fontsize=9)
    ax1.set_ylabel("Total Cost", fontsize=9)
    # Har bar pe value likho
    for j, v in enumerate(total_costs):
        ax1.text(j, v + max(total_costs) * 0.01, str(v),
                 ha='center', fontsize=9, fontweight='bold')
    ax1.set_ylim(0, max(total_costs) * 1.15)

    #  Chart 2: Search Efficiency (Nodes Explored) 
    ax2 = fig.add_subplot(bot_grid[1])
    ax2.bar(x, total_nodes, color=bar_colors, width=0.5)
    ax2.set_title("Search Efficiency\n(Nodes Explored — 5 Deliveries)", fontsize=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(algo_names, fontsize=9)
    ax2.set_ylabel("Total Nodes Explored", fontsize=9)
    for j, v in enumerate(total_nodes):
        ax2.text(j, v + max(total_nodes) * 0.01, str(v),
                 ha='center', fontsize=9, fontweight='bold')
    ax2.set_ylim(0, max(total_nodes) * 1.15)

    # Chart 3: Execution Time 
    ax3 = fig.add_subplot(bot_grid[2])
    ax3.bar(x, total_times, color=bar_colors, width=0.5)
    ax3.set_title("Execution Time\n(Seconds — 5 Deliveries)", fontsize=10)
    ax3.set_xticks(x)
    ax3.set_xticklabels(algo_names, fontsize=9)
    ax3.set_ylabel("Total Time (seconds)", fontsize=9)
    for j, v in enumerate(total_times):
        ax3.text(j, v + max(total_times) * 0.01, f"{v:.5f}",
                 ha='center', fontsize=8, fontweight='bold')
    ax3.set_ylim(0, max(total_times) * 1.20)


    plt.show()


# ============================================================
# Main Program
# ============================================================


grid, base, deliveries = create_grid()
print("========================= Intelligent Urban Delivery Robot =================================\n")
print("BASE    :", base)
print("GOALS   :", deliveries)

print("\n" )
print("  Choose heuristic\n")
print("  1 . Manhattan Distance")
print("  2 . Euclidean Distance\n")

while True:
    choice = input("\n  Choose heuristic for GBFS 1 or 2 : ").strip()
    if choice == "1":
        gbfs_heuristic = "manhattan"
        print("  GBFS  Manhattan selected!")
        break
    elif choice == "2":
        gbfs_heuristic = "euclidean"
        print("  GBFS  Euclidean selected!")
        break
    else:
        print("  Wrong Input!")

while True:
    choice = input("\n  Choose heuristic for A* 1 or 2 : ").strip()
    if choice == "1":
        astar_heuristic = "manhattan"
        print("  A* Manhattan selected!")
        break
    elif choice == "2":
        astar_heuristic = "euclidean"
        print("  A* Euclidean selected!")
        break
    else:
        print("  Wrong Input !")

print("\n")
print(f"  GBFS Heuristic : {gbfs_heuristic.capitalize()}")
print(f"  A*   Heuristic : {astar_heuristic.capitalize()}\n")

# Algorithms ki list
algo_names = ["BFS", "DFS", "UCS",
              f"GBFS\n({gbfs_heuristic[:3].capitalize()})",
              f"A*\n({astar_heuristic[:3].capitalize()})"]
algo_keys  = ["bfs", "dfs", "ucs", "gbfs", "a_star"]

# Har algorithm ki simulation chalao aur results store karo
all_robots = []

for i, algo_key in enumerate(algo_keys):
    print(f"\nRunning {algo_names[i].replace(chr(10), ' ')}...")

    # GBFS aur A* ko user ka chosen heuristic pass karo
    if algo_key == "gbfs":
        robot = run_simulation(grid, base, deliveries,
                               algo=algo_key,
                               heuristic=gbfs_heuristic)
    elif algo_key == "a_star":
        robot = run_simulation(grid, base, deliveries,
                               algo=algo_key,
                               heuristic=astar_heuristic)
    else:
        robot = run_simulation(grid, base, deliveries,
                               algo=algo_key)

    all_robots.append(robot)
    print(f"  Done Cost:{robot['total_cost']}  "
          f"Nodes:{robot['total_nodes']}  "
          f"Time:{robot['total_time']:.6f}s")

# Console mein results table print karo
print(f"\n{'Algorithm':<10} {'Cost':>8} {'Nodes':>8} {'Time':>12}")
print("-" * 42)
for i, name in enumerate(algo_names):
    r = all_robots[i]
    print(f"{name:<10} {r['total_cost']:>8} "
          f"{r['total_nodes']:>8} "
          f"{r['total_time']:>11.6f}s")

# Best algorithm kaun sa hai
best_cost  = min(range(len(algo_names)), key=lambda i: all_robots[i]["total_cost"])
best_nodes = min(range(len(algo_names)), key=lambda i: all_robots[i]["total_nodes"])
best_time  = min(range(len(algo_names)), key=lambda i: all_robots[i]["total_time"])

print(f"\nBest Cost   : {algo_names[best_cost]}  (cost  = {all_robots[best_cost]['total_cost']})")
print(f"Best Nodes  : {algo_names[best_nodes]}  (nodes = {all_robots[best_nodes]['total_nodes']})")
print(f"Best Speed  : {algo_names[best_time]}  (time  = {all_robots[best_time]['total_time']:.6f}s)")

# Visualization 
visualize_all_simulations(all_robots, grid, base, deliveries, algo_names)
