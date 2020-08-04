#from typing import Tuple, Any, Dict
from pathlib import Path

from dw.db import orm
from dw.db import schema as S
#from dw.const.types import FileType


def canonical_forms(cfseq):
    with orm.session() as sess:
        for cf in cfseq:
            if cf == S.COMMIT:
                sess.commit()
            else:
                sess.add(cf)
        sess.commit()

#def files(mapping: Dict[Path, Tuple[FileType, Any]]):
def files(file_dic):
    return file_dic
