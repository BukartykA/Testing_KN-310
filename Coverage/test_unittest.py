import unittest
from app import Figure


class TestFigureUnittest(unittest.TestCase):
    def test_triangle_type(self):
        triangle = Figure("трикутник", 4)
        self.assertEqual(triangle.get_figure_type, "трикутник")

    def test_triangle_angles(self):
        triangle = Figure("трикутник", 4)
        self.assertEqual(triangle.get_angles, 3)

    def test_invalid_length(self):
        with self.assertRaises(AssertionError):
            Figure("квадрат", 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()