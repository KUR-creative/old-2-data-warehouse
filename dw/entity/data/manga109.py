''' Entity: manga109 '''
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import funcy as F

from dw.const.types import Data, DataType
from dw.util import file_utils as fu
from dw.util import fp
from dw.db import names as N # Table
from dw.db import schema as S


#---------------------------------------------------------------
def imgdir(root): return Path(root, 'images')
def xmldir(root): return Path(root, 'manga109-annotations')

#---------------------------------------------------------------
# make.data functions
def valid(root):
    '''[valid] <- data root: is valid?'''
    return True

# root -> [load] -> [process] -> [canonical]
# -> canonical form of data
def load(root):
    imgpaths = fu.human_sorted(fu.descendants(imgdir(root)))
    xmlpaths = fu.human_sorted(fu.descendants(xmldir(root)))
    return imgpaths, xmlpaths

def process(loaded):
    name = lambda p: Path(p).stem
    imgpaths, xmlpaths = loaded
    
    title2xmlpath = F.zipdict(map(name,xmlpaths), xmlpaths)
    xmlpath_imgpath_pairseq = fp.go(
        F.group_by(fu.select(-2),imgpaths), # title: [imgpaths...]
        lambda dic: dic.items(), # (title, [imgpaths...])
        fp.mapcat(fp.tup(
            lambda title, imgpaths:
            zip(F.repeat(title2xmlpath[title]), imgpaths)
        )))
            
    #for xp, ip in xp_ip_pairseq:
    #    assert name(xp) == fu.select(-2, ip)
    return imgpaths, xmlpaths, xmlpath_imgpath_pairseq

def canonical(processed) -> Optional[List[Data]]:
    imgpaths, xmlpaths, xp_ip_pairseq = processed
    iids = list(F.repeatedly(uuid4, len(imgpaths)))
    xids = list(F.repeatedly(uuid4, len(xmlpaths)))
    p2id = F.zipdict(imgpaths + xmlpaths, iids + xids)
    
    xp_ip_pairs = list(xp_ip_pairseq)
    return F.concat(
        # xml
        (S.data(uuid=id, type='m109xml') for id in xids),
        ['COMMIT'],
        (S.source(uuid=id, name='manga109') for id in xids),
        (S.file(uuid=p2id[p],
                path=p,
                type=fu.extension(p)) for p in xmlpaths),
        # img, TODO: add image table
        (S.data(uuid=id, type='image') for id in iids),
        ['COMMIT'],
        (S.source(uuid=id, name='manga109') for id in iids),
        (S.file(uuid=p2id[p],
                path=p,
                type=fu.extension(p)) for p in imgpaths),
                 # Note: file type != extension case...
        (S.data_relation(
            aid=p2id[ip],
            bid=p2id[xp],
            type='img_m109xml') for xp, ip in xp_ip_pairs)
    )

#---------------------------------------------------------------
# get.data functions
