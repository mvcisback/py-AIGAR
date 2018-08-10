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
        aig = e.aigbv.aig
    elif isinstance(e, BoolExpr) or isinstance(e, AIGBV):
        aig = e.aig
    else:
        aig = e
    assert isinstance(aig, AIG)
    assert len(aig.outputs) is 1
    assert len(aig.latches) == 0
    return aig
