from collections import namedtuple
import funcy as F
import itertools as I
from uuid import uuid4

from dw.util import fp
from dw.util.etc_utils import modulo_pad, partition

#---------------------------------------------------------------
def valid(ids, whs, w, h):
    return True
    
def load(ids, origin_whs, crop_w, crop_h):
    ''' 
    ids, origin_whs are about source images.
    w, h are target crop size.
    '''
    return ids, origin_whs, crop_w, crop_h

def process(loaded):
    ids, origin_whs, w, h = loaded
    # Make img_(w,h)s multiply of crop_(w,h)
    img_ws, img_hs = fp.unzip((org_w + modulo_pad(org_w, w),
                               org_h + modulo_pad(org_h, h))
                              for org_w, org_h in origin_whs)
    x0x1s_list = (partition(img_w, w) for img_w in img_ws)
    y0y1s_list = (partition(img_h, h) for img_h in img_hs)
    
    # [[(x0,x1),(y0,y1)), (x1,x2),(y0,y1)) ...], ...]
    intervals_list = fp.map(
        lambda x0x1s, y0y1s: I.product(x0x1s, y0y1s),
        x0x1s_list, y0y1s_list)
    # [ [(x0,x1,y0,y1), (x1,x2,y0,y1), ...], [...], ... ]
    crops_list = [
        [namedtuple('Crop', 'x0 x1 y0 y1')(x0, x1, y0, y1) # type: ignore
         for (x0, x1), (y0, y1) in intervals]
        for intervals in intervals_list]
    # TODO: change to just x,y
    
    return ids, crops_list
        
def canonical(processed):
    img_ids, crops_list = processed

    crop_ids_list = [[uuid4() for _ in crops]
                     for crops in crops_list]
    img_crop_rels = fp.lmapcat(
        lambda iid, cids: zip(F.repeat(iid),cids),
        img_ids, crop_ids_list)
        
    crop_ids = F.lconcat(crop_ids_list)
    crops = F.lconcat(crops_list)
    
    '''
    from pprint import pprint
    pprint(img_ids)
    print('----')
    pprint(img_crop_rels)
    '''
    return F.concat(
        (S.data(uuid=id, type=data_type) for id in crop_ids),
        [S.COMMIT],
        (S.image(uuid=id, x=0,y=0, w=w,h=h, full_w=w,full_h=h)
         for id, (w, h) in zip(ids, whs)),
    return []
