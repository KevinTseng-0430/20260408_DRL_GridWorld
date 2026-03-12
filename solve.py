import numpy as np

def evaluate_uniform_random(gamma, R_step, R_goal):
    V = np.zeros((7, 7))
    obstacles = [(0,0), (0,6), (6,0), (6,6), (3,3)]
    
    for _ in range(1000):
        new_V = np.zeros((7, 7))
        delta = 0
        for r in range(7):
            for c in range(7):
                if (r, c) in obstacles:
                    continue
                v = 0
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if nr < 0 or nr >= 7 or nc < 0 or nc >= 7:
                        # bounce back
                        v += 0.25 * (R_step + gamma * V[r, c])
                    elif (nr, nc) in obstacles:
                        # hit obstacle
                        # What if obstacle is absorbing state with reward R_goal?
                        v += 0.25 * (R_goal + gamma * 0)
                    else:
                        v += 0.25 * (R_step + gamma * V[nr, nc])
                new_V[r, c] = v
                delta = max(delta, abs(v - V[r, c]))
        V = new_V
        if delta < 1e-6:
            break
    return V

# Let's try some standard values
# CS188 standard: gamma = 0.9, R_step = 0, R_goal = 10?
V = evaluate_uniform_random(0.9, -1.0, 10.0)
print("gamma=0.9, R_step=-1.0, R_goal=10.0")
print("V(0,1):", V[0,1])
print("V(0,2):", V[0,2])
print("V(0,3):", V[0,3])

V2 = evaluate_uniform_random(0.9, 0.0, 10.0)
print("\ngamma=0.9, R_step=0.0, R_goal=10.0")
print("V(0,1):", V2[0,1])
print("V(0,2):", V2[0,2])

V3 = evaluate_uniform_random(0.9, -0.04, 1.0)
print("\ngamma=0.9, R_step=-0.04, R_goal=1.0")
print("V(0,1):", V3[0,1])
print("V(0,2):", V3[0,2])

V4 = evaluate_uniform_random(1.0, -1.0, 0.0)
print("\ngamma=1.0, R_step=-1.0, R_goal=0.0")
print("V(0,1):", V4[0,1])
print("V(0,2):", V4[0,2])
print("V(0,3):", V4[0,3])

# Try to solve exactly
# V(0,1) = 0.25*(R_goal) + 0.25*(R_step+gamma*V(0,1)) + 0.25*(R_step+gamma*V(0,2)) + 0.25*(R_step+gamma*V(1,1))
# 1.24 = 0.25*R_goal + 0.75*R_step + 0.25*gamma*(1.24 - 2.84 - 2.05)
# 1.24 = 0.25*R_goal + 0.75*R_step + 0.25*gamma*(-3.65)
