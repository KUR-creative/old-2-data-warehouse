from hypothesis import given
from hypothesis import strategies as st

from dw.util.etc_utils import partition

@st.composite
def mul_part_parts_gen(draw):
    part = draw(st.integers(min_value=1, max_value=1000))
    mul = draw(st.integers(min_value=1, max_value=1000))
    parts = mul * part
    return mul, part, parts
                
@given(mul_part_parts_gen())
def test_partition(gen):
    mul, part, parts = gen
    intervals = partition(parts, part)
    assert len(intervals) == mul
    for a,b in intervals:
        assert b - a == part
        assert a % part == 0
