# dynamic tank level mpec - 3 tanks, 4 total flows and control valves
# MPCC formulation

from pyomo.environ import *
from pyomo.dae import *
from pyomo.gdp import Disjunct, Disjunction
from matplotlib import pyplot as plt

Ntank = 3
m = ConcreteModel()
m.I = RangeSet(Ntank)
m.t = ContinuousSet(bounds=[0,60])

m.L = Var(m.I, m.t, within=NonNegativeReals, initialize=0.75, bounds=(0, 1))
m.delL = Var(m.I, m.t, bounds=(-1, 1))
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

    return m.F[i, t] == m.w[i, t]*m.k[i]*sqrt(m.delL[i, t]+1e-4)

@m.Constraint(m.t)
def _F0(m, t):
    return m.F0[t] == m.k0*m.w0[t]


@m.ConstraintList()
def ICs(m):
    for i in m.I:
        yield m.L[i,0] == 0

# fix the value of delL in the Nth tank since this value
# is not dependent on a next tank (there is none)

@m.Constraint(m.t)
def delL_N(m, t):
    return m.delL[Ntank, t] == m.L[Ntank, t]


discretizer = TransformationFactory('dae.collocation')
discretizer.apply_to(m, nfe=20, ncp=1)



m.BigM = Suffix(direction=Suffix.LOCAL)
m.D1 = Disjunct(m.I, m.t)   # case where level in next tank is below inlet height
for t in m.t:
    for i in range(1,Ntank):
        disj = m.D1[i, t]
        disj.low_level = Constraint(expr=m.L[i+1, t] <= m.H[i+1])
        disj.low_dynamics = Constraint(expr=m.delL[i, t] == m.L[i, t])
        m.BigM[disj.low_level] = 0.6


m.D2 = Disjunct(m.I, m.t)   # case where level in next tank is at or above inlet height
for t in m.t:
    for i in range(1, Ntank):
        disj = m.D2[i, t]
        disj.high_level = Constraint(expr=m.L[i+1, t] >= m.H[i+1])
        disj.high_dynamics = Constraint(expr=m.delL[i, t] == m.L[i, t] - (m.L[i+1, t] - m.H[i+1]))
        m.BigM[disj.high_level] = 0.3

def _disjunction_rule(m, i, t):
    return [m.D1[i, t], m.D2[i, t]]
m.djcn = Disjunction(m.I, m.t, rule=_disjunction_rule)

# add rate of change constraints to valve opening problem

@m.ConstraintList()
def RoC(m):
    t = 0
    for tplus in m.t:
        if tplus > 0:
            for i in m.I:
                yield (m.w[i, tplus] - m.w[i,t])**2 <= 0.04
            yield (m.w0[tplus] -m.w0[t])**2 <= 0.04
            t = tplus


m.obj = Objective(sense=minimize, expr=sum(sum((0.75-m.L[i,t])**2 for t in m.t) for i in m.I))


TransformationFactory('gdp.bigm').apply_to(m)

results = SolverFactory('gdpopt').solve(m)

print("time: %0.4f\n" % results['Solver'][0]['Time'])

m.obj.display()

######### PLOTS ##########

l1 = []
l2 = []
l3 = []
l4 = []
l5 = []

F1 = []
F2 = []
F3 = []
F4 = []
F5 = []
F0 = []
w1 = []
w2 = []
w3 = []
w4 = []
w5 = []
w0 = []

y1_1 = []
y2_1 = []
sp_1 = []
sn_1 = []
y1_2 = []
y2_2 = []
sp_2 = []
sn_2 = []
y1_3 = []
y2_3 = []
sp_3 = []
sn_3 = []
y1_4 = []
y2_4 = []
y1_5 = []
y2_5 = []

for t in m.t:

    l1.append(m.L[1,t].value)
    l2.append(m.L[2,t].value)
    l3.append(m.L[3,t].value)

    F0.append(m.F0[t].value)
    F1.append(m.F[1,t].value)
    F2.append(m.F[2,t].value)
    F3.append(m.F[3,t].value)

    w0.append(m.w0[t].value)
    w1.append(m.w[1,t].value)
    w2.append(m.w[2,t].value)
    w3.append(m.w[3,t].value)

    y1_1.append(m.y1[1,t].value)
    y2_1.append(m.y2[1,t].value)
    y1_2.append(m.y1[2,t].value)
    y2_2.append(m.y2[2,t].value)
    y1_3.append(m.y1[3,t].value)
    y2_3.append(m.y2[3,t].value)
    if Ntank > 3:
        y1_4.append(m.y1[4,t].value)
        y2_4.append(m.y2[4,t].value)
        y1_5.append(m.y1[5,t].value)
        y2_5.append(m.y2[5,t].value)
        w4.append(m.w[4,t].value)
        w5.append(m.w[5,t].value)
        F4.append(m.F[4,t].value)
        F5.append(m.F[5,t].value)
        l4.append(m.L[4,t].value)
        l5.append(m.L[5,t].value)

plt.subplot(221)

plt.plot(m.t, l1, label='l1')
plt.plot(m.t, l2, label='l2')
plt.plot(m.t, l3, label='l3')
if Ntank > 3:
    plt.plot(m.t, l4, label='l4')
    plt.plot(m.t, l5, label='l5')
plt.legend()
plt.subplot(222)
plt.plot(m.t, F0, label='F0')
plt.plot(m.t, F1, label='F1')
plt.plot(m.t, F2, label='F2')
plt.plot(m.t, F3, label='F3')
if Ntank > 3:
    plt.plot(m.t, F4, label='F4')
    plt.plot(m.t, F5, label='F5')
plt.legend()
plt.subplot(223)
plt.plot(m.t, w0, label='w0')
plt.plot(m.t, w1, label='w1')
plt.plot(m.t, w2, label='w2')
plt.plot(m.t, w3, label='w3')
if Ntank > 3:
    plt.plot(m.t, w4, label='w4')
    plt.plot(m.t, w5, label='w5')
plt.legend()
plt.subplot(224)
plt.plot(m.t, y2_1, label='y2_1')
plt.plot(m.t, y1_1, label='y1_1')
plt.plot(m.t, y2_2, label='y2_2')
plt.plot(m.t, y1_2, label='y1_2')
plt.plot(m.t, y2_3, label='y2_3')
plt.plot(m.t, y1_3, label='y1_3')
if Ntank > 3:
    plt.plot(m.t, y2_4, label='y2_4')
    plt.plot(m.t, y1_4, label='y1_4')
    plt.plot(m.t, y2_5, label='y2_5')
    plt.plot(m.t, y1_5, label='y1_5')
plt.legend()

plt.ion()
plt.show()
