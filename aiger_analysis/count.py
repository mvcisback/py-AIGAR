import aiger
import funcy as fn
from parsimonious import Grammar, NodeVisitor

import aiger_analysis.common as cmn

try:
    from dd.cudd import BDD
except ImportError:
    from dd.autoref import BDD


def to_bdd(circ_or_expr, output=None):
    if isinstance(circ_or_expr, aiger.BoolExpr):
        circ, output = circ_or_expr.aig, circ_or_expr.output
    else:
        circ = circ_or_expr

    node_map = dict(circ.node_map)

    assert len(circ.latches) == 0
    if output is None:
        assert len(circ.outputs) == 1
        output = node_map[fn.first(circ.outputs)]
    else:
        output = node_map[output]  # By name instead.

    bdd = BDD()
    input_refs_to_var = {ref: f"x{i}" for i, ref in enumerate(circ.inputs)}
    bdd.declare(*input_refs_to_var.values())

    gate_nodes = {}
    for gate in cmn.eval_order(circ):
        if isinstance(gate, aiger.aig.ConstFalse):
            gate_nodes[gate] = bdd.add_expr('False')
        elif isinstance(gate, aiger.aig.Inverter):
            gate_nodes[gate] = ~gate_nodes[gate.input]
        elif isinstance(gate, aiger.aig.Input):
            gate_nodes[gate] = bdd.add_expr(input_refs_to_var[gate.name])
        elif isinstance(gate, aiger.aig.AndGate):
            gate_nodes[gate] = gate_nodes[gate.left] & gate_nodes[gate.right]

    relabels = {v: k for k, v in input_refs_to_var.items()}
    return gate_nodes[output], bdd, relabels


BDDEXPR_GRAMMAR = Grammar(u'''
bdd_expr = neg / ite / id / const
ite = "ite(" id ", " bdd_expr ", " bdd_expr ")"
neg = "(~ " bdd_expr ")"
id = ~r"[a-z\d]+"
const = "TRUE" / "FALSE"
''')


class BDDExprVisitor(NodeVisitor):
    def generic_visit(self, _, children):
        return children

    def visit_id(self, node, _):
        return aiger.atom(node.text)

    def visit_ite(self, _, children):
        return aiger.ite(children[1], children[3], children[5])

    def visit_neg(self, _, children):
        return ~children[1]

    def visit_bdd_expr(self, _, children):
        return children[0]

    def visit_const(self, node, _):
        return aiger.atom(node.text == "TRUE")


def _parse_bddexpr(ite_str: str):
    return BDDExprVisitor().visit(BDDEXPR_GRAMMAR.parse(ite_str))


def from_bdd(bdd_func):
    return _parse_bddexpr(bdd_func.to_expr())


def count(circ_or_expr, percent=False, output=None):
    f, *_ = to_bdd(circ_or_expr, output)
    n_inputs = len(circ_or_expr.inputs)
    num_models = f.count(n_inputs)
    return num_models / (2**n_inputs) if percent else num_models
