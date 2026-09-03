# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with configurable opponents."""

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=2,
        custom_walls=None,
    ):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Generate food while avoiding walls and the starting position.
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            position = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1),
            )

            if position != (0, 0) and position not in self.walls:
                self.food_positions.add(position)

        # Generate toxic traps while avoiding the start, walls, and food.
        self.toxic_traps = set()

        while len(self.toxic_traps) < 5:
            trap_position = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1),
            )

            if (
                trap_position != (0, 0)
                and trap_position not in self.walls
                and trap_position not in self.food_positions
            ):
                self.toxic_traps.add(trap_position)

        # Generate opponents while avoiding occupied cells.
        self.opponents = []

        while len(self.opponents) < num_opponents:
            opponent_position = [
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1),
            ]
            opponent_tuple = tuple(opponent_position)

            if (
                opponent_tuple != (0, 0)
                and opponent_tuple not in self.walls
                and opponent_tuple not in self.food_positions
                and opponent_tuple not in self.toxic_traps
                and opponent_position not in self.opponents
            ):
                self.opponents.append(opponent_position)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        return {
            "agent_pos": list(self.agent_pos),
            "opponent_positions": [list(op) for op in self.opponents],
            "smells_food": tuple(self.agent_pos) in self.food_positions,
            "hit_wall": tuple(self.agent_pos) in self.walls,
            "smells_toxin": tuple(self.agent_pos) in self.toxic_traps,
            "collision": self.collision,
            "score": self.score,
            "remaining_food": len(self.food_positions),
        }

    def execute_action(self, action: str):
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == "Up":
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == "Down":
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == "Left":
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == "Right":
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        # Wall collision or valid movement.
        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        # Check the updated agent position.
        tuple_pos = tuple(self.agent_pos)

        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        if tuple_pos in self.toxic_traps:
            self.score -= 15

        # Detect an immediate collision before opponents move.
        if any(op == self.agent_pos for op in self.opponents):
            self.score -= 50
            self.collision = True
            return

        # Move opponents without allowing them to enter walls.
        for op in self.opponents:
            move = random.choice(["Up", "Down", "Left", "Right", "Stay"])
            opponent_new_pos = list(op)

            if move == "Up":
                opponent_new_pos[1] = min(
                    self.height - 1,
                    opponent_new_pos[1] + 1,
                )
            elif move == "Down":
                opponent_new_pos[1] = max(0, opponent_new_pos[1] - 1)
            elif move == "Left":
                opponent_new_pos[0] = max(0, opponent_new_pos[0] - 1)
            elif move == "Right":
                opponent_new_pos[0] = min(
                    self.width - 1,
                    opponent_new_pos[0] + 1,
                )

            if tuple(opponent_new_pos) not in self.walls:
                op[0], op[1] = opponent_new_pos

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True
                break

    def is_done(self) -> bool:
        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )


class GridGameGUI:
    """Tkinter interface for the visual grid environment."""

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=2,
        walls=None,
    ):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls,
        )

        max_canvas_dim = 600
        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height,
            ),
        )

        canvas_width = self.env.width * self.cell_size
        canvas_height = self.env.height * self.cell_size

        self.canvas = tk.Canvas(
            root,
            width=canvas_width,
            height=canvas_height,
            bg="white",
        )
        self.canvas.pack()

        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial", 14),
        )
        self.label.pack(pady=10)

        self.button = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Arial", 12),
            bg="#000066",
            fg="white",
        )
        self.button.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        # Draw cells and walls.
        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = (
                    "#64748b"
                    if (x, y) in self.env.walls
                    else "#f1f5f9"
                )

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="#cbd5e1",
                )

                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=("Arial", 8, "bold"),
                    )

        # Draw food as orange circles.
        for food_x, food_y in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = food_x * self.cell_size + offset
            y1 = (
                self.env.height - 1 - food_y
            ) * self.cell_size + offset

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706",
            )

        # Draw toxic traps as purple circles.
        for trap_x, trap_y in self.env.toxic_traps:
            offset = self.cell_size * 0.2
            x1 = trap_x * self.cell_size + offset
            y1 = (
                self.env.height - 1 - trap_y
            ) * self.cell_size + offset

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="purple",
                outline="black",
            )

        # Draw opponents as red squares.
        for opponent_x, opponent_y in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = opponent_x * self.cell_size + offset
            y1 = (
                self.env.height - 1 - opponent_y
            ) * self.cell_size + offset

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000",
            )

        # Draw the agent last so it remains visible.
        agent_x, agent_y = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = agent_x * self.cell_size + offset
        y1 = (
            self.env.height - 1 - agent_y
        ) * self.cell_size + offset

        self.canvas.create_oval(
            x1,
            y1,
            x1 + self.cell_size * 0.7,
            y1 + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a",
        )

    def run_loop(self):
        self.button.config(state="disabled")

        def step():
            if not self.env.is_done():
                action = random.choice(["Up", "Down", "Left", "Right"])
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(
                    text=(
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Action: {action}"
                    )
                )
                self.root.after(250, step)
            else:
                if self.env.collision:
                    message = (
                        "Collision! Game Over! "
                        f"Final Score: {self.env.score}"
                    )
                else:
                    message = f"Finished! Final Score: {self.env.score}"

                self.label.config(text=message)
                self.button.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=2,
    )

    root.mainloop()