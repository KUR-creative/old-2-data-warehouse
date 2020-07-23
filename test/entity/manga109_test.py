from pathlib import Path

from dw.db import orm
from dw.api import make, put
from dw.const import types
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

    #orm.init
    put.data(cfs)
