import aiger_analysis as aa
from aiger import atom


x, y = atom('x'), atom('y')
expr = x & y | y & atom(True)


def test_abc():
    assert aa.is_equal(expr, aa.simplify(expr))
