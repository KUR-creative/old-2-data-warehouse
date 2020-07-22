from sqlalchemy.orm.session import close_all_sessions #type: ignore

from dw.db.schema import Base
from dw.db import orm

#---------------------------------------------------------------
# Commands without session
def CREATE_TABLES():
    assert orm.engine is not None, 'orm.init first.'
    Base.metadata.create_all(orm.engine)
    
# ** DANGER! **
def DROP_ALL():
    assert orm.engine is not None, 'orm.init first.'
    close_all_sessions() # need to close all
    Base.metadata.drop_all(orm.engine)
