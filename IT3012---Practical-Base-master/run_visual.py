from visual_grid_game import GridGameGUI
import tkinter as tk

# U-shaped wall example to match screenshot layout; tweak coordinates as needed
walls = {(4, 3), (5, 3), (6, 3), (4, 4), (6, 4)}

root = tk.Tk()
app = GridGameGUI(
    root,
    width=12,
    height=12,
    num_food=10,
    num_opponents=0,
    walls=walls,
    agent_type="simple",
)
root.mainloop()
