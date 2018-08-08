import aiger_analysis as aa
from aiger import atom

x, y = atom('x'), atom('y')
expr = x & y


def test_elim1():
    aa.is_equal(y, aa.eliminate(expr, ['x']))


def test_elim2():
    aa.is_equal(atom(True), aa.eliminate(x, ['x']))


def test_elim3():
    aa.is_valid(aa.eliminate(expr, ['x', 'y']))
