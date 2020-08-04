from pathlib import Path

from dw.api import make, put
from dw.entity.data import old_snet
from dw.db import orm
from dw.db import query as Q
from dw.util.test_utils import env_val, skipif_none


def test_make_and_save_old_snet_data(conn, snet):
    conn, snet = env_val(conn=conn), env_val(snet=snet)
    skipif_none(conn, snet)

    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()

    # Make sliced 0/1 masks.
    root_dir = snet
    dst_dir = str(Path(root_dir, 'masks01'))
    file_dic = make.data(old_snet)(root_dir, dst_dir)
    put.files(file_dic) # Use multimethod
    # Check file system: rly saved? same number? same sized imgs?

    # Add masks to DB # Use annotations table
    # Check DB and compare with image, masks from file system
    
    Q.DROP_ALL()
