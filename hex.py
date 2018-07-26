# heat exchanger with phase transition model

from pyomo.environ import *
from pyomo.dae import *
from matplotlib import pyplot as plt

nfe = 40
L = 20.0
delx = L/nfe
m = ConcreteModel()
m.x = ContinuousSet(bounds=(0,L))
m.T = Var(m.x)
m.dTdx = DerivativeVar(m.T)



m.Twall = Param(initialize=650) # K

m.rho = Param(initialize=1000) # kg/m3
m.Cp = Param(initialize=4.186) # kJ/kg/K
m.pi = Param(initialize=3.14159)
m.D = Param(initialize=0.10) # m ~ 50mm tube diameter
m.Tb = Param(initialize = 310) # degrees C -- assuming we are at 100 bar
m.v = Param(initialize=1) # m/s : velocity of water flowing in pipe

m.mdot = Param(initialize=m.rho*m.pi*m.D**2/4*m.v) # kg/s
# m.mdot = Var(within=NonNegativeReals, bounds=(5,10))

# approximate HT coefficients from internet sources - need better values
m.hL = Param(initialize=1.250) #kW/m2/K     liquid water HT coefficient
m.hV = Param(initialize=0.500) # kW/m2/K    dry steam HT coefficient
m.hB = Param(initialize=20.000) # kW/m2/K   flow boiling HT coefficient

m.HV = Param(initialize=40.68)  #kJ/mol
m.MW = Param(initialize=0.01802)  #kg/mol
# m.latent_total = Param(initialize=m.rho*m.pi*m.D**2/4*delx*m.HV/m.MW)
m.latent_total = Param(initialize=m.mdot*m.HV/m.MW)
m.latent_i = Var(m.x, initialize=0)


m.y1 = Var(m.x, within=Reals, bounds=(0,1))
m.y2 = Var(m.x, within=Reals, bounds=(0,1))
m.y3 = Var(m.x, within=Reals, bounds=(0,1))
m.sp1 = Var(m.x, within=Reals, bounds=(0,50))
m.sn1 = Var(m.x, within=Reals, bounds=(0,30))
m.sp2 = Var(m.x, within=Reals, bounds=(0,20000))
m.sn2 = Var(m.x, within=Reals, bounds=(0,20000))

@m.Constraint()
def _T0(m):
    return 290 <= m.T[0] <= 290

@m.Constraint(m.x)
def _Tdot(m, x):
    return m.dTdx[x] == m.hL*m.pi*m.D*(m.Twall - m.T[x])/(m.mdot*m.Cp)*m.y1[x] + \
                        0*m.y2[x] + m.hV*m.pi*m.D*(m.Twall - m.T[x])/(m.mdot*m.Cp)*m.y3[x]
@m.Constraint(m.x)
def _ysum(m, x):
    return m.y1[x] + m.y2[x] + m.y3[x] == 1

@m.Constraint(m.x)
def _slacks1(m, x):
    return m.sp1[x] - m.sn1[x] == m.T[x] - m.Tb

# @m.Constraint(m.x)
# def _cc1(m, x):
#     return m.y1[x]*m.sp1[x] <= 0.001
#
# @m.Constraint(m.x)
# def _cc2(m, x):
#     return m.y3[x]*m.sn1[x] <= 0.001

# @m.Constraint(m.x)
# def _cc0(m, x):
#     return m.sn1[x]*m.sp1[x] <= 0.001

# transition (boiling)

# while the integrated enthalpy is less than the total needed to vaporize an element,
# sn2 = 0 and sp2 > 0
@m.Constraint(m.x)
def _slacks2(m, x):
    return m.sp2[x] - m.sn2[x] == m.latent_total - m.latent_i[x]
#
# # while T == Tb, y2 should be active
# @m.Constraint(m.x)
# def _cc3(m, x):
#     return  (m.sp1[x] + m.sn1[x])*m.y2[x] <= 0.001

# #while sn2 == 0, meaning integrated enthalpy is less than total, y2 should be active
# @m.Constraint(m.x)
# def _cc4(m, x):
#     return m.sn2[x]*m.y2[x] <= 0.001

# # # # # once sn2 > 0 and sp2 == 0, y3 can be turned on
# @m.Constraint(m.x)
# def _cc5(m, x):
#     return m.sp2[x]*m.y3[x] <= 0.001



discretizer = TransformationFactory('dae.finite_difference')
discretizer.apply_to(m, nfe=nfe, scheme='BACKWARD')


# integral of heat transfer to each element during boiling process = sum over elements
# of a constant heat transfer amount - integration continues while y2 == 1

@m.ConstraintList()
def _latent_i(m):
    for x in m.x:
        if x == 0:
            yield m.latent_i[x] == 0
        else:
            yield m.latent_i[x] == m.latent_i[xprev] + m.hB*m.pi*m.D*(m.Twall - m.Tb)*delx*m.y2[x]
        xprev = x



# m.obj = Objective(sense=maximize, expr= m.T[20])

m.obj = Objective(sense=minimize, expr=  sum( 10000*m.y3[x]*m.sn1[x] + 10000*m.y1[x]*m.sp1[x]  \
                                           +    1*m.sn2[x]*m.y2[x] + 1*m.sp2[x]*m.y3[x] \
                                              +  10000*(m.sp1[x] + m.sn1[x])*m.y2[x] \
                                                # + 100*m.sp1[x]*m.sn1[x] \
                                                - m.T[L] \
                                                for x in m.x))

solver = SolverFactory('ipopt')
solver.options['tol'] = 1e-6
solver.options['ma27_pivtol'] = 1e-10
solver.options['max_iter'] = 3000
results = solver.solve(m, tee=True)
print(m.T[20].value)

T = []
y1 = []
y2 = []
y3 = []
x = []
for i in m.x:
    T.append(m.T[i].value)
    y1.append(m.y1[i].value)
    y2.append(m.y2[i].value)
    y3.append(m.y3[i].value)
    x.append(m.latent_i[i].value/m.latent_total.value)

plt.figure()
plt.subplot(221)
plt.plot(m.x, T, label='T')
plt.legend()
plt.xlabel('m')
plt.subplot(222)
plt.plot(m.x, x, label='x_vap')
plt.xlabel('m')
plt.legend()
plt.subplot(223)
plt.plot(m.x, y1, label='y1')
plt.plot(m.x, y2, label='y2')
plt.plot(m.x, y3, label='y3')
plt.legend()
plt.xlabel('m')
plt.ion()
plt.show()
