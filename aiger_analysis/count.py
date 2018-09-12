from aiger_analysis import bdd


def count(circ_or_expr, percent=False, output=None):
    f, *_ = bdd.to_bdd(circ_or_expr, output)
    n_inputs = len(circ_or_expr.inputs)
    num_models = f.count(n_inputs)
    return num_models / (2**n_inputs) if percent else num_models
