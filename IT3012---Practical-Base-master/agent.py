# agent.py
import random
from collections import deque


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    """A simple reflex agent that reacts only to the current percept."""

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'Up'
        if percept.get('wall_ahead'):
            return random.choice(['Left', 'Right', 'Down', 'Up'])
        return 'Up'


class ModelBasedAgent:
    """A model-based agent that uses internal state to avoid repeating failed actions."""

    def __init__(self):
        self.last_percept = None
        self.last_action = None
        self.actions = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        action = None

        if self.last_percept == percept and self.last_action is not None:
            if percept.get('wall_ahead'):
                action = next(
                    a for a in self.actions if a != self.last_action
                )
            elif percept.get('food_here'):
                action = 'Right' if self.last_action == 'Up' else 'Up'
            else:
                action = 'Right' if self.last_action != 'Right' else 'Left'
        else:
            if percept.get('food_here'):
                action = 'Up'
            elif percept.get('wall_ahead'):
                action = 'Left'
            else:
                action = 'Up'

        self.last_percept = percept.copy()
        self.last_action = action
        return action


class SearchAgent:
    """A search agent that can solve grid pathfinding problems with BFS."""

    MOVE_DELTAS = {
        'Up': (0, 1),
        'Down': (0, -1),
        'Left': (-1, 0),
        'Right': (1, 0),
    }

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        width, height = grid_size
        walls = set(walls)
        frontier = deque([(start_pos, [])])
        visited = {start_pos}

        while frontier:
            current_pos, path = frontier.popleft()
            if current_pos == goal_pos:
                return path

            for action, delta in self.MOVE_DELTAS.items():
                next_pos = (current_pos[0] + delta[0], current_pos[1] + delta[1])
                if (
                    0 <= next_pos[0] < width
                    and 0 <= next_pos[1] < height
                    and next_pos not in walls
                    and next_pos not in visited
                ):
                    visited.add(next_pos)
                    frontier.append((next_pos, path + [action]))

        return None