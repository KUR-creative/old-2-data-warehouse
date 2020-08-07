from pathlib import Path

import imagesize
import funcy as F 

from dw.api import make, put
from dw.entity.data import szmc_v0
from dw.db import orm
from dw.db import query as Q
from dw.util.test_utils import env_val, skipif_none
from dw.util import file_utils as fu


def test_make_and_save_v0_m101_data(conn, v0_m101):
    conn, v0_m101 = env_val(conn=conn), env_val(v0_m101=v0_m101)
    skipif_none(conn, v0_m101)
    
    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()

    root_dir = v0_m101
    #-----------------
    org_dir = Path(root_dir, 'prev_images')
    mask_dir = Path(root_dir, 'masks')
    mask1bit_dir = Path(root_dir, 'mask1bit')

    # Add origin image, masks.
    fseq = make.data(szmc_v0.mask_file)(root_dir)
    put.files(fseq, exist_ok=True) # TODO: exist_ok=False?
    # really saved?
    assert mask1bit_dir.exists()
    # same number?
    mask_paths = fu.children(mask_dir)
    mask1bit_paths = fu.children(mask1bit_dir)
    assert len(mask_paths) == len(mask1bit_paths)
    # same sized imgs?
    mask_sizes = [imagesize.get(p) for p in mask_paths]
    mask1bit_sizes = [imagesize.get(p) for p in mask1bit_paths]
    assert mask_sizes == mask1bit_sizes
                        
    #put.canonical_forms( make.data(szmc_v0)(root_dir, False) )
