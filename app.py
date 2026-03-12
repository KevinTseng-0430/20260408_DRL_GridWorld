import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Action definitions: (delta_row, delta_col)
ACTIONS = {
    "U": (-1, 0),
    "D": ( 1,  0),
    "L": ( 0, -1),
    "R": ( 0,  1),
}
ARROW = {"U": "↑", "D": "↓", "L": "←", "R": "→"}
ACTION_KEYS = list(ACTIONS.keys())


@app.route("/")
def index():
    try:
        n = int(request.args.get("n", 5))
    except ValueError:
        n = 5
    n = max(5, min(9, n))  # clamp to [5, 9]
    return render_template("index.html", n=n)


@app.route("/evaluate", methods=["POST"])
def evaluate():
    """
    Receive grid configuration, generate random policy,
    run iterative policy evaluation, return results.

    Request JSON:
        {
          "n": int,
          "start": [row, col],
          "end":   [row, col],
          "obstacles": [[row, col], ...]
        }

    Response JSON:
        {
          "policy": { "r,c": "U"|"D"|"L"|"R", ... },
          "values":  { "r,c": float, ... },
          "arrows":  { "r,c": "↑"|"↓"|"←"|"→", ... }
        }
    """
    data = request.get_json()
    n = int(data["n"])
    start = tuple(data["start"])       # (row, col)
    end   = tuple(data["end"])         # (row, col)
    obstacles = set(tuple(o) for o in data["obstacles"])

    # ── Build free states (all cells that are not obstacles) ──────────────────
    all_states = {(r, c) for r in range(n) for c in range(n)}
    free_states = all_states - obstacles          # includes start and end

    # ── Generate stochastic policy for non-terminal, non-obstacle states ───────
    # Each state gets a random subset of 1–4 actions (uniform over chosen actions)
    policy = {}   # state -> list of action keys
    for state in free_states:
        if state == end:
            continue  # terminal — no action needed
        k = random.randint(1, len(ACTION_KEYS))          # how many actions
        policy[state] = random.sample(ACTION_KEYS, k)    # which actions

    # ── Iterative Policy Evaluation (stochastic Bellman) ─────────────────────
    # V(s) = Σ_a π(a|s) · [R + γ · V(s'(a))]
    # π(a|s) = 1 / |policy[s]|  (uniform over chosen actions)
    gamma     = 0.9
    reward    = -1.0
    threshold = 1e-6
    max_iter  = 10_000

    V = {s: 0.0 for s in free_states}

    for _ in range(max_iter):
        delta = 0.0
        new_V = {}
        for state in free_states:
            if state == end:
                new_V[state] = 0.0
                continue

            actions = policy[state]
            prob    = 1.0 / len(actions)   # uniform over chosen actions
            v = 0.0
            r, c = state
            for action in actions:
                dr, dc = ACTIONS[action]
                next_s = (r + dr, c + dc)
                if next_s not in free_states:
                    next_s = state          # bounce back
                
                # Reward logic: +10 for reaching the goal, -1 otherwise
                curr_reward = 10.0 if next_s == end else reward
                
                v += prob * (curr_reward + gamma * V[next_s])

            new_V[state] = v
            delta = max(delta, abs(v - V[state]))

        V = new_V
        if delta < threshold:
            break

    # ── Serialise results (use "r,c" string keys for JSON) ────────────────────
    # policy_out: list of action keys per state
    policy_out = {f"{r},{c}": acts          for (r, c), acts in policy.items()}
    values_out = {f"{r},{c}": round(v, 4)   for (r, c), v   in V.items()}
    # arrows_out: list of arrow symbols per state
    arrows_out = {f"{r},{c}": [ARROW[a] for a in acts]
                  for (r, c), acts in policy.items()}

    return jsonify(policy=policy_out, values=values_out, arrows=arrows_out)


@app.route("/optimize", methods=["POST"])
def optimize():
    """
    Run Value Iteration to find V* and deterministic optimal policy π*.
    Also trace the optimal path from start to end.
    """
    data = request.get_json()
    n = int(data["n"])
    start = tuple(data["start"])
    end   = tuple(data["end"])
    obstacles = set(tuple(o) for o in data["obstacles"])

    all_states = {(r, c) for r in range(n) for c in range(n)}
    free_states = all_states - obstacles

    gamma     = 0.9
    reward    = -1.0
    threshold = 1e-6
    max_iter  = 10_000

    # 1. Value Iteration
    V = {s: 0.0 for s in free_states}
    
    for _ in range(max_iter):
        delta = 0.0
        new_V = {}
        for state in free_states:
            if state == end:
                new_V[state] = 0.0
                continue

            best_v = float('-inf')
            r, c = state
            for action in ACTION_KEYS:
                dr, dc = ACTIONS[action]
                next_s = (r + dr, c + dc)
                if next_s not in free_states:
                    next_s = state  # bounce back
                
                curr_reward = 10.0 if next_s == end else reward
                v = curr_reward + gamma * V[next_s]
                best_v = max(best_v, v)
                
            new_V[state] = best_v
            delta = max(delta, abs(best_v - V[state]))
            
        V = new_V
        if delta < threshold:
            break

    # 2. Extract Optimal Policy π*
    policy = {}
    for state in free_states:
        if state == end:
            continue
            
        best_v = float('-inf')
        best_actions = []
        r, c = state
        
        for action in ACTION_KEYS:
            dr, dc = ACTIONS[action]
            next_s = (r + dr, c + dc)
            if next_s not in free_states:
                next_s = state
            
            curr_reward = 10.0 if next_s == end else reward
            v = curr_reward + gamma * V[next_s]
            
            # Use a small tolerance for floating point comparisons
            if v > best_v + 1e-9:
                best_v = v
                best_actions = [action]
            elif abs(v - best_v) <= 1e-9:
                best_actions.append(action)
                
        # For tracing path cleanly, just pick the first best action
        # but return all tied optimal actions for the matrix display
        policy[state] = best_actions

    # 3. Trace Optimal Path
    path = []
    curr = start
    visited = set()
    while curr != end and curr not in visited:
        path.append(list(curr))
        visited.add(curr)
        if curr not in policy or not policy[curr]:
            break  # Trapped
        # Just follow the first optimal action
        action = policy[curr][0]
        dr, dc = ACTIONS[action]
        next_s = (curr[0] + dr, curr[1] + dc)
        if next_s not in free_states:
            break  # Bounced into wall infinitely
        curr = next_s
    
    # 4. Serialise
    policy_out = {f"{r},{c}": acts for (r, c), acts in policy.items()}
    values_out = {f"{r},{c}": round(v, 4) for (r, c), v in V.items()}
    arrows_out = {f"{r},{c}": [ARROW[a] for a in acts] for (r, c), acts in policy.items()}

    return jsonify(policy=policy_out, values=values_out, arrows=arrows_out, path=path)


if __name__ == "__main__":
    # macOS often uses port 5000 for AirPlay, using 5001 instead
    app.run(debug=True, port=5001)
