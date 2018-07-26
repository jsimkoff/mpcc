# dynamic tank level mpec - 3 tanks, 4 total flows and control valves
# MPCC formulation

from pyomo.environ import *
from pyomo.dae import *

from plottanks import plot_tanks


Ntank = 5
m = ConcreteModel()
m.I = RangeSet(Ntank)
m.t = ContinuousSet(bounds=[0,60])


m.L = Var(m.I, m.t, within=NonNegativeReals, initialize=0.75, bounds=(0.0001, 1.0))
m.delL = Var(m.I, m.t, within=NonNegativeReals, bounds=(0.0001, 1.0))
m.F = Var(m.I, m.t)
m.F0 = Var(m.t)
m.w = Var(m.I, m.t, bounds=(0.1,1))
m.w0 = Var(m.t, bounds=(0.1,1))

m.k = Param(m.I, initialize=0.1, mutable=True)
m.k0 = Param(initialize=0.1)
m.k[1] = 0.14
m.k[2] = 0.2
m.k[3] = 0.3
m.H = Param(m.I, initialize=0.5, mutable=True)
m.H[2] = 0.6
# m.H[5] = 0.4
m.A = Param(m.I, initialize=1.0)

m.dLdt = DerivativeVar(m.L, wrt=m.t)

# m.y = Var(m.I, m.t, within=NonNegativeReals)
# m.y2 = Var(m.I, m.t, within=NonNegativeReals)

m.y = Var(m.I, m.t, within=Binary)
m.y2 = Var(m.I, m.t, within=Binary)

m.sp = Var(m.I, m.t, within=(NonNegativeReals))
m.sn = Var(m.I, m.t, within=NonNegativeReals)

# m.sp = Var(m.I, m.t, bounds=(-0.01, 1))
# m.sn = Var(m.I, m.t, bounds=(-0.01, 1))

m.M1 = 0.60
m.M2 = 0.40

@m.Constraint(m.I, m.t)
def _Ldot(m, i, t):

    if i > 1:
        return m.dLdt[i, t] == 1/m.A[i]*(m.F[i-1,t] - m.F[i, t])
    elif i == 1:
        return m.dLdt[i, t] == 1/m.A[i]*(m.F0[t] - m.F[i, t])
    else:
        Constraint.Skip

@m.Constraint(m.I, m.t)
def _F(m, i, t):

    return m.F[i, t] == m.w[i, t]*m.k[i]*(m.delL[i, t])**0.5

@m.Constraint(m.t)
def _F0(m, t):
    return m.F0[t] == m.k0*m.w0[t]
### NEED TO ADD MPCC formulation :

@m.Constraint(m.I, m.t)
def _delL(m, i, t):
    if i < Ntank:
        return m.delL[i, t] == (m.L[i, t] - (m.L[i+1, t] - m.H[i+1]))*m.y[i, t]  \
                                + m.L[i, t]*(m.y2[i, t])
    elif i == Ntank:
        return m.delL[i, t] == m.L[i, t]
    else:
        return Constraint.Skip

@m.Constraint(m.I, m.t)
def _slacks(m, i, t):
    if i < Ntank:
        return m.sp[i, t] - m.sn[i, t] == m.L[i+1, t] - m.H[i+1]
    else:
        return Constraint.Skip

@m.Constraint(m.I, m.t)
def _ysum(m, i, t):
    return m.y[i, t] + m.y2[i, t] == 1

# @m.Constraint(m.I, m.t)
# def compslack1(m, i, t):
#     return  m.y2[i, t]*m.sp[i, t] <= 1e-1
#
# @m.Constraint(m.I, m.t)
# def compslack2(m, i, t):
#     return m.y[i, t]*m.sn[i, t] <= 1e-1

@m.ConstraintList()
def ICs(m):
    for i in m.I:
        yield m.L[i,0] == 0.0001
#
# @m.Constraint(m.I, m.t)
# def _bigM1(m, i, t):
#     if i < Ntank:
#         return -m.M1*(1 - m.y[i, t]) <= m.L[i+1, t] - m.H[i+1]
#     else:
#         return Constraint.Skip
#
# @m.Constraint(m.I, m.t)
# def _bigM2(m, i, t):
#     if i < Ntank:
#         return m.L[i+1, t] - m.H[i+1] <= m.M2*(1 - m.y2[i, t])
#     else:
#         return Constraint.Skip

discretizer = TransformationFactory('dae.collocation')
discretizer.apply_to(m, nfe=20, ncp=1)
# discretizer.reduce_collocation_points(m, var=m.w,ncp=1,contset=m.t)
# add rate of change constraints to valve opening proble

@m.ConstraintList()
def RoC(m):
    t = 0
    for tplus in m.t:
        if tplus > 0:
            for i in m.I:
                yield (m.w[i, tplus] - m.w[i,t])**2 <= 0.04
            yield (m.w0[tplus] -m.w0[t])**2 <= 0.04
            t = tplus
#
m.obj_var = Var(initialize=0,within=NonNegativeReals)

@m.Constraint()
def _obj_var(m):
    return m.obj_var == sum(sum((0.75-m.L[i,t])**2 for t in m.t) for i in m.I)

m.obj = Objective(sense=minimize, expr=( m.obj_var  \
                                         + sum(sum(1*m.y2[i,t]*m.sp[i,t] + 1*m.y[i, t]*m.sn[i, t] for t in m.t) for i in range(1,Ntank))
                                                    ))

if __name__ == "__main__":
    solver = SolverFactory('baron')
    solver.options["maxtime"] = 43200
    # solver.options["ma27_pivtol"] = 1e-10
    # solver.options["tol"] = 1e-9

    results = solver.solve(m, tee=True, keepfiles=True)
    #logfile=(str("~/bar.log")))
    print("time: %0.4f\n" % results['Solver'][0]['Time'])
    m.obj_var.display()
    plot_tanks(m)
