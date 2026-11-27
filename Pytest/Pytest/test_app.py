import pytest
from app import Figure


# 1. Базові тести + ⭐ маркер unit для двох тестів
@pytest.mark.unit
def test_triangle_type():
    triangle = Figure("трикутник", 4)
    assert triangle.type == "трикутник"


@pytest.mark.unit
def test_invalid_length():
    with pytest.raises(AssertionError):
        Figure("квадрат", 0)


# 2. ⭐ Параметризований тест для всіх дозволених фігур
@pytest.mark.parametrize("figure", Figure.FIGURES)
def test_allowed_figure(figure):
    assert Figure(figure, 1).type == figure


# 3. ⭐ Перевірка властивостей фігури з довжиною 10 (fixture з conftest.py)
def test_figure_length_10_properties(square_length_10):
    assert square_length_10.type == "квадрат"
    assert square_length_10.get_figure_type == "квадрат"
    assert square_length_10.get_figure_length == 10


# 4. 🔥 Тест для кожного неправильного типу та кожного неправильного значення довжини
@pytest.mark.parametrize("invalid_type", ["коло", "ромб", "п'ятикутник", "", 123, None])
def test_all_invalid_types(invalid_type):
    with pytest.raises(AssertionError):
        Figure(invalid_type, 5)


@pytest.mark.parametrize("invalid_length", [0, -1, -50, "5", None])
def test_all_invalid_lengths(invalid_length):
    with pytest.raises((AssertionError, TypeError)):
        Figure("трикутник", invalid_length)


# 5. ⭐ Використання fixture зі scope="module" у двох різних тестах
def test_shared_triangle_type(shared_triangle):
    assert shared_triangle.type == "трикутник"


def test_shared_triangle_length(shared_triangle):
    assert shared_triangle.get_figure_length == 7