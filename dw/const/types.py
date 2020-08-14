from enum import Enum, auto
from typing import NamedTuple

import cv2
from multimethod import overload
from parse import parse

from dw.util import fp

#---------------------------------------------------------------
# Common types
class Connection(NamedTuple):
    user: str
    password: str
    host: str
    port: int
    dbname: str

def connection(conn_str: str):
    parsed = parse('{}:{}@{}:{}/{}', conn_str)
    return Connection(*parsed) if parsed else None

#---------------------------------------------------------------
# Enumerte types
class _AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
    
class FileType(_AutoName):
    npimg = auto()
    folder = auto()
    tfrecord = auto()
    
@overload
def write(file_type, path, value, exist_ok=False):
    ''' write value to path by kind '''
    assert False, 'Use registered file type. See dw.const.types'
    
@write.register
def _(type: fp.equal(FileType.npimg), path, mask, exist_ok): # type: ignore
    #print(':',type(mask), 'l', len(mask))
    cv2.imwrite(path, mask, [cv2.IMWRITE_PNG_BILEVEL, 1])

@write.register # type: ignore
def _(type: fp.equal(FileType.folder), path, _, exist_ok):  # type: ignore
    path.mkdir(exist_ok=exist_ok)

'''
class DataType(_AutoName):
    image = auto()
    m109xml = auto()
    
    file = auto()
    crop = auto()
    mask = auto()
    
    NONE = auto()
'''
