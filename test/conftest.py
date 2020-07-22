import pytest

def pytest_addoption(parser):
    parser.addoption("--conn", action="store", default=None)
    parser.addoption("--m109", action="store", default=None)

#@fixture()
@pytest.fixture(scope="module")
def conn(request): return request.config.getoption("--conn")
@pytest.fixture(scope="module")
def m109(request): return request.config.getoption("--m109")
