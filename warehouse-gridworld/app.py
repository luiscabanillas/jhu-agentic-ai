"""
Warehouse Navigation GridWorld
==============================

A small reinforcement-learning-style game built on a Gymnasium environment and
served through a Gradio UI.

- The warehouse is a 2D grid maze.
- Cells:
    S  -> start cell        (blue)
    G  -> goal cell         (green)
    X  -> obstacle / shelf  (dark)
    .  -> empty floor       (light)
    A  -> the agent         (red circle)
- You control the red agent with the keyboard ARROW KEYS or the on-screen
  buttons. Movement is restricted to UP / RIGHT / DOWN / LEFT (no diagonals).
- The agent cannot move through obstacles or off the grid.
- "Reset / New Maze" randomizes the start, goal, and ~20% obstacle density,
  guaranteeing the maze is solvable, and places the agent back on the start.

Run:
    pip install -r requirements.txt
    python app.py
"""

from collections import deque

import gymnasium as gym
import matplotlib

matplotlib.use("Agg")  # headless backend, required for server-side rendering
import matplotlib.pyplot as plt
import numpy as np
from gymnasium import spaces
from matplotlib.patches import Circle

import gradio as gr

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
GRID_SIZE = 10            # grid is GRID_SIZE x GRID_SIZE
OBSTACLE_DENSITY = 0.20   # ~20% of cells become obstacles
STEP_LIMIT = 100          # episode times out after this many steps

# Action encoding (matches the assignment spec exactly).
UP, RIGHT, DOWN, LEFT = 0, 1, 2, 3
ACTION_DELTAS = {
    UP:    (-1, 0),   # decrease row
    RIGHT: (0, 1),    # increase column
    DOWN:  (1, 0),    # increase row
    LEFT:  (0, -1),   # decrease column
}
ACTION_NAMES = {UP: "UP", RIGHT: "RIGHT", DOWN: "DOWN", LEFT: "LEFT"}

# Reward shaping constants.
R_INVALID = -1.0      # tried to move into a wall / obstacle / off-grid
R_CLOSER = 0.5        # move reduced Manhattan distance to goal
R_FARTHER = -0.7      # move increased Manhattan distance to goal
R_NEW_CELL = 0.1      # small bonus for visiting a cell for the first time
R_GOAL = 10.0         # large reward for reaching the goal
R_TIMEOUT = -5.0      # penalty for hitting the step limit without finishing


