from dw.api import make
from dw.const import types
from dw.entity.data import manga109

def test_make_canonical_form_data_from_manga109(m109):
    make.data(manga109)(m109)
