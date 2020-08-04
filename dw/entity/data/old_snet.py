from typing import List, Optional

from dw.db import schema as S


def valid(root_dir, dst_dir):
    '''[valid] <- data root: is valid?'''
    return True

def load(root_dir, dst_dir):
    return root_dir

def process(loaded):
    return loaded

def canonical(processed) -> Optional[List[S.Base]]:
    return []
