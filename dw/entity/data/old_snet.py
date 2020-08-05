from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np 
import funcy as F

from dw.const.types import FileType
from dw.db import orm
from dw.db import schema as S
from dw.util import file_utils as fu
from dw.util import fp

#---------------------------------------------------------------
def valid(root_dir):
    '''[valid] <- data root: is valid?'''
    return True

def load(root_dir):
    # mask info from fs
    easy_dir = Path(root_dir, 'easy')
    hard_dir = Path(root_dir, 'hard')
    easy_paths = fu.children(easy_dir)
    hard_paths = fu.children(hard_dir)
    # image info from DB
    with orm.session() as sess:
        pass
        #sess.query(S.file.path, S.
    return easy_dir, hard_dir, easy_paths, hard_paths

def process(loaded):
    easy_dir, hard_dir, easy_paths, hard_paths = loaded
    return loaded

def canonical(processed):
    easy_dir, hard_dir, easy_paths, hard_paths = processed
    ids = list(F.repeatedly(uuid4, len(easy_paths + hard_paths)))
    #easy_ids = list(F.repeatedly(uuid4, len(easy_paths)))
    #hard_ids = list(F.repeatedly(uuid4, len(hard_paths)))
    return F.concat(
        (S.data(uuid=id, type='mask') for id in ids))

#---------------------------------------------------------------
class mask_file:
    @staticmethod
    def valid(root_dir):
        '''[valid] <- data root: is valid?'''
        #assert not Path(dst_dir).exists()
        return True

    @staticmethod
    def load(root_dir):
        def path2img(p):
            img = cv2.imread(p)
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # TODO: rgba?
        paths = fu.children(Path(root_dir, 'clean_rbk'))
        rbkseq = map(path2img, paths)
        return root_dir, paths, rbkseq

    @staticmethod
    def process(loaded):
        root_dir, paths, rbkseq = loaded
        easyseq, hardseq = fp.unzip(map( # get red, blue channel
            lambda im: (im[:,:,0].astype(bool).astype(np.uint8),
                        im[:,:,2].astype(bool).astype(np.uint8)),
            rbkseq))
        return root_dir, paths, easyseq, hardseq

    # -> Dict[Path, Tuple[FileType, Any]])
    @staticmethod
    def canonical(processed):
        root_dir, paths, easyseq, hardseq = processed
        
        rbk_to = fu.replace1('clean_rbk')
        easy_pathseq = (rbk_to('easy', path) for path in paths)
        hard_pathseq = (rbk_to('hard', path) for path in paths)
        
        yield FileType.folder, Path(root_dir, 'easy'), True
        yield FileType.folder, Path(root_dir, 'hard'), True
        # type, path, True means exist_ok=true
        for path, mask in zip(easy_pathseq, easyseq):
            yield FileType.npimg, path, mask
        for path, mask in zip(hard_pathseq, hardseq):
            yield FileType.npimg, path, mask
