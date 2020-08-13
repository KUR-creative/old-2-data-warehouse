from dw.api import make, put
from dw.db import orm
from dw.db import query as Q
from dw.db import schema as S
from dw.entity.data import manga109, image_only_relations
from dw.entity.dataset import tmp_cnet_dset
from dw.util.test_utils import env_val, skipif_none


def test_put_data_from_manga109(conn, m109):
    conn, m109 = env_val(conn=conn), env_val(m109=m109)
    skipif_none(conn, m109)
    
    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()
    
    cfs = make.data(manga109)(m109)
    put.db_rows(cfs)
    
    with orm.session() as sess:
        img_ids = [
            x.uuid for x in
            sess.query(S.data.uuid).filter(
                S.data.type == 'image').all()] # TODO: remove magic-string
        xml_ids = [
            x.uuid for x in
            sess.query(S.data.uuid).filter(
                S.data.type == 'm109xml').all()] # TODO: remove magic-string
        
        # Check number of uuids
        num_data = sess.query(S.data).count()
        num_imgs = len(img_ids)
        num_xmls = len(xml_ids)
        num_img_rows = sess.query(S.file).filter(
            S.file.type != 'xml').count()
        num_xml_rows = sess.query(S.file).filter(
            S.file.type == 'xml').count()
        assert num_data == num_imgs + num_xmls
        assert num_imgs == num_img_rows
        assert num_xmls == num_xml_rows
        
        # Check uuids as set
        relations = sess.query(
            S.data_relation.aid, S.data_relation.bid).filter(
                S.data_relation.type == 'img_m109xml'
            ).all()
        img_id_set = set(img_ids)
        xml_id_set = set(xml_ids)
        aid_set = set(r.aid for r in relations)
        bid_set = set(r.bid for r in relations)
        assert len(img_id_set) == len(aid_set)
        assert len(xml_id_set) == len(bid_set)
        assert img_id_set == aid_set
        assert xml_id_set == bid_set
        
    Q.DROP_ALL()

# TODO: move this test under test/entity/dataset
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