def manhattan(a, b):
    """Manhattan distance between two (row, col) points."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# --------------------------------------------------------------------------- #
# Gymnasium Environment
# --------------------------------------------------------------------------- #
class WarehouseGridWorldEnv(gym.Env):
    """A solvable random warehouse maze.

    Observation: Box of 4 floats in [0, 1]
        [agent_x_norm, agent_y_norm, goal_x_norm, goal_y_norm]
        where x is the column and y is the row, normalized by (GRID_SIZE - 1).

    Action: Discrete(4) -> 0=UP, 1=RIGHT, 2=DOWN, 3=LEFT
    """

    metadata = {"render_modes": ["rgb_array"]}

    def __init__(self, size=GRID_SIZE, obstacle_density=OBSTACLE_DENSITY,
                 step_limit=STEP_LIMIT):
        super().__init__()
        self.size = size
        self.obstacle_density = obstacle_density
        self.step_limit = step_limit

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(4,), dtype=np.float32
        )

        # State, initialized in reset().
        self.grid = None          # 0 = free, 1 = obstacle
        self.start = None         # (row, col)
        self.goal = None          # (row, col)
        self.agent = None         # (row, col)
        self.visited = None       # set of visited cells
        self.steps = 0
        self.total_score = 0.0
        self.last_reward = 0.0
        self.reached = False

    # ----------------------------- helpers --------------------------------- #
    def _is_solvable(self, grid, start, goal):
        """BFS from start to goal over free cells."""
        if grid[start] == 1 or grid[goal] == 1:
            return False
        q = deque([start])
        seen = {start}
        while q:
            r, c = q.popleft()
            if (r, c) == goal:
                return True
            for dr, dc in ACTION_DELTAS.values():
                nr, nc = r + dr, c + dc
                if (0 <= nr < self.size and 0 <= nc < self.size
                        and grid[nr, nc] == 0 and (nr, nc) not in seen):
                    seen.add((nr, nc))
                    q.append((nr, nc))
        return False

    def _generate_maze(self):
        """Sample a random, solvable maze with a fresh start and goal."""
        rng = self.np_random
        n_cells = self.size * self.size
        n_obstacles = int(round(self.obstacle_density * n_cells))

        for _ in range(1000):  # rejection sampling until we get a solvable maze
            # Pick distinct start and goal.
            cells = rng.permutation(n_cells)
            start = (int(cells[0]) // self.size, int(cells[0]) % self.size)
            goal = (int(cells[1]) // self.size, int(cells[1]) % self.size)

            grid = np.zeros((self.size, self.size), dtype=np.int8)
            # Candidate obstacle cells: anything that is not start or goal.
            candidates = [
                (r, c)
                for r in range(self.size)
                for c in range(self.size)
                if (r, c) not in (start, goal)
            ]
            idx = rng.permutation(len(candidates))[:n_obstacles]
            for i in idx:
                grid[candidates[int(i)]] = 1

            if self._is_solvable(grid, start, goal):
                return grid, start, goal

        # Extremely unlikely fallback: empty grid (always solvable).
        grid = np.zeros((self.size, self.size), dtype=np.int8)
        return grid, start, goal

    def _get_obs(self):
        denom = max(self.size - 1, 1)
        ar, ac = self.agent
        gr_, gc = self.goal
        return np.array(
            [ac / denom, ar / denom, gc / denom, gr_ / denom],
            dtype=np.float32,
        )

    def _get_info(self):
        return {
            "agent": self.agent,
            "goal": self.goal,
            "start": self.start,
            "steps": self.steps,
            "total_score": self.total_score,
            "last_reward": self.last_reward,
            "distance": manhattan(self.agent, self.goal),
            "reached": self.reached,
        }

    # ----------------------------- API ------------------------------------- #
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.grid, self.start, self.goal = self._generate_maze()
        self.agent = self.start  # agent always begins on the start cell
        self.visited = {self.agent}
        self.steps = 0
        self.total_score = 0.0
        self.last_reward = 0.0
        self.reached = False
        return self._get_obs(), self._get_info()

    def step(self, action):
        if self.reached:
            # Episode already finished; ignore further input.
            return self._get_obs(), 0.0, True, False, self._get_info()

        self.steps += 1
        dr, dc = ACTION_DELTAS[int(action)]
        r, c = self.agent
        nr, nc = r + dr, c + dc

        prev_dist = manhattan(self.agent, self.goal)
        terminated = False
        truncated = False

        # Invalid move: off-grid or into an obstacle -> stay in place, penalize.
        if not (0 <= nr < self.size and 0 <= nc < self.size) or self.grid[nr, nc] == 1:
            reward = R_INVALID
        else:
            self.agent = (nr, nc)
            new_dist = manhattan(self.agent, self.goal)

            if self.agent == self.goal:
                reward = R_GOAL
                terminated = True
                self.reached = True
            else:
                # Distance-based shaping.
                if new_dist < prev_dist:
                    reward = R_CLOSER
                else:
                    reward = R_FARTHER
                # Exploration bonus for a previously unseen cell.
                if self.agent not in self.visited:
                    reward += R_NEW_CELL
            self.visited.add(self.agent)

        # Step-limit timeout.
        if not terminated and self.steps >= self.step_limit:
            reward += R_TIMEOUT
            truncated = True

        self.last_reward = reward
        self.total_score += reward
        return self._get_obs(), reward, terminated, truncated, self._get_info()

    # ----------------------------- rendering ------------------------------- #
    def render_figure(self):
        """Render the current state as a matplotlib Figure (the maze image)."""
        fig, ax = plt.subplots(figsize=(6, 6))
        n = self.size

        # Base colors.
        empty_color = "#e9eef5"     # light empty floor
        obstacle_color = "#2c3e50"  # dark obstacle / shelf
        start_color = "#2d7dd2"     # blue start
        goal_color = "#27ae60"      # green goal

        for r in range(n):
            for c in range(n):
                cell = (r, c)
                if self.grid[r, c] == 1:
                    color = obstacle_color
                elif cell == self.start:
                    color = start_color
                elif cell == self.goal:
                    color = goal_color
                else:
                    color = empty_color

                ax.add_patch(
                    plt.Rectangle(
                        (c, n - 1 - r), 1, 1,
                        facecolor=color, edgecolor="#9aa7b8", linewidth=1.0,
                    )
                )

                # Letter labels for special cells.
                label = None
                text_color = "white"
                if self.grid[r, c] == 1:
                    label = "X"
                elif cell == self.start:
                    label = "S"
                elif cell == self.goal:
                    label = "G"
                if label:
                    ax.text(
                        c + 0.5, n - 1 - r + 0.5, label,
                        ha="center", va="center",
                        fontsize=12, fontweight="bold", color=text_color,
                    )

        # The red agent (drawn last so it sits on top).
        ar, ac = self.agent
        ax.add_patch(
            Circle((ac + 0.5, n - 1 - ar + 0.5), 0.32,
                   facecolor="#e74c3c", edgecolor="white", linewidth=2.0, zorder=5)
        )
        ax.text(
            ac + 0.5, n - 1 - ar + 0.5, "A",
            ha="center", va="center", fontsize=11,
            fontweight="bold", color="white", zorder=6,
        )

        ax.set_xlim(0, n)
        ax.set_ylim(0, n)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.tight_layout(pad=0.5)
        return fig


# --------------------------------------------------------------------------- #
# Gradio UI
# --------------------------------------------------------------------------- #
def scoreboard_md(info):
    """Build the markdown scoreboard shown beside the grid."""
    reached = "✅ Yes" if info["reached"] else "❌ No"
    return f"""
