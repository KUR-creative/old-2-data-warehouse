''' Entity: contributed data from szmc v0 '''
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import cv2
import numpy as np
import funcy as F

from dw.const.types import FileType
from dw.db import schema as S
from dw.util import file_utils as fu
from dw.util import fp


#---------------------------------------------------------------
# make.data functions
def valid(root, add_images: bool):
    '''[valid] <- data root: is valid?'''
    # Check 1:1 mapping.
    return True

# root -> [load] -> [process] -> [canonical]
# -> canonical form of data
def load(root, add_images: bool):
    return root

def process(loaded):
    return loaded

def canonical(processed) -> Optional[List[S.Base]]:
    return processed

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
