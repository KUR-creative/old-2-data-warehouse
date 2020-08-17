''' Entity: contributed data from szmc v0 '''
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import cv2
import funcy as F
import imagesize
import numpy as np


from dw.const.types import FileType
from dw.db import schema as S
from dw.util import file_utils as fu
from dw.util import fp


#---------------------------------------------------------------
# make.data functions
def valid(root_dir, add_images: bool): # = True
    '''
    [valid] <- data root: is valid?
    add_images means: add generated images in 'images' folder
    '''
    # Check 1:1 mapping.
    return True

# root -> [load] -> [process] -> [canonical]
# -> canonical form of data
def load(root_dir, add_images: bool): # = True
    ''' add_images:
    if True, then add generated images in 'images' folder.
    if False, skip adding images in 'images' folder '''
    org_dir = 'prev_images'
    org_paths = fu.children(Path(root_dir, org_dir))
    mask1bit_paths = fp.go(
        org_paths,
        fp.map(fu.replace1(org_dir, 'mask1bit')),
        fp.map(lambda p: Path(p).with_suffix('.png')),
        fp.lmap(str))
    return org_paths, mask1bit_paths

def process(loaded):
    img_paths, mask_paths = loaded
    img_ids = list(F.repeatedly(uuid4, len(img_paths)))
    mask_ids = list(F.repeatedly(uuid4, len(mask_paths)))
    paths = img_paths + mask_paths
    whs = [imagesize.get(p) for p in paths]
    ids = img_ids + mask_ids
    return (img_paths, mask_paths,
            img_ids, mask_ids,
            paths, whs, ids)

def canonical(processed) -> Optional[List[S.Base]]:
    (img_paths, mask_paths,
     img_ids, mask_ids,
     paths, whs, ids) = processed
    return F.concat(
        # ids first
        (S.data(uuid=id, type='image') for id in img_ids),
        (S.data(uuid=id, type='mask') for id in mask_ids),
        [S.COMMIT],
        # all
        (S.file(uuid=id, path=path, type=fu.extension(path))
         for id, path in zip(ids, paths)),
        (S.source(uuid=id, name='szmc_v0') for id in ids),
        (S.image(uuid=id, x=0,y=0, w=w,h=h, full_w=w,full_h=h)
         for id, (w, h) in zip(ids, whs)),
        # mask
        (S.annotation(uuid=id, type='text.mask', group='all')
         for id in mask_ids),
        # relations
        (S.data_relation(aid=iid, bid=mid, type='img_mask')
         for iid, mid in zip(img_ids, mask_ids)))

#---------------------------------------------------------------
class mask_file: # TODO: simmilar to old_snet.mask_file ..
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
        paths = fu.children(Path(root_dir, 'masks')) # diff
        maskseq = map(path2img, paths)
        return root_dir, paths, maskseq

    @staticmethod
    def process(loaded):
        root_dir, paths, maskseq = loaded
        # DIFF: get red channel(diff)
        mask1bitseq = (im[:,:,0].astype(bool).astype(np.uint8)
                       for im in maskseq)
        return root_dir, paths, mask1bitseq

    @staticmethod
    def canonical(processed):
        root_dir, paths, mask1bitseq = processed
        
        mask1bit_pathseq = (
            fu.replace1('masks', 'mask1bit', p) for p in paths)
        
        yield FileType.folder, Path(root_dir, 'mask1bit'), True
        # type, path, True means exist_ok=true
        for path, mask in zip(mask1bit_pathseq, mask1bitseq):
            yield FileType.npimg, path, mask
#---------------------------------------------------------------
# get.data functions
