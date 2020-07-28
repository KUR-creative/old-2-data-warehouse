import pytest


def skipif_none(*candidates):
    for fixture in candidates:
        if fixture is None:
            pytest.skip('Some fixture is None')
            return
