'''
table row classes and 'COMMIT' are canonical form for DB
with put.canonical_forms(..), we can use DB declaratively.
'''
from uuid import uuid4
from collections import namedtuple

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.sql import func
#from sqlalchemy import UniqueConstraint


#---------------------------------------------------------------
def keyvalgen(obj): # https://stackoverflow.com/a/54034230
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
class executed_command(Base):
    __tablename__ = 'executed_command'
    command = Column(String, nullable=False, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now(),
                       primary_key=True)
    git_hash = Column(String, nullable=False)
    note = Column(String)
    
#---------------------------------------------------------------
# Canonical Form for DB

COMMIT = 'COMMIT' # canonical form for session.commit(), const.

class data(Base):
    __tablename__ = 'data'
    uuid = Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid4)
    type = Column(String)

#---------------------------------------------------------------
class file(Base):
    __tablename__ = 'file'
    uuid = Column(pg.UUID(as_uuid=True), ForeignKey('data.uuid'))
    path = Column(String, primary_key=True, nullable=False)
    type = Column(String) # extension
    md5 = Column(pg.BYTEA)
    
class source(Base):
    __tablename__ = 'source'
    uuid = Column(pg.UUID(as_uuid=True), ForeignKey('data.uuid'),
                  primary_key=True)
    name = Column(String, primary_key=True, nullable=False)

class annotation(Base):
    __tablename__ = 'annotation'
    uuid = Column(pg.UUID(as_uuid=True), ForeignKey('data.uuid'),
                  primary_key=True)
    type = Column(String) # Annotation type
    group = Column(String) # Same type of anno, but different.
                           # Commonly used for class of data

class image(Base):
    __tablename__ = 'image'
    uuid = Column(pg.UUID(as_uuid=True), ForeignKey('data.uuid'),
                  primary_key=True)
    x = Column(Integer, CheckConstraint('0 <= x AND x < full_w'),
               primary_key=True)
    y = Column(Integer, CheckConstraint('0 <= y AND y < full_h'),
               primary_key=True)
    w = Column(Integer, CheckConstraint('0 <= w AND w <= full_w'),
               primary_key=True)
    h = Column(Integer, CheckConstraint('0 <= h AND h <= full_h'),
               primary_key=True)
    full_w = Column(Integer)
    full_h = Column(Integer)
    
        
    
#---------------------------------------------------------------
class named_relations(Base):
    __tablename__ = 'named_relations'
    name = Column(String, primary_key=True)
    revision = Column(Integer, primary_key=True)
    size = Column(Integer, primary_key=True)
    
class data_relation(Base):
    __tablename__ = 'data_relation'
    aid = Column(pg.UUID(as_uuid=True), ForeignKey('data.uuid'),
                 primary_key=True)
    bid = Column(pg.UUID(as_uuid=True), ForeignKey('data.uuid'),
                 primary_key=True)
    type = Column(String, nullable=False) # extension
    
def identity_data_rel_rowseq(ids, type):
    '''
    Identity relation used to express 'just input' dataset
    ex) dataset for cnet. it has only images.
    '''
    return (
        data_relation(aid=id, bid=id, type=type) for id in ids)

class named_relations2data_relation(Base):
    __tablename__ = 'named_relations2data_relation'
    
    name = Column(String, primary_key=True)
    revision = Column(Integer, primary_key=True)
    size = Column(Integer, primary_key=True)
    
    inp = Column(pg.UUID(as_uuid=True), primary_key=True)
    out = Column(pg.UUID(as_uuid=True), primary_key=True)
    
    __table_args__ = (
    ForeignKeyConstraint(
        ['name', 'revision', 'size'],
        ['named_relations.name',
         'named_relations.revision',
         'named_relations.size']),
    ForeignKeyConstraint(
        ['inp',               'out'              ],
        ['data_relation.aid', 'data_relation.bid']))
    
def named2rel_rowseq(name, revision, aid_bid_pairs):
    ''' Generate row sequence of namned relations '''
    return (
        named_relations2data_relation(
            name=name, revision=revision, size=len(aid_bid_pairs),
            inp=aid, out=bid
        ) for aid,bid in aid_bid_pairs
    )

def identity_named2rel_rowseq(name, revision, ids):
    ''' 
    Generate row sequence of namned relations(rel=identity)
    Identity relation means: inp = out
    
    Identity relation used to express 'just input' dataset
    ex) dataset for cnet. it has only images.
    '''
    return named2rel_rowseq(name, revision, list(zip(ids,ids)))

class dataset(Base):
    __tablename__ = 'dataset'
    
    train_name = Column(String, primary_key=True)
    train_revision = Column(Integer, primary_key=True)
    train_size = Column(Integer, primary_key=True)
    
    dev_name = Column(String, primary_key=True)
    dev_revision = Column(Integer, primary_key=True)
    dev_size = Column(Integer, primary_key=True)
    
    test_name = Column(String, primary_key=True)
    test_revision = Column(Integer, primary_key=True)
    test_size = Column(Integer, primary_key=True)
    
    __table_args__ = (
    ForeignKeyConstraint(
        ['train_name', 'train_revision', 'train_size'],
        ['named_relations.name',
         'named_relations.revision',
         'named_relations.size']),
    ForeignKeyConstraint(
        ['dev_name', 'dev_revision', 'dev_size'],
        ['named_relations.name',
         'named_relations.revision',
         'named_relations.size']),
    ForeignKeyConstraint(
        ['test_name', 'test_revision', 'test_size'],
        ['named_relations.name',
         'named_relations.revision',
         'named_relations.size']))

#===============================================================
class help:
    ''' namespace for helper functions '''
    identity_data_rel_rowseq = identity_data_rel_rowseq
    named2rel_rowseq = named2rel_rowseq
    identity_named2rel_rowseq = identity_named2rel_rowseq
    
    @staticmethod
    def ntup(row, type_name='_'):
        ''' Makes eager row. No more laziness! '''
        dic = row._asdict()
        return namedtuple(type_name, dic)(**dic)
    # py > 3.7, key order preserved.
