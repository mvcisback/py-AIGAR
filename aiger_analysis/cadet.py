import os
from subprocess import PIPE, call
import tempfile
import functools as fn

import aiger
from aiger_analysis import is_satisfiable, is_valid
import aiger_analysis.common as cmn


def _call_cadet_on_file(file_name,
                        result_file,
                        var_prefix,
                        projection=False,
                        use_cegar=False):
    assert file_name.endswith('.aag')
    assert result_file.endswith('.aag')

    ret = call(['./../../../cadet/dev/cadet',
                 '--sat_by_qbf']
                + (['-e', result_file] if projection else [])
                + (['--cegar'] if use_cegar else [])
                + ['--aiger_controllable_inputs', var_prefix]
                + ['-v', '1']
                + [file_name] # noqa
                , stdout=PIPE  # comment this line to see more output
               )
    assert not projection or ret == 10
    if projection:
        ret = aiger.parser.load(result_file)
    return ret


def _call_cadet(aig, existentials, projection=False):
    # prefix variables; make sure prefix does not exist elsewhere
    prefix = 'FbGiGjE7ol_'  # randomly generated
    assert all([not s.startswith(prefix) for s in aig.inputs])
    aig = aig['i', {v: prefix + v for v in existentials}]

    # create dir to hold all files for this call;
    # avoids confusion and guarantees deletion on exit
    with tempfile.TemporaryDirectory() as tmpdirname:
        # create input file
        aig_name = os.path.join(tmpdirname, 'input.aag')
        input_file = open(aig_name, "w+")
        input_file.write(str(aig))
        input_file.close()
        return _call_cadet_on_file(aig_name,
                                   os.path.join(tmpdirname, 'result.aag'),
                                   prefix,
                                   projection=projection)


def eliminate(e, variables):
    return _call_cadet(cmn.extract_aig(e), variables, projection=True)


def simplify_quantifier_prefix(quantifiers):
    seen_variables = set()
    simplified_q = []
    for q, variables in quantifiers:
        assert len(seen_variables & set(variables)) is 0
        seen_variables |= set(variables)
        if len(variables) == 0:
            continue
        else:
            if len(simplified_q) > 0 and simplified_q[-1][0] == q:
                (last_q, last_vars) = simplified_q[-1]
                simplified_q[-1] = (last_q, last_vars + variables)
            else:
                simplified_q.append((q, variables))
    return simplified_q


# accepts only closed formulas; i.e. all variables must be quantified
def is_true_QBF(e, quantifiers):
    quantifiers = simplify_quantifier_prefix(quantifiers)
    aig = cmn.extract_aig(e)
    assert sum(map(len, fn.pluck(1, quantifiers))) == len(aig.inputs)
    if len(quantifiers) is 1:  # solve with SAT
        if quantifiers[0][0] is 'a':
            return is_valid(aig)
        else:
            assert quantifiers[0][0] is 'e'
            return is_satisfiable(aig)
    elif len(quantifiers) is 2:  # 2QBF
        if quantifiers[0][0] is 'e':
            e = ~aiger.BoolExpr(aig)
            aig = e.aig
        return _call_cadet(aig, quantifiers[1][1]) == 10
    else:
        raise NotImplementedError('Cannot handle general QBF at the moment')
