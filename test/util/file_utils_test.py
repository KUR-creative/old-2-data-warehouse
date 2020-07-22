from string import ascii_letters, digits, punctuation
from pathlib import Path
from random import randint

from hypothesis import given
from hypothesis import strategies as st

from dw.util import file_utils as fu

VALID_PATH_CHARS =(ascii_letters + digits +
                   ''.join(set(punctuation) - set('\\/.')))
@st.composite
def valid_at_pathstr(draw):
    parts = draw(st.lists(
        st.text(VALID_PATH_CHARS, min_size=1),
        min_size=2,
    ))
    at = randint(-len(parts), len(parts)-1)
    #at = randint(0, len(parts)-1)
    return at, '/'.join(parts)

@given(valid_at_pathstr())
def test_select_with_string_path(at_path):
    at, path = at_path
    
    parts = Path(path).parts
    i = at + len(parts) if at < 0 else at
    assert path == str(Path(
        *parts[:i], fu.select(at, path), *parts[i+1:]
    )), 'str path case'
    
    ppath = Path(path)
    assert ppath == Path(
        *parts[:i], fu.select(at, ppath), *parts[i+1:]
    ), 'Path path case'

    select_at = fu.select(at)
    ppath = Path(path)
    assert ppath == Path(
        *parts[:i], select_at(ppath), *parts[i+1:]
    ), 'Path path, curried select case'
    assert path == str(Path(
        *parts[:i], select_at(path), *parts[i+1:]
    )), 'str path, curried select case'
