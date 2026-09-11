import unittest
from classify_triangle import classify_triangle


class TestClassifyTriangle(unittest.TestCase):

    def test_equilateral(self):
        self.assertEqual(classify_triangle(5, 5, 5), "Equilateral, not a right triangle")

    def test_equilateral_small_values(self):
        self.assertEqual(classify_triangle(1, 1, 1), "Equilateral, not a right triangle")

    def test_isosceles_ab_equal(self):
        self.assertEqual(classify_triangle(5, 5, 8), "Isosceles, not a right triangle")

    def test_isosceles_bc_equal(self):
        self.assertEqual(classify_triangle(8, 5, 5), "Isosceles, not a right triangle")

    def test_isosceles_ac_equal(self):
        self.assertEqual(classify_triangle(5, 8, 5), "Isosceles, not a right triangle")

    def test_isosceles_right_triangle(self):
        self.assertEqual(classify_triangle(1, 1, 2 ** 0.5), "Isosceles, right triangle")

    def test_scalene(self):
        self.assertEqual(classify_triangle(4, 5, 6), "Scalene, not a right triangle")

    def test_scalene_right_triangle_3_4_5(self):
        self.assertEqual(classify_triangle(3, 4, 5), "Scalene, right triangle")

    def test_scalene_right_triangle_any_order(self):
        self.assertEqual(classify_triangle(5, 3, 4), "Scalene, right triangle")
        self.assertEqual(classify_triangle(4, 5, 3), "Scalene, right triangle")

    def test_scalene_right_triangle_5_12_13(self):
        self.assertEqual(classify_triangle(5, 12, 13), "Scalene, right triangle")

    def test_invalid_sum_too_small(self):
        self.assertEqual(classify_triangle(1, 2, 10), "Not a valid triangle")

    def test_invalid_degenerate_triangle(self):
        self.assertEqual(classify_triangle(1, 2, 3), "Not a valid triangle")

    def test_invalid_zero_side(self):
        self.assertEqual(classify_triangle(0, 4, 5), "Not a valid triangle")

    def test_invalid_negative_side(self):
        self.assertEqual(classify_triangle(-3, 4, 5), "Not a valid triangle")

    def test_invalid_all_zero(self):
        self.assertEqual(classify_triangle(0, 0, 0), "Not a valid triangle")

    def test_float_sides_scalene_right(self):
        self.assertEqual(classify_triangle(3.0, 4.0, 5.0), "Scalene, right triangle")

    def test_float_sides_equilateral(self):
        self.assertEqual(classify_triangle(2.5, 2.5, 2.5), "Equilateral, not a right triangle")


if __name__ == "__main__":
    unittest.main()