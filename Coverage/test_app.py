import pytest
from app import Figure


@pytest.mark.parametrize("figure", Figure.FIGURES)
def test_allowed_figures(figure):
    obj = Figure(figure, 5)
    assert obj.get_figure_type == figure
    assert obj.get_figure_length == 5


@pytest.mark.parametrize(
    "figure, expected_angles",
    [
        ("квадрат", 4),
        ("прямокутник", 4),
        ("трикутник", 3),
    ],
)
def test_get_angles_all_branches(figure, expected_angles):
    obj = Figure(figure, 4)
    assert obj.get_angles == expected_angles


@pytest.mark.parametrize("invalid_type", ["коло", "ромб", "", None])
def test_invalid_figure_type(invalid_type):
    with pytest.raises(AssertionError):
        Figure(invalid_type, 3)


@pytest.mark.parametrize("invalid_length", [0, -1, -10])
def test_invalid_figure_length(invalid_length):
    with pytest.raises(AssertionError):
        Figure("квадрат", invalid_length)