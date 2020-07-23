from pathlib import Path

from dw.api import make, put
from dw.const.types import DataType as DT
from dw.db import orm
from dw.db import query as Q
from dw.db import schema as S
from dw.entity.data import manga109
from dw.util import file_utils as fu
from dw.util.test_utils import skipif_none


def test_make_canonical_form_data_from_manga109(m109):
    skipif_none(m109)
    cfs = make.data(manga109)(m109)
    num_imgs = len(fu.descendants(manga109.imgdir(m109)))
    num_xmls = len(fu.descendants(manga109.xmldir(m109)))
    
    assert len(cfs) == num_imgs + num_xmls
    # assert about data type

def test_put_data_from_manga109(conn, m109):
    skipif_none(conn, m109)
    cfs = make.data(manga109)(m109)

    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()
    
    put.data(cfs)
    
    with orm.session() as sess:
        num_data = sess.query(S.data).count()
        
        num_imgs = (sess.query(S.data)
            .filter(S.data.type == DT.image.value).count())
        num_xmls = (sess.query(S.data)
            .filter(S.data.type == DT.m109xml.value).count())
        
        num_img_rows = (sess.query(S.file)
            .filter(S.file.type != 'xml').count())
        num_xml_rows = (sess.query(S.file)
            .filter(S.file.type == 'xml').count())
        
    assert num_data == num_imgs + num_xmls
    assert num_imgs == num_img_rows
    assert num_xmls == num_xml_rows
    
    Q.DROP_ALL()
