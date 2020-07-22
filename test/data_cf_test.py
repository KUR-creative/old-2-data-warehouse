from uuid import uuid4

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
import funcy as F

from dw.db import orm
from dw.db import schema as S
from dw.db import query as Q
from dw.const import types
from dw.api import put

@st.composite
def rand_datum(draw):
    return types.Data(
        uuid4(), draw(st.sampled_from(types.DataType)))
@given(datums=st.lists(rand_datum()))
@settings(max_examples=20)
def test_insert(datums, conn):
    if conn is None: pytest.skip()
    # insert generated canonical forms of data
    orm.init(types.connection(conn))
    Q.CREATE_TABLES()
    with orm.session() as sess:
        sess.add_all(F.lmap(S.Data, datums))
        # Be Careful!! sess must be in ctx manager!!!
        for inp, out in zip(datums, sess.query(S.Data).all()):
            assert inp.uuid == out.uuid
    Q.DROP_ALL()
