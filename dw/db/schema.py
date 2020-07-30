from enum import Enum
from uuid import uuid4
from pprint import pformat
from pathlib import Path

from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql as pg

from dw.const import types
from dw.util import fp

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
# https://stackoverflow.com/a/54034230
def keyvalgen(obj):
    """ Generate attr name/val pairs, filtering out SQLA attrs."""
    excl = ('_sa_adapter', '_sa_instance_state')
    for k, v in vars(obj).items():
        if not k.startswith('_') and not any(hasattr(v, a) for a in excl):
            yield k, v
class ReprHelper:
    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in keyvalgen(self))
        return f"{self.__class__.__name__}<{params}>"
    
Base = declarative_base(cls=ReprHelper)

#===============================================================
'''
data는 서로 관계를 가질 수 있는 정보의 단위이다.
named_dat_rel 은 이름 붙여진 데이터 사이의 관계이다.
dataset은 named_dat_rel 3개로 이루어진다.
'''

class data(Base):
    __tablename__ = 'data'
    uuid = Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid4)
    type = Column(String)

    def __init__(self, nt_obj):
        super(data, self).__init__(**nt_dic(nt_obj)) # type: ignore
    value = None # not column, just conformance to types.data

class file(Base):
    __tablename__ = 'file'
    uuid = Column(pg.UUID(as_uuid=True), ForeignKey('data.uuid'))
    path = Column(String, primary_key=True, nullable=False)
    type = Column(String) # extension
    md5 = Column(pg.BYTEA)
    #data = relationship('user', backref=backref('user'))
    #type = Column(String)
    
class source(Base):
    __tablename__ = 'source'
    uuid = Column(pg.UUID(as_uuid=True), ForeignKey('data.uuid'),
                  primary_key=True)
    name = Column(String, primary_key=True, nullable=False)

class data_relation(Base):
    __tablename__ = 'data_relation'
    aid = Column(pg.UUID(as_uuid=True), ForeignKey('data.uuid'),
                 primary_key=True)
    bid = Column(pg.UUID(as_uuid=True), ForeignKey('data.uuid'),
                 primary_key=True)
    type = Column(String, nullable=False) # extension
    
def only_one_rel_rowseq(ids, type):
    return (data_relation(aid=id, bid=id, type=type) for id in ids)

class map_data_rel2rel_chunk(Base):
    __tablename__ = 'map_data_rel2rel_chunk'
    
    name = Column(String, primary_key=True)
    revision = Column(Integer, primary_key=True)
    size = Column(Integer, primary_key=True)
    
    inp = Column(pg.UUID(as_uuid=True), primary_key=True)
    out = Column(pg.UUID(as_uuid=True), primary_key=True)

    ForeignKeyConstraint(['inp',          'out'         ],
                         ['data_relation.aid', 'data_relation.bid'])
    
def only_inp_chunk_rowseq(name, revision, ids):
    ''' 
    Generate row sequence of only input data relation chunk. 
    ex) dataset for cnet. it has only images.
    '''
    return (
        map_data_rel2rel_chunk(
            name=name, revision=revision, size=len(ids),
            inp=id, out=id
        ) for id in ids
    )

#---------------------------------------------------------------
class help:
    ''' namespace for helper functions '''
    only_one_rel_rowseq = only_one_rel_rowseq
    only_inp_chunk_rowseq = only_inp_chunk_rowseq

def is_valid_column_name(name):
    ''' from inspection of dir(table_classes) '''
    return name not in {'metadata',
                        '_sa_class_manager',
                        '_decl_class_registry'}

#---------------------------------------------------------------
def generate_names_file(out_path=Path('dw/db/names.py')):
    # locals -> classes
    classes = fp.lfilter(
        lambda x: hasattr(x, '__tablename__'),
        globals().values())
    
    # classes -> code
    all_nameseq = fp.concat(
        (cls.__name__ for cls in classes),
        fp.mapcat(
            lambda cls: fp.attr_names(
                cls, fp.every_pred(fp.is_public_name,
                                   is_valid_column_name)),
                classes
        ))
    names = sorted(set(all_nameseq))
    code = '\n'.join([
        "'''",
        "Before import this, call schema.generate_name_file()",
        "Or, import schema first.",
        "This is auto-generated file. DO NOT MODIFY!",
        "'''",
        *("{} = '{}'".format(n,n) for n in names)
    ])
    
    # code -> file
    old_code =(out_path.read_text() if out_path.exists()
               else None)
    if code != old_code:
        with open(out_path, 'w') as f:
            f.write(code)
        print('dw/db/names.py updated!')

generate_names_file()
