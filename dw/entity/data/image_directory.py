from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import funcy as F
import filetype

from dw.util import file_utils as fu
from dw.db import schema as S


# make.data functions
def valid(root, source):
    '''[valid] <- data root: is valid?'''
    return Path(root).is_dir()

# root -> [load] -> [process] -> [canonical]
# -> canonical form of data
def load(root, source):
    paths = fu.human_sorted(fu.descendants(root))
    for p in paths:
        kind = filetype.guess(p)
        assert kind is not None
        assert kind.mime.split('/')[0] == 'image'
    return source, paths

def process(loaded):
    source, paths = loaded
    ids = list(F.repeatedly(uuid4, len(paths)))
    return source, paths, ids

def canonical(processed) -> Optional[List[S.Base]]:
    source, paths, ids = processed
    return F.concat(
        # xml
        (S.data(uuid=id, type='image') for id in ids),
        [S.COMMIT],
        (S.source(uuid=id, name=source) for id in ids),
        (S.file(uuid=id, path=p, type=fu.extension(p))
         for id,p in zip(ids, paths)))

#---------------------------------------------------------------
# get.data functions
