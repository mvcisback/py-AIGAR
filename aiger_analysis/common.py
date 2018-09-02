from collections import defaultdict

import funcy as fn
from aiger import AIG, BoolExpr
from aigerbv.aigbv import AIGBV
from aigerbv.expr import SignedBVExpr, UnsignedBVExpr
from toposort import toposort


def _dependency_graph(nodes):
    queue, deps, visited = list(nodes), defaultdict(set), set()
    while queue:
        node = queue.pop()
        if node in visited:
            continue
        else:
            visited.add(node)

        children = node.children
        queue.extend(children)
        deps[node].update(children)

    return deps


def eval_order(circ):
    return fn.lcat(toposort(_dependency_graph(circ.cones | circ.latch_cones)))


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
