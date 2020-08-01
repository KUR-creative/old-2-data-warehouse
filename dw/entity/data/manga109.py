''' Entity: manga109 '''
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import funcy as F

from dw.const.types import Data, DataType
from dw.util import file_utils as fu
from dw.util import fp
from dw.db import names as N # Table


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
    iid = F.zipdict(
        imgpaths, F.repeatedly(uuid4, len(imgpaths)))
    xid = F.zipdict(
        xmlpaths, F.repeatedly(uuid4, len(xmlpaths)))
    
    # Note: file type != extension case...
    return [
        Data(
            xid[p],
            DataType.m109xml,
            {N.source: {N.uuid:xid[p], N.name:'manga109'},
             N.file: {N.uuid: xid[p],
                      N.path: p,
                      N.type: fu.extension(p)}}
        ) for p in xmlpaths
    ] + [
        Data(
            iid[ip],
            DataType.image,
            {N.source: {N.uuid: iid[ip], N.name:'manga109'},
             N.file: {N.uuid: iid[ip],
                      N.path: ip,
                      N.type: fu.extension(ip)},
             N.data_relation: {N.aid: iid[ip],
                               N.bid: xid[xp],
                               N.type: 'img_m109xml'}}
        ) for xp, ip in xp_ip_pairseq
    ]

#---------------------------------------------------------------
# get.data functions
