from enum import Enum, auto
from typing import NamedTuple

from parse import parse

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
    mask01 = auto()
'''
class DataType(_AutoName):
    image = auto()
    m109xml = auto()
    
    file = auto()
    crop = auto()
    mask = auto()
    
    NONE = auto()
'''
