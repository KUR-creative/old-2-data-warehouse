''' 
Components of make.data pipeline 
[valid] <- data root: is valid?
root -> [load] -> [process] -> [canonical]
-> canonical form of data
'''
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import funcy as F

from dw.const.types import Data, DataType
from dw.util import file_utils as fu


def valid(root):
    return True

# root -> [load] -> [process] -> [canonical]
# -> canonical form of data
def load(root):
    img_dir = Path(root, 'images')
    xml_dir = Path(root, 'manga109-annotations')
    imgpaths = fu.descendants(img_dir)
    xmlpaths = fu.descendants(xml_dir)
    return imgpaths, xmlpaths

def process(loaded):
    return loaded

def canonical(processed) -> Optional[List[Data]]:
    ext = lambda p: Path(p).suffix.replace('.','',1)
    imgpaths, xmlpaths = processed
    
    title_imgpath_dic = F.group_by(fu.select(-2),imgpaths)
    img_ids = list(F.repeatedly(uuid4, len(imgpaths)))
    xml_ids = list(F.repeatedly(uuid4, len(xmlpaths)))
    
    return [
        Data(uuid,
             DataType.file,
             dict(file=dict(path=p, extension=ext(p))))
        for uuid, p in zip(img_ids, imgpaths)
    ] + [
        Data(xml_id,
             DataType.m109xml,
             dict(file=dict(path=p, extension=ext(p)),
                  data_rel=(img_id, xml_id, 'manga109_xml')))
        for img_id, xml_id, p in zip(img_ids, xml_ids, xmlpaths)
    ]
        
