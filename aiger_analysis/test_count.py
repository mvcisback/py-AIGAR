from uuid import uuid1

from aiger import hypothesis as aigh
from aigerbv.expr import atom
from hypothesis import given, settings, unlimited
import aiger
import hypothesis.strategies as st

from aiger_analysis import count


@given(aigh.Circuits)
def test_count_smoke(circ):
    circ = circ.unroll(3)
    assert count.count(circ, output=list(circ.outputs)[0]) >= 0


@settings(max_examples=20, timeout=unlimited)
@given(aigh.Circuits, aigh.Circuits)
def test_count_and(circ1, circ2):
    # Remove Latches.
    circ1, circ2 = circ1.unroll(1), circ2.unroll(1)

    # Make names disjoint.
    circ1 = circ1['i', {name: str(uuid1()) for name in circ1.inputs}]
    circ2 = circ2['i', {name: str(uuid1()) for name in circ2.inputs}]

    # Select outputs.
    out1, *_ = circ1.outputs
    out2, *_ = circ2.outputs

    # And outputs.
    out3 = str(uuid1())
    circ3 = (circ1 | circ2) >> aiger.and_gate([out1, out2], out3)

    # Property to check.
    count1 = count.count(circ1, out1)
    count2 = count.count(circ2, out2)
    count3 = count.count(circ3, out3)

    assert count1 * count2 == count3


@settings(max_examples=20, timeout=unlimited)
@given(st.integers(-8, 7))
def test_count_le(i):
    expr = atom(4, 'x') < atom(4, i)
    assert count.count(expr.aigbv.aig) == i + 8

