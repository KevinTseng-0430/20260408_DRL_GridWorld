import numpy as np

# Known values from the TA's screenshot (first quadrant)
# V(0,1) = 1.24, V(0,2) = -2.84, V(0,3) = -3.79
# V(1,0) = 1.24, V(1,1) = -2.05, V(1,2) = -3.58, V(1,3) = -3.63
# V(2,0) = -2.83, V(2,1) = -3.58, V(2,2) = -2.96, V(2,3) = -0.78
# V(3,0) = -3.78, V(3,1) = -3.64, V(3,2) = -0.78, V(3,3) = NaN (Gray)

# Actions from Policy Matrix
# P(1,0)=['L'], P(2,0)=['L'], P(3,0)=['L','R'], P(4,0)=['R'], P(5,0)=['R']
# P(0,1)=['D'], P(1,1)=['R','D'], P(2,1)=['L'], P(3,1)=['U'], P(4,1)=['R'], P(5,1)=['R','U']
# P(0,2)=['D'], P(1,2)=['D'], P(2,2)=['U','R'], P(3,2)=['U'], P(4,2)=['R','D'], P(5,2)=['D']

# We need to find gamma and R.
# Let's test combinations of:
# R_step = [0, -1, -0.04]
# gamma = [0.9, 0.99, 1.0]
# Is environment stochastic or deterministic?
# Let's print out the equations.

V = {
    (0,1): 1.24, (0,2): -2.84, (0,3): -3.79, (0,4): -2.84, (0,5): 1.23,
    (1,0): 1.24, (1,1): -2.05, (1,2): -3.58, (1,3): -3.63,
    (2,0): -2.83, (2,1): -3.58, (2,2): -2.96, (2,3): -0.78,
    (3,0): -3.78, (3,1): -3.64, (3,2): -0.78,
    (4,0): -2.84, (4,1): -3.59, (4,2): -2.96, (4,3): -0.78,
}
P = {
    (1,0): ['L'], (2,0): ['L'], (3,0): ['L','R'],
    (0,1): ['D'], (1,1): ['R','D'], (2,1): ['L'], (3,1): ['U'],
    (0,2): ['D'], (1,2): ['D'], (2,2): ['U','R'], (3,2): ['U'], (4,2): ['R','D'],
}

def expected_v(s, actions, gamma, R_step):
    ans = 0
    prob = 1.0 / len(actions)
    for a in actions:
        dx, dy = {'L':(-1,0), 'R':(1,0), 'U':(0,1), 'D':(0,-1)}[a]
        nx, ny = s[0]+dx, s[1]+dy
        if nx<0 or nx>6 or ny<0 or ny>6 or (nx==3 and ny==3): # hit wall / obstacle
            nv = V.get(s, 0) # bounce back
            r = R_step
        elif (nx,ny) in [(0,0), (6,0), (0,6), (6,6)]: # hit grey corners
            nv = 0
            r = R_step # Maybe entering corner gives large reward?
            # Or maybe corners have fixed value?
        else:
            nv = V[(nx,ny)]
            r = R_step
        ans += prob * (r + gamma * nv)
    return ans

print("Testing simple deterministic relations (V(s) = R + gamma*V(s'))")
# If (2,0) goes L to (1,0):
v20, v10 = V[(2,0)], V[(1,0)]
print(f"V(2,0)={v20}, V(1,0)={v10}")
# v20 = R + gamma * v10  =>  -2.83 = R + 1.24 * gamma

# If (0,2) goes D to (0,1):
v02, v01 = V[(0,2)], V[(0,1)]
print(f"V(0,2)={v02}, V(0,1)={v01}")
# v02 = R + gamma * v01  =>  -2.84 = R + 1.24 * gamma

# If (2,1) goes L to (1,1):
v21, v11 = V[(2,1)], V[(1,1)]
print(f"V(2,1)={v21}, V(1,1)={v11}")
# v21 = R + gamma * v11  =>  -3.58 = R - 2.05 * gamma

# From these, we can solve for R and gamma!
# -2.83 = R + 1.24 * gamma
# -3.58 = R - 2.05 * gamma
# Subtract the two:
# -2.83 - (-3.58) = gamma * (1.24 - (-2.05))
# 0.75 = gamma * 3.29
# gamma = 0.75 / 3.29
print(f"Estimated gamma = {0.75 / 3.29}")
print(f"Estimated R = {-2.83 - 1.24 * (0.75/3.29)}")
