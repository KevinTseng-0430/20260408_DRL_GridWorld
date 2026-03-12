import numpy as np

# We have a 7x7 grid.
# V[y, x] is the value.
V_target = np.array([
    [np.nan, 1.24, -2.84, -3.79, -2.84, 1.23, np.nan],
    [1.24, -2.05, -3.58, -3.64, -3.59, -2.06, 1.23],
    [-2.83, -3.58, -2.96, -0.78, -2.96, -3.59, -2.84],
    [-3.78, -3.63, -0.78, np.nan, -0.78, -3.64, -3.79],
])

def test_mdp(R_step, R_wall, R_obstacle, R_goal, P_intended=1.0, gamma=0.9):
    # Try different policy matrices.
    pass

# Instead of exhaustive search, let's look at the Policy Matrix in the TA's image explicitly.
# The Policy Matrix shows EXACTLY the policy being evaluated!
# Let's write down the explicit Policy Matrix from the image (bottom half is symmetric).
# P[y, x] = list of actions
P = {
    (0,1): ['L'], (0,2): ['L'], (0,3): ['L','R'], (0,4): ['R'], (0,5): ['R'],
    (1,0): ['D'], (1,1): ['R','D'], (1,2): ['L'], (1,3): ['U'], (1,4): ['R'], (1,5): ['R','U'], (1,6): ['D'],
    (2,0): ['D'], (2,1): ['D'], (2,2): ['U','R'], (2,3): ['U'], (2,4): ['R','D'], (2,5): ['D'], (2,6): ['D'],
    (3,0): ['U','D'], (3,1): ['R'], (3,2): ['R'], (3,4): ['L'], (3,5): ['L'], (3,6): ['U','D']
}

# Values for these states:
V = {
    (0,1): 1.24, (0,2): -2.84, (0,3): -3.79, (0,4): -2.84, (0,5): 1.23,
    (1,0): 1.24, (1,1): -2.05, (1,2): -3.58, (1,3): -3.64, (1,4): -3.59, (1,5): -2.06, (1,6): 1.23,
    (2,0): -2.83, (2,1): -3.58, (2,2): -2.96, (2,3): -0.78, (2,4): -2.96, (2,5): -3.59, (2,6): -2.84,
    (3,0): -3.78, (3,1): -3.63, (3,2): -0.78, (3,4): -0.78, (3,5): -3.64, (3,6): -3.79
}

# The Bellman equation for evaluated policy:
# V(s) = sum_a (1/|A(s)|) [ R(s,a,s') + gamma * V(s') ]
# Let's assume R(s,a,s') is R_step for normal steps.
# What if transitioning TO Grey cell (Corners) gives +10?
# V(0,1) = R_step + gamma * V(0,0). If V(0,0)=0, V(0,1)=R_step + gamma*0 = R_step = 1.24.
# V(0,2) = R_step + gamma * V(0,1).  -2.84 = R_step + gamma*1.24 => -2.84 = 1.24 + gamma*1.24 => gamma = -4.08 / 1.24 = -3.29.
# This proves P(0,1)=L does NOT simply go to (0,0) and terminate with V=0 and R=1.24!

# What if P is drawn WITH (x,y) SWAPPED?
# 'L' means negative y? (i.e. UP in conventional image coordinates, but LEFT geometrically).
# If (0,1) has 'L' maybe it points to (0,0).

print("Check linear dependencies:")
print(f"V(0,2) = {V[0,2]}, V(0,1) = {V[0,1]}")
print(f"V(1,2) = {V[1,2]}, V(1,1) = {V[1,1]}")

