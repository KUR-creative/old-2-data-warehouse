from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np 
import funcy as F

from dw.const.types import FileType
from dw.db import schema as S
from dw.util import file_utils as fu
from dw.util import fp

#---------------------------------------------------------------
def valid(root_dir):
    '''[valid] <- data root: is valid?'''
    return True

def load(root_dir):
    img_paths = fu.children(Path(root_dir, 'image'))
    img_to = fu.replace1('image')
    easy_paths = [img_to('easy', p) for p in img_paths]
    hard_paths = [img_to('hard', p) for p in img_paths]
    return img_paths, easy_paths, hard_paths

def process(loaded):
    img_paths, easy_paths, hard_paths = loaded
    img_ids = list(F.repeatedly(uuid4, len(img_paths)))
    easy_ids = list(F.repeatedly(uuid4, len(easy_paths)))
    hard_ids = list(F.repeatedly(uuid4, len(hard_paths)))
    paths = img_paths + easy_paths + hard_paths
    ids = img_ids + easy_ids + hard_ids
    return (img_paths, easy_paths, hard_paths,
            img_ids, easy_ids, hard_ids,
            paths, ids)

def canonical(processed):
    (img_paths, easy_paths, hard_paths,
     img_ids, easy_ids, hard_ids,
     paths, ids) = processed
    return F.concat(
        # ids first
        (S.data(uuid=id, type='image') for id in img_ids),
        (S.data(uuid=id, type='mask') for id in easy_ids),
        (S.data(uuid=id, type='mask') for id in hard_ids),
        # all
        [S.COMMIT],
        (S.file(uuid=id, path=path, type=fu.extension(path))
         for id, path in zip(ids, paths)),
        (S.source(uuid=id, name='old_snet') for id in ids),
        # mask
        (S.annotation(uuid=id, type='text.mask', group='easy')
         for id in easy_ids),
        (S.annotation(uuid=id, type='text.mask', group='hard')
         for id in hard_ids),
        # relations
        (S.data_relation(aid=iid, bid=eid, type='img_mask')
         for iid, eid in zip(img_ids, easy_ids)),
        (S.data_relation(aid=iid, bid=hid, type='img_mask')
         for iid, hid in zip(img_ids, hard_ids)),
    )

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
