from dw.api import make, put
from dw.db import orm
from dw.db import query as Q
from dw.db import schema as S
from dw.entity.data import manga109, image_only_relations
from dw.entity.dataset import tmp_cnet_dset
from dw.util.test_utils import env_val, skipif_none


def test_make_and_save_data_rel_chunk_and_dataset(conn, m109):
    conn, m109 = env_val(conn=conn), env_val(m109=m109)
    skipif_none(conn, m109)
    
    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()
    
    # Put m109
    put.db_rows( make.data(manga109)(m109) )
    
    # Put additional data to generate dataset
    cfseq = make.data(image_only_relations)()
    put.db_rows(cfseq)
    # Check img-img relations
    with orm.session() as sess:
        img_rels = [(row.aid, row.bid) for row in 
            sess.query(S.data_relation).filter(
            S.data_relation.type == 'only_img' # TODO: remove magic-string
        ).all()]
        img_ids = [row.uuid for row in
            sess.query(S.data).filter(
            S.data.type == 'image' # TODO: remove magic-string
        ).all()]
    assert len(img_rels) == len(img_ids)
    assert [r[0] for r in img_rels] == [r[1] for r in img_rels]
    assert sorted(row[0] for row in img_rels) \
        == sorted(img_ids)

    # Make and Put dataset
    put.db_rows( make.dataset(tmp_cnet_dset)() )
    # Check tables
    with orm.session() as sess:
        assert sess.query(S.named_relations).count() == 3
        assert sess.query(S.named_relations2data_relation).count() \
            == 100
        assert sess.query(S.dataset).count() == 1
        
    Q.DROP_ALL()
