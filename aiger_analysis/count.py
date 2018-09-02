import aiger
import funcy as fn

import aiger_analysis.common as cmn

try:
    from dd.cudd import BDD
except ImportError:
    from dd.autoref import BDD


def to_bdd(circ, output):
    assert len(circ.outputs) == 1 or (output is not None)
    assert len(circ.latches) == 0

    node_map = dict(circ.node_map)

    if output is None:
        output = node_map[fn.first(circ.outputs)]
    else:
        output = node_map[output]  # By name instead.

    bdd = BDD()
    input_refs_to_var = {ref: f'x{i}' for i, ref in enumerate(circ.inputs)}
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

    return gate_nodes[output], bdd


def count(circ, percent=False, output=None):
    f, bdd = to_bdd(circ, output)
    n_inputs = len(circ.inputs)
    num_models = f.count(n_inputs)
    return num_models / (2**n_inputs) if percent else num_models
