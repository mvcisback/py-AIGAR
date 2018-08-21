#!/usr/bin/env python3

import sys
import argparse
from typing import NamedTuple

import aiger
from aiger import BoolExpr, atom
from aiger_analysis import eliminate, is_equal


def _cutlatches_and_rename(aig):
    if len(aig.latches) == 0:
        return aig
    aig, latch_names = aig.cutlatches(aig.latches)
    output_map = {new_name: [old_name]
                  for old_name, (new_name, _) in latch_names.items()}
    out_rename_aig = aiger.tee(output_map)
    input_map = {old_name: [new_name]
                 for old_name, (new_name, _) in latch_names.items()}
    in_rename_aig = aiger.tee(input_map)
    return in_rename_aig >> aig >> out_rename_aig


class Game(NamedTuple):
    aig: aiger.AIG

    @property
    def system(self):
        return [x for x in self.inputs if x.startswith('controllable_')]

    @property
    def environment(self):
        return [x for x in self.inputs if not x.startswith('controllable_')]

    @property
    def output(self):
        assert isinstance(self.aig, aiger.AIG)
        assert len(self.aig.outputs) is 0
        return list(self.aig.outputs)[0]

    @property
    def inputs(self):
        return self.aig.inputs

    def is_realizable(self, use_cegar=False):
        assert len(self.aig.outputs) is 1
        bad = atom(False)
        single_step = BoolExpr(_cutlatches_and_rename(self.aig) >>
                               aiger.sink(self.aig.latches))

        i = 0
        while True:
            i += 1
            print(f'Iteration {i}')

            miter = ~single_step & ~bad
            miter = eliminate(miter, self.system, verbose=True)
            next_bad = bad | eliminate(~miter, self.environment, verbose=True)

            zero_inputs = {x: False for x in next_bad.inputs}
            if next_bad(inputs=zero_inputs):
                print('Unrealizable')
                return False

            print('Fixed point check')
            if is_equal(bad, next_bad):
                print('Realizable')
                return True

            bad = next_bad


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="A safety game solver using repeated projections.")
    arg_parser.add_argument('--cegar', dest='cegar', action='store_true',
                            help="Support CADET' projection with CEGAR.")
    arg_parser.add_argument('input_file', action='store', nargs='?',
                            type=str,
                            help='Input file in extended AIGER format')
    args = arg_parser.parse_args()
    file_name = args.input_file
    if file_name is None:
        arg_parser.print_help(sys.stderr)
        quit(1)
    res = Game(aiger.load(file_name)).is_realizable(use_cegar=args.cegar)
    print(res)
