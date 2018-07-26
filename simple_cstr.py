# simple cstr

from pyomo.dae import *
from pyomo.environ import *
from matplotlib import pyplot as plt

m = ConcreteModel()
m.t = ContinuousSet(bounds=[0,100])
m.Fb = Var(m.t)
m.Fa = Var(m.t)
m.Fa0 = Var(m.t, initialize=0.1, bounds=(0, 0.2))   # volumetric flow in
m.Ca = Var(m.t, bounds=(0,30))
m.Cb = Var(m.t, bounds=(0,30))
m.T = Var(m.t, bounds=(280,500))

m.dCadt = DerivativeVar(m.Ca)
m.dCbdt = DerivativeVar(m.Cb)
m.dTdt = DerivativeVar(m.T)

m.V = Param(initialize=1)
# m.T = Param(initialize=320)
m.E = Param(initialize=10000)
m.R = Param(initialize=8.314)
m.k = Param(initialize=1e1)
m.MWa = Param(initialize=30)
m.H = 10000
m.rho = 1000
m.cp = 30
m.Tc = 300
m.UA = Var(m.t, bounds=(600,1200))

# @m.Constraint(m.t)
# def Fa_in(m,t):
#     return m.Fa0 [t]== 0.3
#
# @m.Constraint(m.t)
# def _UA(m, t):
#     return m.UA[t] == 1000

@m.Constraint(m.t)
def flow_bal_a(m, t):
    return m.Fb[t] == m.Cb[t]*m.Fa0[t]      # since flow out =

@m.Constraint(m.t)
def flow_bal_b(m, t):
    return m.Fa[t] == m.Ca[t]*m.Fa0[t]


@m.Constraint(m.t)
def Ca_dot(m, t):
    return m.dCadt[t] == m.Fa0[t]*m.MWa/m.V - m.k*m.Ca[t]*exp(-m.E/(m.R*m.T[t])) \
                            - m.Fa[t]

@m.Constraint(m.t)
def Cb_dot(m, t):
    return m.dCbdt[t] == m.k*m.Ca[t]*exp(-m.E/(m.R*m.T[t])) - m.Fb[t]

@m.Constraint(m.t)
def T_dot(m,t):
    return m.rho*m.V*m.cp*m.dTdt[t] == m.H*m.Ca[t]*m.k*exp(-m.E/(m.R*m.T[t]))  \
                                        - m.UA[t]*(m.T[t] - m.Tc)

@m.ConstraintList()
def ICs(m):
    yield m.Ca[0] == 0
    yield m.Cb[0] == 0
    yield m.T[0] == 330

    # yield m.Fa[0] == 0
    # yield m.Fb[0] == 0

discretizer = TransformationFactory('dae.finite_difference')
discretizer.apply_to(m, nfe=60, scheme='BACKWARD')

@m.ConstraintList()
def roc(m):
    t = 0
    for tplus in m.t:
        if tplus > 0:
            yield (m.UA[tplus] - m.UA[t])**2 <= 100
            t = tplus

m.obj = Objective(sense=maximize, expr=sum(m.Fb[t] - (m.T[t]-330)**2  - (m.Cb[t]- 22)**2 for t in m.t))

solver = SolverFactory('ipopt')
solver.options["halt_on_ampl_error"] = "yes"
results = solver.solve(m, tee=True)


Ca = []
Cb = []
Fa = []
Fb = []
T = []
Fa0 = []
UA = []

for t in m.t:
    Ca.append(m.Ca[t].value)
    Cb.append(m.Cb[t].value)
    Fa.append(m.Fa[t].value)
    Fb.append(m.Fb[t].value)
    T.append(m.T[t].value)
    Fa0.append(m.Fa0[t].value)
    UA.append(m.UA[t].value)

plt.subplot(221)
plt.plot(m.t, Ca, label='Ca')
plt.plot(m.t, Cb, label='Cb')
plt.legend()
plt.subplot(222)
plt.plot(m.t, Fa, label='Fa')
plt.plot(m.t, Fb, label='Fb')
plt.plot(m.t, Fa0, label='FA0')
plt.legend()
plt.subplot(223)
plt.plot(m.t, T, label='T')
plt.legend()
plt.subplot(224)

plt.plot(m.t, UA, label='UA')
plt.legend()

plt.ion()
plt.show()
