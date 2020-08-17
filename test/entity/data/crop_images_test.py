from hypothesis import given
from hypothesis import strategies as st

from dw.api import make, put
from dw.db import orm
from dw.db import query as Q
from dw.db import schema as S
from dw.entity.data import crop_images, szmc_v0
from dw.util.etc_utils import modulo_pad, partition
from dw.util.test_utils import env_val, skipif_none

@st.composite
def gen(draw):
    ws = draw(st.lists(
        st.integers(min_value=400, max_value=10000),
        min_size=1, max_size=2
    ))
    hs = draw(st.lists(
        st.integers(min_value=400, max_value=10000),
        min_size=1, max_size=2
    ))
    w = draw(st.integers(min_value=200, max_value=350))
    h = draw(st.integers(min_value=200, max_value=350))
    return list(zip(ws,hs)), w, h

@given(gen())
def test_crops(g):
    whs, w, h = g
    _, crops_list = crop_images.process((None, whs, w, h))
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
        img_ids = [x.uuid for x in
                   sess.query(S.data.uuid).filter(
                       S.data.type == 'image').all()] # TODO: remove magic-string
        whs = [(im.w, im.h) for im in
               sess.query(S.image.w, S.image.h).all()]
    w = h = 256
    put.db_rows( make.data(crop_images)(img_ids, whs, w, h) )
    assert False
