from typing import Iterable

import funcy as F

from dw.const import types
from dw.db import orm
from dw.db import schema as S


def data(cfs: Iterable[types.Data]):
    ''' put.data(Canonical_FormS) to initialized db '''
    assert orm.engine is not None, 'orm.init first.'

    datumseq = (S.data(cf) for cf in cfs)
    values = [cf.value for cf in cfs]
    with orm.session() as sess:
        sess.add_all(datumseq)
        sess.commit()

    from pprint import pprint
    print(' v0')
    pprint(values[0])
    print(' v-1')
    pprint(values[-1])