### 🏆 Scoreboard

| Metric | Value |
| --- | --- |
| **Total score** | `{info['total_score']:.2f}` |
| **Last reward** | `{info['last_reward']:.2f}` |
| **Steps** | `{info['steps']} / {STEP_LIMIT}` |
| **Agent position** | `(row {info['agent'][0]}, col {info['agent'][1]})` |
| **Goal position** | `(row {info['goal'][0]}, col {info['goal'][1]})` |
| **Manhattan distance** | `{info['distance']}` |
| **Goal reached** | {reached} |
"""


def status_line(info, last_action=None):
    if info["reached"]:
        return "🎉 **Goal reached!** Press *Reset / New Maze* to play again."
    if info["steps"] >= STEP_LIMIT:
        return "⏱️ **Out of steps!** Press *Reset / New Maze* to try again."
    if last_action is not None:
        return f"Moved **{ACTION_NAMES[last_action]}** — keep going!"
    return "Use the **arrow keys** or the buttons to guide the red agent to the green goal."


def build_app():
    env = WarehouseGridWorldEnv()

    def do_reset():
        _, info = env.reset()
        return env.render_figure(), scoreboard_md(info), status_line(info)

    def do_move(action):
        # Ignore moves after the episode ends; user must reset.
        if env.reached or env.steps >= STEP_LIMIT:
            info = env._get_info()
            return env.render_figure(), scoreboard_md(info), status_line(info)
        _, _, _, _, info = env.step(action)
        return env.render_figure(), scoreboard_md(info), status_line(info, action)

    # JS that turns physical arrow keys into clicks on the hidden buttons.
    arrow_key_js = """
    () => {
        const map = {
            "ArrowUp":    "btn-up",
            "ArrowRight": "btn-right",
            "ArrowDown":  "btn-down",
            "ArrowLeft":  "btn-left",
        };
        if (window.__warehouseKeyHandler) {
            document.removeEventListener("keydown", window.__warehouseKeyHandler);
        }
        window.__warehouseKeyHandler = (e) => {
            const id = map[e.key];
            if (!id) return;
            e.preventDefault();  // stop the page from scrolling
            const btn = document.getElementById(id);
            if (btn) btn.click();
        };
        document.addEventListener("keydown", window.__warehouseKeyHandler);
    }
    """

    with gr.Blocks(title="Warehouse GridWorld", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "# 📦 Warehouse Navigation GridWorld\n"
            "Guide the red **agent (A)** from the blue **start (S)** to the "
            "green **goal (G)**, avoiding the dark **shelves (X)**. "
            "Use the **arrow keys** or the on-screen buttons."
        )

        with gr.Row():
            with gr.Column(scale=3):
                grid_img = gr.Plot(label="Warehouse")
            with gr.Column(scale=2):
                board = gr.Markdown()
                status = gr.Markdown()

                # On-screen D-pad.
                with gr.Row():
                    gr.Column(scale=1)
                    up_btn = gr.Button("⬆️ Up", elem_id="btn-up")
                    gr.Column(scale=1)
                with gr.Row():
                    left_btn = gr.Button("⬅️ Left", elem_id="btn-left")
                    down_btn = gr.Button("⬇️ Down", elem_id="btn-down")
                    right_btn = gr.Button("➡️ Right", elem_id="btn-right")
                reset_btn = gr.Button("🔄 Reset / New Maze", variant="primary")

        outputs = [grid_img, board, status]

        up_btn.click(lambda: do_move(UP), outputs=outputs)
        right_btn.click(lambda: do_move(RIGHT), outputs=outputs)
        down_btn.click(lambda: do_move(DOWN), outputs=outputs)
        left_btn.click(lambda: do_move(LEFT), outputs=outputs)
        reset_btn.click(do_reset, outputs=outputs)

        # Initialize the first maze and wire up the keyboard listener on load.
        demo.load(do_reset, outputs=outputs)
        demo.load(None, None, None, js=arrow_key_js)

    return demo


if __name__ == "__main__":
    build_app().launch()
