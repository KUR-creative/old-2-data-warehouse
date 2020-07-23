''' Entity: manga109 '''
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import funcy as F

from dw.const.types import Data, DataType
from dw.util import file_utils as fu


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
    imgpaths = fu.descendants(imgdir(root))
    xmlpaths = fu.descendants(xmldir(root))
    return imgpaths, xmlpaths

def process(loaded):
    return loaded

def canonical(processed) -> Optional[List[Data]]:
    extension = lambda p: Path(p).suffix.replace('.','',1)
    imgpaths, xmlpaths = processed
    
    title_imgpath_dic = F.group_by(fu.select(-2),imgpaths)
    img_ids = list(F.repeatedly(uuid4, len(imgpaths)))
    xml_ids = list(F.repeatedly(uuid4, len(xmlpaths)))
    
    # Note: file type != extension case...
    return [
        Data(uuid,
             DataType.file,
             dict(source=dict(name='manga109'),
                  file=dict(path=p, type=extension(p))))
        for uuid, p in zip(img_ids, imgpaths)
    ] + [
        Data(xml_id,
             DataType.m109xml,
             dict(file=dict(path=p, type=extension(p)),
                  data_rel=dict(a=img_id,
                                b=xml_id,
                                type='img_m109xml')))
        for img_id, xml_id, p in zip(img_ids, xml_ids, xmlpaths)
    ]

#---------------------------------------------------------------
# get.data functions
