from typing import Iterable

from dw.const import types
from dw.db import orm
from dw.db import schema as S
from dw.util import fp

#---------------------------------------------------------------
def data(cfs: Iterable[types.Data]):
    ''' put.data(CanonicalFormS) to initialized db '''
    assert orm.engine is not None, 'orm.init first.'

    datumseq = (S.data(cf) for cf in cfs)
    valueseq = (cf.value for cf in cfs)
    rowseq = fp.mapcat(value2row, valueseq)
    with orm.session() as sess:
        sess.add_all(datumseq); sess.commit()
        sess.add_all(rowseq)

#def dat_rel_chunk(cfs: Iterable[types.DatRelChunk]):
#    ''' put.dat_rel_chunk(CanonicalForms) '''

#---------------------------------------------------------------
def value2row(v):
    ''' value dict -> schema object(row) '''
    return [fp.prop(name, S)(**row) for name,row in v.items()]
    # Is it ok? Is orm commit data_rel last?? Maybe..
