# Grid Map Reinforcement Learning Project

A Reinforcement Learning (RL) project structured around the **CRISP-DM (Cross-Industry Standard Process for Data Mining)** methodology. This project implements an interactive web application that allows users to configure start points, end points, and obstacles on a customizable grid map. It demonstrates backend computations for "Random Policy Evaluation" and "Optimal Path Finding (Value Iteration)" through an intuitive graphical interface.  
Liev Demo: https://bytseng.dpdns.org/DRL_HW1/  
<img width="718" height="773" alt="image" src="https://github.com/user-attachments/assets/145bd1d1-6016-40ec-92eb-d54087091f15" />


---

## 1. Business Understanding

### Project Objective
The core objective of this project is to **visualize abstract reinforcement learning algorithms**. It helps learners and users understand two fundamental concepts of the Markov Decision Process (MDP) through an intuitive Graphical User Interface (GUI):
1. **Policy Evaluation**: Calculating the expected value of each state under a given random stochastic policy.
2. **Finding the Optimal Policy**: Discovering the optimal action selection that maximizes cumulative rewards through Value Iteration, thereby deriving the shortest obstacle-avoiding path to the goal.

### Success Criteria
*   Build an interactive, decoupled web application (Flask backend + Vanilla JS frontend).
*   Provide a highly configurable map environment (grid sizes from 5x5 to 9x9, custom start/end points and obstacles).
*   Ensure accurate algorithm computations that reach mathematical convergence (Threshold $10^{-6}$).
*   Properly visualize the Policy Matrix (action directions for each cell) and the Value Matrix (a heat-map style value gradient).

---

## 2. Data Understanding

In reinforcement learning, "data" is not a static dataset as seen in traditional machine learning; rather, it is defined by interactions with the **Environment**.

### Markov Decision Process (MDP) Definition
*   **State Space ($\mathcal{S}$)**:
    *   Every accessible free cell on the grid represents a state, denoted as $(row, col)$.
    *   Obstacles are excluded from the state space and cannot be entered.
    *   The End Cell is a **Terminal State**. Once reached, the episode ends, and its future expected value is defined as $V(terminal) = 0$.
*   **Action Space ($\mathcal{A}$)**:
    *   Each state has 4 possible actions: `["U" (Up), "D" (Down), "L" (Left), "R" (Right)]`.
    *   If an action leads into a boundary wall or an obstacle, the state remains unchanged (bouncing back to the original cell).
*   **Reward Function ($\mathcal{R}$)**:
    *   Reaching the End state: **$+10$**.
    *   Any other movement step: **$-1$**.
    *   *Design Rationale: The negative reward penalizes taking longer routes, while the positive reward strongly attracts the agent toward the goal, generating a distinct value gradient.*
*   **Discount Factor ($\gamma$)**: Set to `0.9` to represent the present value of future rewards.

---

## 3. Data Preparation

Data preparation corresponds to the construction and transmission of the "Environment" established by the user on the frontend interface.

### Environment Setup
1.  **Grid Initialization**: Users generate an $N \times N$ empty grid via the URL parameter `?n=X`.
2.  **State Configuration**: Users define the environment via mouse click events:
    *   `Start` (Green): The starting node for the agent to find the optimal path.
    *   `End` (Red): The Terminal State.
    *   `Obstacles` (Gray): Specific coordinates removed from the Free States $\mathcal{S}$.
3.  **State Encapsulation and Transmission**: The frontend captures the `[row, col]` coordinates of all cells, packages them into a JSON payload, and sends them to the backend Flask API endpoints (`/evaluate` or `/optimize`).

---

## 4. Modeling

This project implements two dynamic programming-based reinforcement learning algorithms, updating state values via the Bellman Equations.

### Model A: Random Policy Evaluation
This model answers the question: *"If a robot randomly wanders in a maze, what is its expected score from any given starting position?"*
1.  **Stochastic Policy Generation**: For each free state, 1 to 4 viable action weights are randomly assigned (with uniform probability distribution).
2.  **Bellman Expected Equation**:
    $$V(s) = \sum_{a} \pi(a|s) \big[ \mathcal{R}(s,a,s') + \gamma V(s') \big]$$
    *   Where $\pi(a|s) = 1 / |policy[s]|$ (uniform probability).
3.  **Iterative Update**: Repeatedly recalculate $V(s)$ for all states until convergence is met (when maximum change $\Delta < 10^{-6}$).

### Model B: Value Iteration for Optimal Path
This model answers the question: *"How should the robot move to reach the destination with the highest possible score (shortest path)?"*
1.  **Bellman Optimality Equation**:
    $$V^*(s) = \max_{a} \big[ \mathcal{R}(s,a,s') + \gamma V^*(s') \big]$$
    *   Instead of considering probabilities, it updates $V(s)$ by greedily choosing the action that yields the highest expected value.
2.  **Convergence and Policy Extraction**:
    *   Once the $V^*$ matrix converges, a final pass over all states extracts the optimal deterministic policy $\pi^*(s)$ by identifying the action that produces the maximum $V$ value.
3.  **Path Tracing**: Starting from the Start coordinate, the agent moves entirely greedily following $\pi^*$, recording the sequence of coordinates as the optimal path.

---

## 5. Evaluation

We evaluate and verify whether our mathematical models align perfectly with the user's visual expectations.

### Frontend Result Analysis
1.  **Dual-Matrix Display**:
    *   **Policy Matrix ($\pi$)**: Renders the computed action arrays (e.g., `["↑", "→"]` or `["↓"]`) directly into the corresponding cells. This allows for an intuitive understanding of the agent's behavioral tendencies.
    *   **Value Matrix ($V$)**: Displays the computed numerical values rounded to two decimal places. Utilizing CSS color coding (positive green > 0, negative red < 0), it visually demonstrates the **Value Gradient** radiating outwards from the destination (0).
2.  **Random Policy vs. Optimal Policy Comparison**:
    *   When evaluating a **Random Policy**, the agent takes many unnecessary detours, accumulating heavy $-1$ penalties. Consequently, the vast majority of cells in the Value Matrix display very low negative numbers (e.g., $-25.43$).
    *   After computing the **Optimal Policy**, the values in the Value Matrix rise significantly, as the algorithm guarantees no wasted steps, clearly illustrating the "most efficient" path value.
3.  **Optimal Path Highlighting**:
    *   When computing the Optimal Path, the frontend processes the `path` array returned by the backend and applies a **golden glowing border (`.path-highlight`)** to the main grid map and the two lower matrices. This rendered path perfectly circumvents all `Obstacles` to reach the destination directly.

---

## 6. Deployment

The project currently runs on a local server and includes complete startup scripts and lightweight dependencies.

### Dependencies
*   Python 3.8+
*   Flask

### Startup Instructions
1.  Open Terminal and navigate to the project directory.
2.  Install Flask (if not already installed): `pip install flask`
3.  Run the startup script: `python3 app.py` (Defaults to running on Port 5001).
4.  Open your browser and visit [http://127.0.0.1:5001](local) to interact with the grid map.
