import aiger_analysis as aa
from aiger_analysis.cadet import simplify_quantifier_prefix
from aiger import atom

x, y = atom('x'), atom('y')
expr = x & y

# print(y)
# print(aa.eliminate(expr, ['x']))

def test_elim1():
    assert aa.is_equal(y, aa.eliminate(expr, ['x']))


def test_elim2():
    assert aa.is_equal(atom(True), aa.eliminate(x, ['x']))


def test_elim3():
    assert aa.is_valid(aa.eliminate(expr, ['x', 'y']))


def test_simplify_quantifier_prefix1():
    assert simplify_quantifier_prefix([('e', [])]) == []


def test_simplify_quantifier_prefix2():
    assert simplify_quantifier_prefix([('e', [1])]) == [('e', [1])]


def test_simplify_quantifier_prefix3():
    assert simplify_quantifier_prefix([('e', [1]), ('e', [2])]) == [('e', [1, 2])]


def test_simplify_quantifier_prefix4():
    assert simplify_quantifier_prefix([('e', [1]), ('a', []), ('e', [2])]) == [('e', [1, 2])]


def test_simplify_quantifier_prefix5():
    assert simplify_quantifier_prefix([('e', [1]), ('a', [2])]) == [('e', [1]), ('a', [2])]