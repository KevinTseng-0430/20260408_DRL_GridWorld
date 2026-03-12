import numpy as np

# Let's solve exactly from the values in the first quadrant of the uniform random MDP.
V = {
    (0,1): 1.24, (0,2): -2.84, (0,3): -3.79,
    (1,0): 1.24, (1,1): -2.05, (1,2): -3.58, (1,3): -3.63,
    (2,0): -2.83, (2,1): -3.58, (2,2): -2.96, (2,3): -0.78,
    (3,0): -3.78, (3,1): -3.64, (3,2): -0.78,
}
# Assuming symmetric, V(0,4) = V(0,2), etc.
V[(0,4)] = V[(0,2)]
V[(1,4)] = V[(1,2)]
V[(2,4)] = V[(2,2)]
V[(3,4)] = V[(3,2)]
V[(0,0)] = 0.0 # absorbing

# V(0,1) = 0.25*(R_goal + gamma*0) + 0.25*(R_step + gamma*V(0,2)) + 0.25*(R_step + gamma*V(1,1)) + 0.25*(R_step + gamma*V(0,1))
# 1.24 * 4 = R_goal + gamma*0 + R_step + gamma*(-2.84) + R_step + gamma*(-2.05) + R_step + gamma*(1.24)
# 4.96 = R_goal + 3*R_step + gamma*(-3.65)   --- Eq (1)

# V(0,2) = 0.25*(R_step + gamma*V(0,1)) + 0.25*(R_step + gamma*V(0,3)) + 0.25*(R_step + gamma*V(1,2)) + 0.25*(R_step + gamma*V(0,2))
# -2.84 * 4 = 4*R_step + gamma*(1.24 - 3.79 - 3.58 - 2.84)
# -11.36 = 4*R_step + gamma*(-8.97)          --- Eq (2)

# V(0,3) = 0.25*(R_step + gamma*V(0,2)) + 0.25*(R_step + gamma*V(0,4)) + 0.25*(R_step + gamma*V(1,3)) + 0.25*(R_step + gamma*V(0,3))
# -3.79 * 4 = 4*R_step + gamma*(-2.84*2 - 3.63 - 3.79)
# -15.16 = 4*R_step + gamma*(-13.10)         --- Eq (3)

# From Eq (2) and Eq (3):
# 4*R_step = -11.36 + 8.97*gamma
# 4*R_step = -15.16 + 13.10*gamma
# -11.36 + 8.97*gamma = -15.16 + 13.10*gamma
# 3.8 = 4.13*gamma  =>  gamma = 3.8 / 4.13 ≈ 0.92 ? Let's print exactly:
print("gamma = ", 3.8 / 4.13)
print("gamma roughly = 0.9")

gamma = 0.9
# 4*R_step = -11.36 + 8.97*0.9 = -11.36 + 8.073 = -3.287 ==> R_step = -0.82 ?
# If gamma = 1.0:
# 4*R_step = -11.36 + 8.97 = -2.39 => R_step = -0.59 ?

# Let's test with gamma = 0.9, R_step = -1
# -11.36 = -4 + gamma*(-8.97)  =>  gamma = 7.36 / 8.97 = 0.82
