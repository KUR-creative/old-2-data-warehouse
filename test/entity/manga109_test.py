from pathlib import Path

import pytest

from dw.api import make, put
from dw.const.types import DataType as DT
from dw.db import orm
from dw.db import query as Q
from dw.db import schema as S
from dw.entity.data import manga109
from dw.util import file_utils as fu
from dw.util.test_utils import env_val, skipif_none


def test_make_canonical_form_data_from_manga109(m109):
    m109 = env_val(m109=m109)
    skipif_none(m109)
    
    cfs = make.data(manga109)(m109)
    num_imgs = len(fu.descendants(manga109.imgdir(m109)))
    num_xmls = len(fu.descendants(manga109.xmldir(m109)))
    
    assert len(cfs) == num_imgs + num_xmls
    # assert about data type

#@pytest.mark.skip('...')
def test_put_data_from_manga109(conn, m109):
    conn, m109 = env_val(conn=conn), env_val(m109=m109)
    skipif_none(conn, m109)
    
    cfs = make.data(manga109)(m109)

    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()
    
    put.data(cfs)
    
    with orm.session() as sess:
        img_ids = [
            x.uuid for x in
            sess.query(S.data.uuid).filter(
                S.data.type == DT.image.value).all()]
        xml_ids = [
            x.uuid for x in
            sess.query(S.data.uuid).filter(
            S.data.type == DT.m109xml.value).all()]
        
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
            S.data_rel.aid, S.data_rel.bid).filter(
                S.data_rel.type == 'img_m109xml'
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

def test_make_and_save_data_rel_chunk(conn, m109):
    conn, m109 = env_val(conn=conn), env_val(m109=m109)
    skipif_none(conn, m109)
    
    cfs = make.data(manga109)(m109)

    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()
    
    put.data(cfs)
    
    # create only img rels(img=img) for m109 images
    # db -> imgs
    # imgs -> img:img rels
    with orm.session() as sess:
        img_ids = [
            x.uuid for x in sess.query(S.data.uuid).filter(
                S.data.type == DT.image.value).all()
        ]
        
        # Save img only relations
        sess.add_all(
            S.data_rel(aid=iid, bid=iid, type='only_img')
            for iid in img_ids)
        sess.commit()

        # Partition train/dev/test ids
        n_train = 70
        n_dev = 20
        n_test = 10
        total = n_train + n_dev + n_test
        
        train_ids = img_ids[:n_train]
        dev_ids = img_ids[n_train: n_train + n_dev]
        test_ids = img_ids[n_train + n_dev: total]
        assert total == len(train_ids + dev_ids + test_ids)

        # Save chunks
        train_rows = [
            S.data_rel_chunk(
                name='m109.train', revision=0, size=n_train,
                inp=iid, out=iid)
            for iid in train_ids]
        dev_rows = [
            S.data_rel_chunk(
                name='m109.dev', revision=0, size=n_dev,
                inp=iid, out=iid)
            for iid in dev_ids]
        test_rows = [
            S.data_rel_chunk(
                name='m109.test', revision=0, size=n_test,
                inp=iid, out=iid)
            for iid in test_ids]
        all_rows = train_rows + dev_rows + test_rows

        sess.add_all(all_rows)
        sess.commit()
    
        # Check saved numbers
        assert sess.query(S.data_rel_chunk).count() == total
        
        def assert_correct_num_of_saved_rows(name, size):
            assert sess.query(S.data_rel_chunk).filter(
                S.data_rel_chunk.name == name
            ).count() == size
            assert sess.query(S.data_rel_chunk).filter(
                S.data_rel_chunk.size == size
            ).count() == size
        assert_correct_num_of_saved_rows('m109.train', n_train)
        assert_correct_num_of_saved_rows('m109.dev', n_dev)
        assert_correct_num_of_saved_rows('m109.test', n_test)
        # assert size of chunk
        #rows = sess.query(S.data_rel).filter(S.data_rel.type == 'only_img').all()
        
    Q.DROP_ALL()
    # get relations from db
    # shuffle and partition in 3 parts.
    # naming relations and save to db
    # get chunk from db
    
    # assert set(relations from 3 chunks) == ma109 rels in db

    # create m109 dataset with 3 chunks
    # save to db
    pass
