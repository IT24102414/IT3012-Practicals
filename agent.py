from collections import deque
import heapq
from logic_engine import KnowledgeBase


class SimpleReflexAgent:
    """Simple Reflex Agent: uses only the current percept."""
    def sense_and_act(self, percept: dict) -> str:
        if percept["food_here"]:
            return "suck"
        if percept["wall_ahead"]:
            return "turn_left"
        return "move_forward"


class ModelBasedAgent:
    """Model-Based Agent with internal memory."""
    DIRECTIONS = ["Up", "Right", "Down", "Left"]
    DIRECTION_VECTORS = {"Up": (0, 1), "Right": (1, 0), "Down": (0, -1), "Left": (-1, 0)}

    def __init__(self):
        self.position = (0, 0)
        self.direction = "Up"
        self.visited_cells = set()
        self.blocked_cells = set()
        self.percept_history = []
        self.last_action = None
        self.last_percept = None

    def reset(self):
        self.position = (0, 0)
        self.direction = "Up"
        self.visited_cells.clear()
        self.blocked_cells.clear()
        self.percept_history.clear()
        self.last_action = None
        self.last_percept = None

    def get_next_cell(self, direction):
        x, y = self.position
        dx, dy = self.DIRECTION_VECTORS[direction]
        return x + dx, y + dy

    def get_left_direction(self):
        i = self.DIRECTIONS.index(self.direction)
        return self.DIRECTIONS[(i - 1) % 4]

    def get_right_direction(self):
        i = self.DIRECTIONS.index(self.direction)
        return self.DIRECTIONS[(i + 1) % 4]

    def update_internal_state(self):
        if self.last_action == "turn_left":
            self.direction = self.get_left_direction()
        elif self.last_action == "turn_right":
            self.direction = self.get_right_direction()
        elif self.last_action == "move_forward" and self.last_percept is not None and not self.last_percept["wall_ahead"]:
            self.position = self.get_next_cell(self.direction)

    def select_action(self, percept):
        if percept["food_here"]:
            return "suck"

        forward = self.get_next_cell(self.direction)
        left = self.get_next_cell(self.get_left_direction())
        right = self.get_next_cell(self.get_right_direction())

        if not percept["wall_ahead"] and forward not in self.visited_cells and forward not in self.blocked_cells:
            return "move_forward"
        if percept["wall_ahead"] and left in self.visited_cells and right not in self.blocked_cells:
            return "turn_right"
        if left not in self.visited_cells and left not in self.blocked_cells:
            return "turn_left"
        if right not in self.visited_cells and right not in self.blocked_cells:
            return "turn_right"
        if not percept["wall_ahead"] and forward not in self.blocked_cells:
            return "move_forward"
        if left not in self.blocked_cells:
            return "turn_left"
        return "turn_right"

    def sense_and_act(self, percept: dict) -> str:
        self.update_internal_state()
        self.visited_cells.add(self.position)
        forward = self.get_next_cell(self.direction)
        if percept["wall_ahead"]:
            self.blocked_cells.add(forward)
        self.percept_history.append({
            "position": self.position,
            "direction": self.direction,
            "percept": percept.copy(),
            "last_action": self.last_action,
        })
        action = self.select_action(percept)
        self.last_action = action
        self.last_percept = percept.copy()
        return action


class SearchAgent:
    """BFS and A* search with Practical 05 Knowledge Base feasibility checking."""
    DIRECTIONS = [
        ("Up", (0, 1)), ("Right", (1, 0)),
        ("Down", (0, -1)), ("Left", (-1, 0))
    ]

    def __init__(self):
        self.kb = KnowledgeBase()
        self.kb.tell_rule(["TargetVisible", "HasDust"], "SafeToEngage")
        self.kb.tell_rule(["SafeToEngage", "BloodseekerMissing"], "Retreat")
        self.infeasible_tiles = set()

    @staticmethod
    def get_neighbors(position, walls, grid_size):
        x, y = position
        width, height = grid_size
        walls = {tuple(w) for w in walls}
        result = []
        for action, (dx, dy) in SearchAgent.DIRECTIONS:
            p = (x + dx, y + dy)
            if 0 <= p[0] < width and 0 <= p[1] < height and p not in walls:
                result.append((p, action))
        return result

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        start_pos, goal_pos = tuple(start_pos), tuple(goal_pos)
        walls = {tuple(w) for w in walls}
        if start_pos in walls or goal_pos in walls:
            return None
        queue = deque([(start_pos, [])])
        visited = {start_pos}
        while queue:
            current, path = queue.popleft()
            if current == goal_pos:
                return path
            for neighbor, action in self.get_neighbors(current, walls, grid_size):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [action]))
        return None

    @staticmethod
    def heuristic(position, goal):
        return abs(position[0] - goal[0]) + abs(position[1] - goal[1])

    def is_tile_feasible(self, tile, tile_percepts=None):
        """Infer safety for one tile. Retreat means the tile is infeasible."""
        tile = tuple(tile)
        percepts = (tile_percepts or {}).get(tile, {})
        self.kb.clear_facts()
        for fact, value in percepts.items():
            if value:
                self.kb.tell_fact(fact)
        self.kb.forward_chain()
        if "Retreat" in self.kb.facts:
            self.infeasible_tiles.add(tile)
            return False
        return True

    def a_star_search(self, start_pos, goal_pos, walls, grid_size, tile_percepts=None):
        """A* checks the KB before adding every neighbor to open_list."""
        start_pos, goal_pos = tuple(start_pos), tuple(goal_pos)
        walls = {tuple(w) for w in walls}
        self.infeasible_tiles.clear()
        if start_pos in walls or goal_pos in walls:
            return None
        if not self.is_tile_feasible(start_pos, tile_percepts):
            return None

        open_list = []
        counter = 0
        heapq.heappush(open_list, (self.heuristic(start_pos, goal_pos), 0, counter, start_pos, []))
        best_g = {start_pos: 0}

        while open_list:
            _, current_g, _, current, path = heapq.heappop(open_list)
            if current == goal_pos:
                return path
            if current_g > best_g.get(current, float("inf")):
                continue

            for neighbor, action in self.get_neighbors(current, walls, grid_size):
                # Practical 05: KB check BEFORE open_list insertion.
                if not self.is_tile_feasible(neighbor, tile_percepts):
                    continue
                new_g = current_g + 1
                if new_g < best_g.get(neighbor, float("inf")):
                    best_g[neighbor] = new_g
                    counter += 1
                    f = new_g + self.heuristic(neighbor, goal_pos)
                    heapq.heappush(open_list, (f, new_g, counter, neighbor, path + [action]))
        return None
