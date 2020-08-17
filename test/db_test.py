from uuid import uuid4

import pytest
import sqlalchemy as sa

from dw.const import types
from dw.db import orm
from dw.db import query as Q
from dw.db import schema as S
from dw.util.test_utils import env_val, skipif_none


def test_init_with_conn_obj(conn):
    conn = env_val(conn=conn)
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
    
def test_init_with_conn_str(conn: str):
    conn = env_val(conn=conn)
    skipif_none(conn)
    
    orm.engine = None
    orm._make_sess = None
    
    orm.init(conn)
    Q.CREATE_TABLES()
    Q.DROP_ALL()

#---------------------------------------------------------------
def test_image_constraints(conn):
    conn = env_val(conn=conn)
    skipif_none(conn)
    
    orm.init(conn)
    Q.CREATE_TABLES()

    uuid = uuid4()
    with orm.session() as sess:
        sess.add(S.data(uuid=uuid, type='test'))
        
    with pytest.raises(sa.exc.IntegrityError):
        with orm.session() as sess:
            sess.add(S.image(uuid=uuid, x=-1, y=0, w=10, h=20,
                             full_w=40, full_h=100))
    with pytest.raises(sa.exc.IntegrityError):
        with orm.session() as sess:
            sess.add(S.image(uuid=uuid, x=0, y=0, w=100, h=20,
                             full_w=40, full_h=100))
    Q.DROP_ALL()
