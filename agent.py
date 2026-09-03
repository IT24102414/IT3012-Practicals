import random
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept['agent_pos']
        return random.choice(self.actions_pool)


class SearchAgent:
    """Agent that uses BFS, DFS, or UCS to plan paths to food."""

    def __init__(self):
        self.plan = []              # Step 1.3 requirement
        self.active_algo = 'BFS'    # Default algorithm

    # --- BFS ---
    def bfs_search(self, start, goal, walls, grid_size):
        frontier = deque([(start, [])])  # (state, path)
        reached = set([start])

        while frontier:
            state, path = frontier.popleft()
            if state == goal:
                return path

            for next_state, action in self._expand(state, walls, grid_size):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
        return []

    # --- DFS ---
    def dfs_search(self, start, goal, walls, grid_size):
        frontier = [(start, [])]  # stack
        reached = set([start])

        while frontier:
            state, path = frontier.pop()
            if state == goal:
                return path

            for next_state, action in self._expand(state, walls, grid_size):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
        return []

    # --- UCS ---
    def ucs_search(self, start, goal, walls, grid_size):
        frontier = [(0, start, [])]  # (cost, state, path)
        reached = {start: 0}

        while frontier:
            cost, state, path = heapq.heappop(frontier)
            if state == goal:
                return path

            for next_state, action in self._expand(state, walls, grid_size):
                new_cost = cost + 1
                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost
                    heapq.heappush(frontier, (new_cost, next_state, path + [action]))
        return []

    # --- Helper: Expand neighbors ---
    def _expand(self, state, walls, grid_size):
        x, y = state
        width, height = grid_size
        moves = {
            "Up": (x, y + 1),
            "Down": (x, y - 1),
            "Left": (x - 1, y),
            "Right": (x + 1, y),
        }
        successors = []
        for action, (nx, ny) in moves.items():
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                successors.append(((nx, ny), action))
        return successors

    # --- Main decision loop ---
    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            start = tuple(percept['agent_position'])
            foods = percept['all_food']
            walls = set(percept['walls'])
            grid_size = percept['grid_size']

            if foods:
                # Pick closest food (Manhattan distance)
                goal = min(foods, key=lambda f: abs(f[0]-start[0]) + abs(f[1]-start[1]))

                if self.active_algo == 'BFS':
                    self.plan = self.bfs_search(start, goal, walls, grid_size)
                elif self.active_algo == 'DFS':
                    self.plan = self.dfs_search(start, goal, walls, grid_size)
                elif self.active_algo == 'UCS':
                    self.plan = self.ucs_search(start, goal, walls, grid_size)

        if self.plan:
            return self.plan.pop(0)
        return "Stay"
