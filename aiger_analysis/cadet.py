import os
from subprocess import PIPE, call  # noqa
import tempfile
import funcy as fn
from enum import Enum

import aiger
from aiger_analysis import is_satisfiable, is_valid
import aiger_analysis as aa
import aiger_analysis.common as cmn


class CadetCodes(Enum):
    QBF_IS_TRUE = 10
    QBF_IS_FALSE = 20
    QBF_IS_UNKNOWN = 30


def _call_cadet_on_file(file_name,
                        result_file,
                        var_prefix,
                        projection=False,
                        use_cegar=False,
                        verbose=False):
    assert file_name.endswith('.aag')
    assert result_file.endswith('.aag')

    cmd = ['cadet', '--sat_by_qbf']
    if projection:
        cmd += ['-e', result_file]
    if use_cegar:
        cmd += ['--cegar']
    cmd += ['--aiger_controllable_inputs', var_prefix]
    cmd += ['-v', '1']
    cmd += [file_name]

    ret = call(cmd) if verbose else call(cmd, stdout=PIPE)

    assert not projection or ret == CadetCodes.QBF_IS_TRUE.value
    if projection:
        ret = aiger.parser.load(result_file)
        ret = aa.abc.simplify(ret)
    return ret


def _call_cadet(aig,
                existentials,
                projection=False,
                use_cegar=True,
                verbose=False):
    # prefix variables; make sure prefix does not exist elsewhere
    prefix = 'FbGiGjE7ol_'  # randomly generated
    assert all([not s.startswith(prefix) for s in aig.inputs])
    aig = aig['i', {v: prefix + v for v in existentials}]

    # create dir to hold all files for this call;
    # avoids confusion and guarantees deletion on exit
    with tempfile.TemporaryDirectory() as tmpdirname:
        # create input file
        aig_name = os.path.join(tmpdirname, 'input.aag')
        aig.write(aig_name)
        return _call_cadet_on_file(aig_name,
                                   os.path.join(tmpdirname, 'result.aag'),
                                   prefix,
                                   projection=projection,
                                   use_cegar=use_cegar,
                                   verbose=verbose)


def eliminate(e, variables, verbose=False):
    result_aig = _call_cadet(cmn.extract_aig(e),
                             variables,
                             projection=True,
                             verbose=verbose)
    if type(e) is aiger.BoolExpr:
        return aiger.BoolExpr(result_aig)
    return result_aig


def simplify_quantifier_prefix(quantifiers):
    seen_variables = set()
    simplified_q = []
    for q, variables in quantifiers:
        variables = list(map(str, variables))
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
        true_return_code = CadetCodes.QBF_IS_TRUE.value
        if quantifiers[-1][0] is 'a':
            e = ~aiger.BoolExpr(aig)
            aig = e.aig
            true_return_code = CadetCodes.QBF_IS_FALSE.value
        return _call_cadet(aig, quantifiers[1][1]) == true_return_code
    else:
        raise NotImplementedError('Cannot handle general QBF at the moment')
