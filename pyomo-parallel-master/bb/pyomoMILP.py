# simple MILP

from pyomo.environ import *

m = ConcreteModel()
m.I = Set(initialize=[1,2])
m.y = Var(m.I, within=NonNegativeReals)
# m.y = Var(m.I, within=Integers)

m.obj = Objective(sense=maximize, expr= 5*m.y[1] + 6*m.y[2])

@m.Constraint()
def _c1(m):
    return 4*m.y[1] + 7*m.y[2] <= 28


@m.Constraint()
def _c2(m):
    return m.y[1] + m.y[2] <= 5

m.y[1].fix(2)
m.y[2].fix(3)
solver = SolverFactory('glpk')
results = solver.solve(m, keepfiles=False, tee=True)
m.display()
