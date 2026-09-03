# IT3012 Practical Base - Lab 02

This repository contains a small grid-based agent simulation for the IT3012 lab assignments.

## Project Structure

- `agent.py` - Agent implementations, including:
  - `GreedyGridAgent` for the grid simulation
  - `SimpleReflexAgent` for reflex-based behavior
  - `ModelBasedAgent` for stateful decision-making
  - `SearchAgent` for BFS path planning
- `grid_game.py` - A simple non-visual grid hunt environment with food, walls, and traps.
- `visual_grid_game.py` - A Tkinter-based visual environment with agents and moving opponents.
- `simulator.py` - Entry point for running the non-visual grid hunt simulation.
- `test_suite.py` - Unit tests for the reflex, model-based, and search agents.

## Getting Started

1. Install Python 3.11+.
2. Run the test suite:

```bash
python test_suite.py
```

3. Run the simulation:

```bash
python simulator.py
```

4. Run the visual grid game:

```bash
python visual_grid_game.py
```

## Notes

- The test suite expects `SimpleReflexAgent`, `ModelBasedAgent`, and `SearchAgent` to be available from `agent.py`.
- `SearchAgent.bfs_search` uses breadth-first search to return the shortest path avoiding walls.
