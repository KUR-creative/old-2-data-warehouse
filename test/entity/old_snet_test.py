from pathlib import Path

import imagesize

from dw.api import make, put
from dw.entity.data import old_snet
from dw.db import orm
from dw.db import schema as S
from dw.db import query as Q
from dw.util.test_utils import env_val, skipif_none
from dw.util import file_utils as fu


def test_make_and_save_old_snet_data(conn, snet):
    conn, snet = env_val(conn=conn), env_val(snet=snet)
    skipif_none(conn, snet)

    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()

    # Make sliced 0/1 masks.
    root_dir = snet
    easy_dir = Path(root_dir, 'easy')
    hard_dir = Path(root_dir, 'hard')
    fseq = make.data(old_snet.mask_file)(root_dir)
    put.files(fseq, exist_ok=True) # TODO: exist_ok=False?
    # really saved? 
    assert easy_dir.exists()
    assert hard_dir.exists()
    # same number?
    easy_paths = fu.children(easy_dir)
    hard_paths = fu.children(hard_dir)
    assert len(easy_paths) == len(hard_paths)
    # same sized imgs?
    easy_sizes = [imagesize.get(p) for p in easy_paths]
    hard_sizes = [imagesize.get(p) for p in hard_paths]
    assert easy_sizes == hard_sizes

    # before put.cfs
    with orm.session() as sess:
        prev_num_data = sess.query(S.data).count()
    num_files = len(easy_paths) + len(hard_paths)
    # Add masks to DB # Use annotation table
    put.canonical_forms( make.data(old_snet)(snet) )
    # Check DB and compare with image, masks from file system
    with orm.session() as sess:
        # check data(type = mask)
        num_data = sess.query(S.data).count()
        assert num_files == num_data - prev_num_data
        # check annotation
        assert num_files == sess.query(S.annotation).count()
        # check file
        # check source
        # check data_relation
    
    #shutil.rmtree(dst_dir)
    #assert not dst_dir.exists()
    
    Q.DROP_ALL()
