# MIP example 1

from pyomo.environ import *

m = ConcreteModel()
m.I = Set(initialize=[1,2])
m.y = Var(m.I, within=NonNegativeReals, initialize=0)
m.obj = Objective(sense=maximize, expr= 5*m.y[1] + 6*m.y[2])
@m.Constraint()
def _c1(m):
    return 4*m.y[1] + 7*m.y[2] <= 28
@m.Constraint()
def _c2(m):
    return m.y[1] + m.y[2] <= 5
