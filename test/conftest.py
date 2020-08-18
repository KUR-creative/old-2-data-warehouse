import pytest

def pytest_addoption(parser):
    parser.addoption("--conn", action="store", default=None)
    parser.addoption("--m109", action="store", default=None)
    parser.addoption("--snet", action="store", default=None)
    parser.addoption("--v0_m101", action="store", default=None)
    parser.addoption("--v0_school", action="store", default=None)
    parser.addoption("--cfc", action="store", default=None)
    parser.addoption("--test_cfc", action="store", default=None)

@pytest.fixture(scope="module")
def conn(request): return request.config.getoption("--conn")
@pytest.fixture(scope="module")
def m109(request): return request.config.getoption("--m109")
@pytest.fixture(scope="module")
def snet(request): return request.config.getoption("--snet")

@pytest.fixture(scope="module")
def v0_m101(request):
    return request.config.getoption("--v0_m101")
@pytest.fixture(scope="module")
def v0_school(request):
    return request.config.getoption("--v0_school")
@pytest.fixture(scope="module")
def cfc(request):
    ''' clean fmd comics '''
    return request.config.getoption("--cfc")
@pytest.fixture(scope="module")
def test_cfc(request):
    ''' clean fmd comics for test'''
    return request.config.getoption("--test_cfc")
