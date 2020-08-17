from collections import namedtuple
import itertools as I


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
    
    return ids, crops_list
        
def canonical(processed):
    return []
