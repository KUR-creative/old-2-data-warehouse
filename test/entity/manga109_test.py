from pathlib import Path

from dw.api import make
from dw.const import types
from dw.entity.data import manga109
from dw.util import file_utils as fu


def test_make_canonical_form_data_from_manga109(m109):
    cfs = make.data(manga109)(m109)
    img_dir = Path(m109, 'images')
    xml_dir = Path(m109, 'manga109-annotations')
    num_imgs = len(fu.descendants(img_dir))
    num_xmls = len(fu.descendants(xml_dir))
    
    assert len(cfs) == num_imgs + num_xmls
    # assert about data type
