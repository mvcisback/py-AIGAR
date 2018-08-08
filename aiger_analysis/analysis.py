"""
This module provides basic operations on aig circuits, such as
satisfiability queries, model counting, and quantifier elimination.
"""

import funcy as fn

import aiger
import aigerbv
from pysat.formula import CNF
from pysat.solvers import Lingeling
import aiger_analysis.common as cmn


def _tseitin(e):
    aig = cmn.extract_aig(e)

    node_map = dict(aig.node_map)
    output = node_map[fn.first(aig.outputs)]
    clauses = []
    symbol_table = {}  # maps input names to tseitin variables
    gates = {}         # maps gates to tseitin variables
    max_var = 0

    def fresh_var():
        nonlocal max_var
        max_var += 1
        return max_var

    true_var = None  # Reserved variable name for constant True

    for gate in fn.cat(aig._eval_order):
        if isinstance(gate, aiger.aig.ConstFalse):
            if true_var is None:
                true_var = fresh_var()
                clauses.append([true_var])
            gates[gate] = - true_var
        elif isinstance(gate, aiger.aig.Inverter):
            gates[gate] = - gates[gate.input]
        elif isinstance(gate, aiger.aig.Input):
            if gate.name not in symbol_table:
                symbol_table[gate.name] = fresh_var()
                gates[gate] = symbol_table[gate.name]
        elif isinstance(gate, aiger.aig.AndGate):
            gates[gate] = fresh_var()
            clauses.append([-gates[gate.left], -gates[gate.right],  gates[gate]])  # noqa
            clauses.append([ gates[gate.left],                     -gates[gate]])  # noqa
            clauses.append([                    gates[gate.right], -gates[gate]])  # noqa

    clauses.append([gates[output]])

    return clauses, symbol_table, max_var


def is_satisfiable(e):
    formula = CNF()
    clauses, _, _ = _tseitin(e)
    for clause in clauses:
        formula.append(clause)
    with Lingeling(bootstrap_with=formula.clauses) as ling:
        return ling.solve()


def is_valid(e):
    aig = cmn.extract_aig(e)
    aig = aig >> aiger.bit_flipper(inputs=aig.outputs)  # negate
    return not is_satisfiable(aig)


def is_equal(e1, e2):
    if isinstance(e1, aiger.AIG):
        assert len(e1.outputs) is 1
        e1 = aiger.BoolExpr(e1)
    if isinstance(e2, aiger.AIG):
        assert len(e2.outputs) is 1
        e2 = aiger.BoolExpr(e2)
    is_valid(e1 == e2)
