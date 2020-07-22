import pytest

from dw.const import types
from dw.db import orm
from dw.db import query as Q


def test_tmp(conn):
    if conn is None: pytest.skip()
    orm.engine = None
    orm.sess_factory = None
    with pytest.raises(AssertionError):
        Q.CREATE_TABLES()
    with pytest.raises(AssertionError):
        Q.DROP_ALL()
        
    orm.init(types.connection(conn))
    Q.CREATE_TABLES()
    Q.DROP_ALL()
    
def test_inint_conn_str(conn):
    if conn is None: pytest.skip()
    orm.init(conn)
    Q.CREATE_TABLES()
    Q.DROP_ALL()

