import pytest

from dw.const import types
from dw.db import orm
from dw.db import query as Q
from dw.util.test_utils import skipif_none


def test_init_with_conn_obj(conn):
    skipif_none(conn)
    orm.engine = None
    orm._make_sess = None
    with pytest.raises(AssertionError):
        Q.CREATE_TABLES()
    with pytest.raises(AssertionError):
        Q.DROP_ALL()
        
    orm.init(types.connection(conn))
    Q.CREATE_TABLES()
    Q.DROP_ALL()
    
def test_init_with_conn_str(conn):
    skipif_none(conn)
    
    orm.init(conn)
    Q.CREATE_TABLES()
    Q.DROP_ALL()

