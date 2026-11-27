import pytest
from app import Figure


@pytest.fixture
def square_length_10():
    """Fixture, яка повертає фігуру з довжиною 10."""
    return Figure("квадрат", 10)


@pytest.fixture(scope="module")
def shared_triangle():
    """Fixture зі scope='module' для спільного використання у кількох тестах."""
    return Figure("трикутник", 7)