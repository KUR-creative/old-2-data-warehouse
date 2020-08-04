# mypy: ignore-errors
from multimethod import overload
import cv2

from dw.const.types import FileType as FT
from dw.db import orm
from dw.db import schema as S
from dw.util import fp


def canonical_forms(cfseq):
    with orm.session() as sess:
        for cf in cfseq:
            if cf == S.COMMIT:
                sess.commit()
            else:
                sess.add(cf)
        sess.commit()

@overload
def _write(type: fp.equal(FT.npimg), path, mask, exist_ok=False):
    cv2.imwrite(path, mask, [cv2.IMWRITE_PNG_BILEVEL, 1])

@overload
def _write(type: fp.equal(FT.folder), path, _, exist_ok=False):
    path.mkdir(exist_ok=exist_ok)

#def files(mapping: Dict[Path, Tuple[FT, Any]]):
def files(type_path_valueseq, exist_ok=False):
    # Visual Check
    for t,p,v in type_path_valueseq:
        _write(t, p, v, exist_ok)
