from aiger import AIG, BoolExpr
from aigerbv.aigbv import AIGBV
from aigerbv.expr import SignedBVExpr, UnsignedBVExpr


def extract_aig(e):
    assert isinstance(e, AIG) or \
           isinstance(e, BoolExpr) or \
           isinstance(e, AIGBV) or \
           isinstance(e, SignedBVExpr) or \
           isinstance(e, UnsignedBVExpr)
    if isinstance(e, SignedBVExpr) or isinstance(e, UnsignedBVExpr):
        e = e.aigbv
    if isinstance(e, BoolExpr) or isinstance(e, AIGBV):
        e = e.aig
    assert isinstance(e, AIG)
    assert len(e.outputs) is 1
    assert len(e.latches) == 0
    return e
