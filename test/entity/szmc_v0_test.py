from pathlib import Path

import imagesize

from dw.api import make, put
from dw.entity.data import szmc_v0
from dw.db import orm
from dw.db import schema as S
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
    org_paths = fu.children(org_dir)
    mask_paths = fu.children(mask_dir)
    mask1bit_paths = fu.children(mask1bit_dir)
    assert len(mask_paths) == len(mask1bit_paths)
    # same sized imgs?
    mask_sizes = [imagesize.get(p) for p in mask_paths]
    mask1bit_sizes = [imagesize.get(p) for p in mask1bit_paths]
    assert mask_sizes == mask1bit_sizes
                        
    # before put.cfs
    with orm.session() as sess:
        prev_num_data = sess.query(S.data).count()
        prev_num_files = sess.query(S.file).count()
        prev_num_rels = sess.query(S.data_relation).count()
    num_added = len(org_paths + mask_paths)
    num_masks = len(mask_paths)
    assert num_added == 2 * num_masks
    # Add masks to DB # Use annotation table
    put.canonical_forms( make.data(szmc_v0)(root_dir, False) )
    # Check DB and compare with image, masks from file system
    with orm.session() as sess:
        # check data(type = mask)
        num_data = sess.query(S.data).count()
        num_imgs_in_db = sess.query(S.data).filter(
            S.data.type == 'image'
        ).count()
        num_masks_in_db = sess.query(S.data).filter(
            S.data.type == 'mask'
        ).count()
        assert num_added == num_data - prev_num_data
                # TODO: add constant table and their relations
        assert num_imgs_in_db == num_masks_in_db
        assert num_added == num_imgs_in_db + num_masks_in_db
        # check file
        num_files = sess.query(S.file).count()
        assert num_added == num_files - prev_num_files
        # check source
        assert num_added == sess.query(S.source).filter(
            S.source.name == 'szmc_v0').count()
        # check annotation
        assert num_masks == sess.query(S.annotation).count()
        # check data_relation
        num_rels = sess.query(S.data_relation).count()
        assert num_masks == num_rels - prev_num_rels

    Q.DROP_ALL()
