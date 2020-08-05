import shutil
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
    img_dir = Path(root_dir, 'image')
    easy_dir = Path(root_dir, 'easy')
    hard_dir = Path(root_dir, 'hard')
    
    fseq = make.data(old_snet.mask_file)(root_dir)
    put.files(fseq, exist_ok=True) # TODO: exist_ok=False?
    # really saved? 
    assert easy_dir.exists()
    assert hard_dir.exists()
    # same number?
    img_paths = fu.children(img_dir)
    easy_paths = fu.children(easy_dir)
    hard_paths = fu.children(hard_dir)
    assert len(easy_paths) == len(hard_paths)
    # same sized imgs?
    img_sizes = [imagesize.get(p) for p in img_paths]
    easy_sizes = [imagesize.get(p) for p in easy_paths]
    hard_sizes = [imagesize.get(p) for p in hard_paths]
    assert img_sizes == easy_sizes == hard_sizes

    # before put.cfs
    with orm.session() as sess:
        prev_num_data = sess.query(S.data).count()
        prev_num_files = sess.query(S.file).count()
        prev_num_rels = sess.query(S.data_relation).count()
    num_added = len(img_paths + easy_paths + hard_paths)
    num_masks = len(easy_paths + hard_paths)
    # Add masks to DB # Use annotation table
    put.canonical_forms( make.data(old_snet)(snet) )
    # Check DB and compare with image, masks from file system
    with orm.session() as sess:
        # check data(type = mask)
        num_data = sess.query(S.data).count()
        assert num_added == num_data - prev_num_data
        # check file
        num_files = sess.query(S.file).count()
        assert num_added == num_files - prev_num_files
        # check source
        assert num_added == sess.query(S.source).filter(
            S.source.name == 'old_snet').count()
        # check annotation
        assert num_masks == sess.query(S.annotation).count()
        # check data_relation
        num_rels = sess.query(S.data_relation).count()
        assert num_masks == num_rels - prev_num_rels

    Q.DROP_ALL()
