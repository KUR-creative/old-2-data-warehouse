from enum import Enum
from uuid import uuid4
from pprint import pformat

from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql as pg

from dw.const import types

#---------------------------------------------------------------
# NOTE: If it is useless to general case, remove it!
def nt_dic(nt_obj):
    ''' namedtuple obj to db dic ''' 
    dic = nt_obj._asdict()
    for k,v in dic.items():
        if isinstance(v, Enum):
            dic[k] = v.value
    return dic

#---------------------------------------------------------------
'''
data는 서로 관계를 가질 수 있는 정보의 단위이다.
named_dat_rel 은 이름 붙여진 데이터 사이의 관계이다.
dataset은 named_dat_rel 3개로 이루어진다.
'''

Base = declarative_base()

class data(Base):
    __tablename__ = 'data'
    uuid = Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid4)
    type = Column(String)

    def __init__(self, nt_obj):
        super(data, self).__init__(**nt_dic(nt_obj)) # type: ignore
    def __repr__(self):
        return "<data(uuid=%s, type=%s): value=%s>" % (
            self.uuid, self.type, pformat(self.value))
    
    value = None # not column, just conformance to types.data

class file(Base):
    __tablename__ = 'file'
    uuid = Column(pg.UUID(as_uuid=True), ForeignKey('data.uuid'), primary_key=True)
    path = Column(String, nullable=False)
    type = Column(String) # extension
    md5 = Column(pg.BYTEA)
    def __repr__(self):
        return "<file(uuid=%s, path=%s>" % (
            self.uuid, self.path)
    
    #data = relationship('user', backref=backref('user'))
    #type = Column(String)
