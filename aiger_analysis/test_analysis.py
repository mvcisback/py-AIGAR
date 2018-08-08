from aiger import atom
from aiger_analysis import is_satisfiable

x, y = atom('x'), atom('y')
expr_sat = x | y
expr_unsat = expr_sat & ~ expr_sat


def test_satisfiable():
    assert is_satisfiable(expr_sat)


def test_satisfiable_2():
    assert is_satisfiable(atom(True))


def test_unsatisfiable():
    assert not is_satisfiable(expr_unsat)


def test_unsatisfiable_2():
    assert not is_satisfiable(atom(False))


def test_unsatisfiable_aig():
    assert not is_satisfiable(expr_unsat.aig)
