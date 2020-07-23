from contextlib import contextmanager
from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dw.const.types import Connection
from dw.const import types

#---------------------------------------------------------------
# DO NOT CHANGE MANUALLY
engine = None
_make_sess = None

def init(conn: Union[Connection, str], echo=True):
    ''' Call only one time '''
    global engine, _make_sess
    
    if engine is None:
        if type(conn) is str:
            conn = types.connection(conn) # type: ignore
        conn_str = 'postgresql://{}:{}@{}:{}/{}'.format(*conn)
        engine = create_engine(conn_str, echo=echo)
    if _make_sess is None:
        _make_sess = sessionmaker(bind=engine)

@contextmanager
def session():
    '''Provide a transactional scope around a series of operations.'''
    assert _make_sess is not None, 'orm.init first.'

    session = _make_sess()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
