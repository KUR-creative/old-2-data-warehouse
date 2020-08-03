from pathlib import Path

import pytest
import funcy as F

from dw.api import make, put
from dw.db import orm
from dw.db import query as Q
from dw.db import schema as S
from dw.entity.data import manga109
from dw.util import file_utils as fu
from dw.util.test_utils import env_val, skipif_none


def test_put_data_from_manga109(conn, m109):
    conn, m109 = env_val(conn=conn), env_val(m109=m109)
    skipif_none(conn, m109)
    
    cfs = make.data(manga109)(m109)

    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()
    
    #put.data(cfs)
    put.canonical_forms(cfs)
    
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

@pytest.mark.skip('...')
def test_make_and_save_data_rel_chunk_and_dataset(conn, m109):
    conn, m109 = env_val(conn=conn), env_val(m109=m109)
    skipif_none(conn, m109)
    
    cfs = make.data(manga109)(m109)

    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()
    
    put.canonical_forms(cfs)
    
    with orm.session() as sess:
        #------------------------------------------------------
        # Generate relations 
        img_ids = [
            x.uuid for x in sess.query(S.data.uuid).filter(
                S.data.type == 'image').all() # TODO: remove magic-string
        ]
        
        # Save img only (identity) relations
        sess.add_all(
            S.help.identity_data_rel_rowseq(img_ids, 'only_img'))
        sess.commit()

        # Partition train/dev/test ids
        n_train = 70; n_dev = 20; n_test = 10
        total = n_train + n_dev + n_test
        
        train_ids = img_ids[:n_train]
        dev_ids = img_ids[n_train: n_train + n_dev]
        test_ids = img_ids[n_train + n_dev: total]
        assert total == len(train_ids + dev_ids + test_ids)

        #------------------------------------------------------
        # Create & Save named_relations(relations' name)
        train = NamedRelations('m109.train', 0, n_train)
        dev = NamedRelations('m109.dev', 0, n_dev)
        test = NamedRelations('m109.test', 0, n_test)
        sess.add_all([
            S.named_relations(**train._asdict()),
            S.named_relations(**dev._asdict()),
            S.named_relations(**test._asdict())])
        sess.commit()
        
        #------------------------------------------------------
        # Build and Save data_rel:rel_name relation
        rowseq = S.help.identity_named2rel_rowseq
        train_rowseq = rowseq(
            train.name, train.revision, train_ids)
        dev_rowseq = rowseq(
            dev.name, dev.revision, dev_ids)
        test_rowseq = rowseq(
            test.name, test.revision, test_ids)
        sess.add_all(F.concat(
            train_rowseq, dev_rowseq, test_rowseq))
        sess.commit()
       
        #------------------------------------------------------
        #Create dataset
        def keys(prefix):
            return F.partial(
                F.walk_keys, lambda k: f'{prefix}_{k}')
        sess.add(S.dataset(
            **keys('train')(train._asdict()),
            **keys('dev')(dev._asdict()),
            **keys('test')(test._asdict())))
    
        #------------------------------------------------------
        # Check saved numbers
        named_rels2dat_rel = S.named_relations2data_relation
        assert total == sess.query(named_rels2dat_rel).count()
        
        def assert_correct_num_of_saved_rows(name, size):
            assert sess.query(named_rels2dat_rel).filter(
                named_rels2dat_rel.name == name
            ).count() == size
            assert sess.query(named_rels2dat_rel).filter(
                named_rels2dat_rel.size == size
            ).count() == size
        assert_correct_num_of_saved_rows(train.name, train.size)
        assert_correct_num_of_saved_rows(dev.name, dev.size)
        assert_correct_num_of_saved_rows(test.name, test.size)

        # Check images: from data source = from api(db)
        
    Q.DROP_ALL()
