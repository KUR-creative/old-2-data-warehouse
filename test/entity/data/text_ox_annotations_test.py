
from sqlalchemy.orm import aliased

from dw.api import make, put
from dw.entity.data import crop_images, text_ox_annotations
from dw.db import orm
from dw.db import schema as S
from dw.db import query as Q
from dw.ui import cli
from dw.util.test_utils import env_val, skipif_none
from dw.util import fp


def test_make_and_save_old_snet_data(
        conn, v0_m101, v0_school, test_cfc):
    conn = env_val(conn=conn)
    v0_m101 = env_val(v0_m101=v0_m101)
    v0_school = env_val(v0_school=v0_school)
    cfc = env_val(test_cfc=test_cfc)
    skipif_none(conn, v0_m101, v0_school, cfc)

    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()
    
    assert cli.init(conn) == cli.RUN_SUCCESS
    assert cli.data.szmc_v0(conn, v0_m101) == cli.RUN_SUCCESS
    assert cli.data.szmc_v0(conn, v0_school) == cli.RUN_SUCCESS
    assert cli.data.image_directory(conn, cfc) == cli.RUN_SUCCESS

    with orm.session() as sess:
        rows = [(row.uuid, row.type, row.w, row.h) for row in
                sess.query(S.data.uuid, S.data.type,
                           S.image.w, S.image.h
                ).join(S.image).all()]
    ids, types, org_ws, org_hs = fp.unzip(rows)
    
    #----------------------------------------------
    w = h = 256
    put.db_rows( make.data(crop_images)(
        ids, types, org_ws, org_hs, w, h) )
    
    # Get crop ids
    with orm.session() as sess:
        # only clean images(clean_fmd_comics)
        no_text_pairs = [
            (row.bid, True) for row in
            sess.query(S.data_relation.bid)
                .join(S.source,
                      S.data_relation.aid == S.source.uuid)
                .filter(S.source.name == 'clean_fmd_comics')
                .filter(S.data_relation.type == 'image_crop')
                .all()]
        
        # crop pairs (not whole image)
        idat = aliased(S.data)
        mdat = aliased(S.data)
        img_mask_pairs = [
            (row.aid, row.bid) for row in
            sess.query(S.data_relation.aid, S.data_relation.bid)
                .join(idat, idat.uuid == S.data_relation.aid)
                .join(mdat, mdat.uuid == S.data_relation.bid)
                .filter(idat.type == 'image')
                .filter(mdat.type == 'mask')]

    # TODO: Check equality of mask = composed crops
    # TODO: If too slow, remove v0_m101, reduce size of example..
    thrshold = 100
    put.db_rows( make.data(text_ox_annotations)(
        fp.concat(no_text_pairs, img_mask_pairs), thrshold) )

    from pprint import pprint
    pprint(no_text_pairs)
    pprint(img_mask_pairs)
