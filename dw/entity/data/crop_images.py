import itertools as I
from uuid import uuid4

from dw.db import schema as S
from dw.util import fp
from dw.util.etc_utils import modulo_pad, factorseq


#---------------------------------------------------------------
def valid(ids, types, origin_ws, origin_hs, crop_w, crop_h):
    return True
    
def load(ids, types, origin_ws, origin_hs, crop_w, crop_h):
    ''' 
    ids, origin_whs are about source images.
    w, h are target crop size.
    '''
    return ids, types, origin_ws, origin_hs, crop_w, crop_h

def process(loaded):
    ids, types, org_ws,org_hs, w,h = loaded
    # Make img_(w,h)s multiply of crop_(w,h)
    img_wseq = (org_w + modulo_pad(org_w,w) for org_w in org_ws)
    img_hseq = (org_h + modulo_pad(org_h,h) for org_h in org_hs)
    xs = [list(factorseq(img_w, w)) for img_w in img_wseq]
    ys = [list(factorseq(img_h, h)) for img_h in img_hseq]
    xys_list = fp.lmap(fp.pipe(I.product, list), xs, ys)
    org_whs = zip(org_ws, org_hs)
    
    '''
    from pprint import pprint
    print('---------------------------')
    #pprint(xys_list)
    pprint(loaded)
    #pprint(fp.lmap(list,xyseq))
    pprint(xs)
    '''
    assert len(ids) == len(xys_list)
    return ids, types, org_whs, w,h, xys_list
        
def canonical(processed):
    ''' origin image => crops '''
    org_ids, types, org_whs, w,h, xys_list = processed
    # org_ids, types, org_whs are origin image info. same len.
    # w, h are all crops size
    # xys_list is begin coord(x,y) of crops of images.
    # list of list, same len with other lists.
    
    crop_ids_list = fp.lmap(
        lambda xys: fp.lrepeatedly(uuid4, len(xys)), xys_list)
    zipped = fp.lmapcat(
        lambda cids, oid, type, org_wh:
        fp.lzip(cids,
                fp.repeat(oid),
                fp.repeat(type),
                fp.repeat(org_wh)),
        crop_ids_list, org_ids, types, org_whs)
    crop_ids, img_ids, crop_types, full_whs = fp.unzip(zipped)
    crop_xys = fp.lcat(xys_list)
                
    return fp.concat(
        (S.data(uuid=id, type=type)
         for id, type in zip(crop_ids, crop_types)),
        [S.COMMIT],
        (S.image(uuid=id, x=x,y=y, w=w,h=h, full_w=fw,full_h=fh)
         for id, (x,y), (fw,fh) in
         zip(crop_ids, crop_xys, full_whs)),
        (S.data_relation(aid=iid, bid=cid, type='image_crop')
         for iid, cid in zip(img_ids, crop_ids))
    )
