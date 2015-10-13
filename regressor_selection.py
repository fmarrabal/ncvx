from __future__ import division
from cvxpy import *
from noncvx_admm import *
import numpy as np
import random

np.random.seed(1)
random.seed(1)

m = 161
n = 2*m
k = 10
M = 1
SNR = 20
A = np.random.randn(m, n)
x_true = np.random.uniform(-M, M, size=(n,1))
zeros = random.sample(range(n), n-k)
x_true[zeros] = 0

sigma = norm(A.dot(x_true), 2).value/(np.sqrt(n)*SNR)
noise = np.random.normal(0, sigma, size=(m,1))
b = A.dot(x_true) + noise

print "x true cost", sum_squares(noise).value

# # True solution.
# x = Variable(n)
# bound = Bool(n)
# constr = [abs(x) <= M*bound, sum_entries(bound) <= k]
# cost = sum_squares(A*x - b)
# prob = Problem(Minimize(cost), constr)
# prob.solve(solver=GUROBI)
# print "true value", cost.value
# # print np.around(x.value, decimals=3)

# ADMM solution.
x = Card(n, k, M)
cost = sum_squares(A*x - b)
prob = Problem(Minimize(cost))

RESTARTS = 5
ITERS = 50
prob.solve(method="admm", restarts=RESTARTS,
           # rho=np.random.uniform(1,10,size=RESTARTS),
           max_iter=ITERS, solver=MOSEK, random=True)
print "ADMM value", cost.value

prob.solve(method="relax_and_round")
print "relax and round value", cost.value

# Compare to LASSO.
gamma = Parameter(sign="positive")
reg = norm(x, 1)
cost = sum_squares(A*x - b)
prob = Problem(Minimize(cost + gamma*reg), [abs(x) <= M])
found_card = False
for gamma_val in np.logspace(-2,4,num=100):
    gamma.value = gamma_val
    prob.solve(solver=MOSEK)
    card = sum(abs(x).value > 1e-3)
    if card <= k:
        # Polish.
        polish_prob = Problem(Minimize(cost),
                              [abs(x) <= (abs(x).value > 1e-3)*M])
        print polish_prob.solve(solver=MOSEK)
        found_card = True
        break
assert found_card
print "LASSO value", cost.value