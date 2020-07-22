from dw.api import make
from dw.const import types
from dw.entity.data import manga109

def make_canonical_form_data_from_manga109(m109):
    print(m109)
    make.data(manga109)(m109)
