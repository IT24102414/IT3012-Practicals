def get_percept(self) -> dict:
    ahead_pos = self._get_ahead_position()
    return {
        "wall_ahead": ahead_pos in self.walls,
        "food_here": tuple(self.agent_pos) in self.food_positions,
        "food_ahead": ahead_pos in self.food_positions,
        "toxin_here": tuple(self.agent_pos) in self.toxic_traps,
        "smells_toxin": tuple(self.agent_pos) in self.toxic_traps,
        "collision": self.collision,
        "score": self.score,
        "remaining_food": len(self.food_positions),

        # 🌍 New global state keys
        "grid_size": (self.width, self.height),
        "walls": list(self.walls),
        "all_food": list(self.food_positions),
    }
