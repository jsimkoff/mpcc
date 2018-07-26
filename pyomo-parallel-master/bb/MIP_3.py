# MIP_3.py
# another MIP example

from pyomo.environ import *

m = ConcreteModel()
m.I = Set(initialize=[1,2,3, 4, 5])
m.y = Var(m.I, within=NonNegativeReals, initialize=0)

m.obj = Objective(sense=maximize, expr= 4*m.y[1] - m.y[2] )
@m.Constraint()
def _c1(m):
    return 3*m.y[2] - 2*m.y[2] + m.y[3] == 14
@m.Constraint()
def _c2(m):
    return m.y[2] + m.y[4] == 3
@m.Constraint()
def _c3(m):
    return 2*m.y[1] - 2*m.y[2] + m.y[5] == 3

if __name__ == "__main__":
    m.y.domain = NonNegativeIntegers
    results = SolverFactory('glpk').solve(m, tee=True, keepfiles=True)
    m.display()
