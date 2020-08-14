# mypy: ignore-errors
import cv2

from dw.const import types
from dw.db import orm
from dw.db import schema as S
from dw.util import fp


def db_rows(cfseq):
    with orm.session() as sess:
        for cf in cfseq:
            if cf == S.COMMIT:
                sess.commit()
            else:
                sess.add(cf)
        sess.commit()

#def files(mapping: Dict[Path, Tuple[FT, Any]]):
def files(type_path_valueseq, exist_ok=False):
    # Visual Check
    for t,p,v in type_path_valueseq:
        types.write(t, p, v, exist_ok)
