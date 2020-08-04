from typing import Union

from hypothesis import given
from hypothesis import strategies as st

from dw.util import fp


@given(st.lists(st.integers()))
def test_plus_int(xs):
    expect = 0
    for x in xs:
        expect = expect + x
    assert fp.plus(*xs) == expect

@st.composite
def gen(draw):
    val = draw(st.from_type(Union[int, str])) # type: ignore
    num = draw(st.integers(min_value=0, max_value=100))
    return [val] * num
@given(gen())
def test_equal(xs):
    assert fp.equal(*xs)

@given(gen().filter(lambda xs: len(xs) >= 2))
def test_curried_equal(xs):
    assert fp.equal(xs[0])(*xs[1:])
'''
@given(st.lists(gen(), min_size=2))
def test_curried_equal(xs):
    assert fp.equal(xs[0])(xs[1:])
'''
