
from bbMILP import BranchAndBound
import re
import copy
from copy import deepcopy
import math
from pyomo.environ import *
from plottanks import plot_tanks
# from pyomoMILP import m as pyomo_m

###
### KNAPSACK EXAMPLE
###



class MINLP(BranchAndBound):

    __slots__ = ('fixed', 'model', 'NLPsolver')

    def __init__(self, pyomo_m, sense):
        self.model = pyomo_m
        self.fixed = {}
        self.NLPsolver = SolverFactory('ipopt')
        self.NLPsolver.options["tol"] = 1e-9
        # self.NLPsolver.options["ma27_pivtol"] = 1e-10
        BranchAndBound.__init__(self, sense) # sense = -1 for maximization problem!


    def debug(self):
        print("LOCKED IN")
        print(self.locked_in)
        print("LOCKED OUT")
        print(self.locked_out)
        print("SOLUTION")
        print(self.solution)
        print("SOLUTION VALUE")
        print(self.solution_value)
        print("BOUND")
        print(self.bound)
        print("LAST")
        print(getattr(self,'last',None))


    def compute_bound(self):
        # fixed is a dict
        m_bound = self.model
        m_bound.y.unfix()
        m_bound.sn.unfix()
        m_bound.sp.unfix()

        for i in self.fixed.keys():
            m_bound.y[i].fix(self.fixed[i])

            tk = i[0]
            tm = i[1]

            # if self.fixed[i] == 0:
            #     m_bound.sp[tk, tm].fix(0.0)
            # elif self.fixed[i] == 1:
            #     m_bound.sn[tk, tm].fix(0.0)

            # if self.fixed[i] == 0:
            #     for tm2 in m_bound.t:
            #         if (tm2 < tm):
            #             m_bound.sp[tk, tm2].fix(0.0)
            #             m_bound.y[tk, tm2].fix(0.0)
            #
            # elif self.fixed[i] == 1:
            #     for tm2 in m_bound.t:
            #         if (tm2 > tm):
            #             m_bound.sn[tk, tm2].fix(0.0)
            #             m_bound.y[tk, tm2].fix(1.0)

        # print("IPOPT soln:")
        results = self.NLPsolver.solve(m_bound, keepfiles=False, tee=False)

        print("subproblem: %s" % str(results.solver.termination_condition))

        if str(results.solver.termination_condition) != 'optimal':
            # print("infeasible subproblem\n")
            self.bound = self.sense*float('Inf')
        else:
            self.bound = value(m_bound.obj)
            self.solution_value = value(m_bound.obj)
            self.solution = m_bound
        return self.bound



    def make_child(self, which_child):
        child = MINLP(self.model, self.sense)

        child.bound = self.bound
        child.fixed = copy.copy(self.fixed)

        for i in range(1, 5):
            for t in self.model.t:
                val = self.model.y[i,t].value

                if min(val - floor(val) , ceil(val) - val) >= 1e-6:

                    v1 = floor(val)
                    v2 = ceil(val)
                    tk = i
                    tm = t

                    break

        if which_child == 0:    # Down
            child.fixed[tk, tm] = v1
            print(child.fixed)
            # all of this is w.r.t. y -- if y = 0 --> y2 = 1,
            # --> need to enforce sp(i, t) == 0

        elif which_child == 1:
            child.fixed[tk, tm] = v2
            # if y = 1, need to enforce sn(i, t) == 0

        else:
            raise RuntimeError("Unknown child %d" % which_child)


        print("making child:")
        print("bound: %f" % child.bound)
        print(child.fixed)

        print("\n")

        return child

    def separate(self):
        return 2

    def terminal(self):
        """
        Return True if this is a terminal.
        """
        frac = 0
        # for i in subproblem.model.y:
        for i in range(1,5):
            for t in self.model.t:
                val = self.model.y[i,t].value
                if min(val - floor(val) , ceil(val) - val) >= 1e-6:    # tolerance on integrality violation
                    frac = 1
                    break
        #return math.isclose(self.solution_value, self.bound)    # TOLERANCE
        return frac == 0

    def get_solution(self):
        """
        Return solution if integer
        """

        frac = 0
        # for i in subproblem.model.y:
        for i in range(1, 5):
            for t in self.model.t:
                val = self.model.y[i,t].value
                if min(val - floor(val) , ceil(val) - val) >= 1e-6:    # tolerance on integrality violation
                    frac = 1

        if (frac > 0):
            return (None, None)
        return (self.solution_value, deepcopy(self.solution)    )

    def print_solution(self, solution):

        solution.display()




if __name__ == '__main__':
    from bbMILP import SerialBBSolver
    from tanks_mpcc import m
    problem = MINLP(m, 1)    # 1 to minimize, -1 to maximize
    solver = SerialBBSolver()
    value, solution = solver.solve(problem=problem)
    print("MINLP opt value: %f" % value)
    print("optimal integrated error: %f" % solution.obj_var.value)
    # problem.print_solution(solution)
    plot_tanks(solution)
