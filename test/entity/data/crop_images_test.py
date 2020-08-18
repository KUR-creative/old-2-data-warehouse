from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st
import imagesize

from dw.api import make, put
from dw.db import orm
from dw.db import query as Q
from dw.db import schema as S
from dw.entity.data import crop_images, szmc_v0
from dw.util.etc_utils import modulo_pad, partition
from dw.util.test_utils import env_val, skipif_none
from dw.util import fp
from dw.util import file_utils as fu
from dw.util.etc_utils import modulo_pad


@st.composite
def gen(draw):
    ws = draw(st.lists(
        st.integers(min_value=400, max_value=10000),
        min_size=2, max_size=2
    ))
    hs = draw(st.lists(
        st.integers(min_value=400, max_value=10000),
        min_size=2, max_size=2
    ))
    w = draw(st.integers(min_value=200, max_value=350))
    h = draw(st.integers(min_value=200, max_value=350))
    return list(zip(ws,hs)), w, h

@given(gen())
def test_generated_number_of_crops(g):
    whs, w, h = g
    ws, hs = fp.unzip(whs)
    _, _, _, _,_, crops_list = crop_images.process(
        (whs, None, ws, hs, w, h))
    assert len(whs) == len(crops_list)
    for (img_w, img_h), crops in zip(whs, crops_list):
        n_w = len(partition(img_w + modulo_pad(img_w, w), w))
        n_h = len(partition(img_h + modulo_pad(img_h, h), h))
        assert len(crops) == n_w * n_h

def test_make_crops(conn, v0_m101):
    conn, v0_m101 = env_val(conn=conn), env_val(v0_m101=v0_m101)
    skipif_none(conn, v0_m101)

    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()
    
    fseq = make.data(szmc_v0.mask_file)(v0_m101)
    put.files(fseq, exist_ok=True)
    put.db_rows( make.data(szmc_v0)(v0_m101, False) )

    with orm.session() as sess:
        rows = [(row.uuid, row.type, row.w, row.h) for row in
                sess.query(S.data.uuid, S.data.type,
                           S.image.w, S.image.h
                ).join(S.image).all()]
    ids, types, org_ws, org_hs = fp.unzip(rows)
    
    # before
    with orm.session() as sess:
        before_n_data = sess.query(S.data).count()
        before_n_imgs = sess.query(S.image).count()
        before_n_rels = sess.query(S.data_relation).count()
    #----------------------------------------------
    w = h = 256
    put.db_rows( make.data(crop_images)(
        ids, types, org_ws, org_hs, w, h) )
    #----------------------------------------------
    # after
    with orm.session() as sess:
        after_n_data = sess.query(S.data).count()
        after_n_imgs = sess.query(S.image).count()
        after_n_rels = sess.query(S.data_relation).count()
        assert after_n_data > before_n_data
        assert after_n_imgs > before_n_imgs
        assert after_n_rels > before_n_rels
        assert(after_n_data - before_n_data
            == after_n_imgs - before_n_imgs
            == after_n_rels - before_n_rels)

    # Check number of added crops
    root_dir = v0_m101
    mask_dir = Path(root_dir, 'mask1bit')
    mask_paths = fu.children(mask_dir)
    
    org_ws, org_hs = fp.unzip(
        imagesize.get(p) for p in mask_paths)
    xys_list = crop_images.crop_xys_list(org_ws, org_hs, h, w)
    num_crops = len(fp.lcat(xys_list)) * 2 # img, mask
    with orm.session() as sess:
        assert num_crops == after_n_data - before_n_data
        
    # look & feel check!
    '''
    with orm.session() as sess:
        parents = fp.lmap(
            S.help.ntup,
            sess.query(S.file.path, S.image.x, S.image.y)
            .join(S.data_relation,
                  S.file.uuid == S.data_relation.aid)
            .join(S.image,
                  S.image.uuid == S.data_relation.bid)
            .order_by(S.file.path, S.image.x, S.image.y))
    
    #from pprint import pprint
    #pprint(parents)
    import cv2
    for path, x, y in parents:
        img = cv2.imread(path)
        cv2.imshow('parent', img)
        cv2.imshow('crop', img[y:y+h, x:x+w])
        cv2.waitKey(0)
    '''
