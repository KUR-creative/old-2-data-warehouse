from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import funcy as F
import filetype
import imagesize

from dw.util import file_utils as fu
from dw.db import schema as S


def assert_img(path):
    kind = filetype.guess(path)
    assert kind is not None
    assert kind.mime.split('/')[0] == 'image'
    return path
    
#---------------------------------------------------------------
# make.data functions
def valid(root, source):
    '''[valid] <- data root: is valid?'''
    return Path(root).is_dir()

# root -> [load] -> [process] -> [canonical]
# -> canonical form of data
def load(root, source):
    paths = fu.human_sorted(fu.descendants(root))
    whs = [imagesize.get(assert_img(p)) for p in paths]
    return source, paths, whs

def process(loaded):
    source, paths, whs = loaded
    ids = list(F.repeatedly(uuid4, len(paths)))
    return source, paths, whs, ids

def canonical(processed) -> Optional[List[S.Base]]:
    source, paths, whs, ids = processed
    return F.concat(
        (S.data(uuid=id, type='image') for id in ids),
        [S.COMMIT],
        (S.image(uuid=id, x=0,y=0, w=w,h=h, full_w=w,full_h=h)
         for id, (w, h) in zip(ids, whs)),
        (S.source(uuid=id, name=source) for id in ids),
        (S.file(uuid=id, path=p, type=fu.extension(p))
         for id, p in zip(ids, paths)))

#---------------------------------------------------------------
# get.data functions
