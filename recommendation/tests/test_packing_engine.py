from decimal import Decimal

from django.test import TestCase

from boxes.models import Box
from products.models import Product

from ..services.packing_engine import Void, _fits_in_void, _split_void, _unique_orientations, can_fit


class UniqueOrientationsTest(TestCase):
    def test_all_dimensions_unique(self):
        dims = _unique_orientations(10, 8, 5)
        self.assertEqual(len(dims), 6)

    def test_two_dimensions_equal(self):
        dims = _unique_orientations(10, 10, 5)
        self.assertEqual(len(dims), 3)

    def test_all_dimensions_equal(self):
        dims = _unique_orientations(5, 5, 5)
        self.assertEqual(len(dims), 1)


class FitsInVoidTest(TestCase):
    def test_exact_fit(self):
        void = Void(0, 0, 0, 10, 10, 10)
        self.assertTrue(_fits_in_void((10, 10, 10), void))

    def test_smaller_fits(self):
        void = Void(0, 0, 0, 20, 15, 10)
        self.assertTrue(_fits_in_void((10, 8, 5), void))

    def test_too_large_in_one_dimension(self):
        void = Void(0, 0, 0, 10, 10, 10)
        self.assertFalse(_fits_in_void((12, 8, 5), void))

    def test_too_large_in_all_dimensions(self):
        void = Void(0, 0, 0, 10, 10, 10)
        self.assertFalse(_fits_in_void((15, 12, 11), void))


class SplitVoidTest(TestCase):
    def test_split_creates_three_voids(self):
        void = Void(0, 0, 0, 20, 15, 10)
        result = _split_void(void, (10, 8, 5))
        self.assertEqual(len(result), 3)

    def test_split_right_void_position(self):
        void = Void(0, 0, 0, 20, 15, 10)
        result = _split_void(void, (10, 8, 5))
        right = [v for v in result if v.x == 10][0]
        self.assertEqual(right.l, 10)
        self.assertEqual(right.w, 15)
        self.assertEqual(right.h, 10)

    def test_split_front_void_position(self):
        void = Void(0, 0, 0, 20, 15, 10)
        result = _split_void(void, (10, 8, 5))
        front = [v for v in result if v.y == 8][0]
        self.assertEqual(front.l, 20)
        self.assertEqual(front.w, 7)
        self.assertEqual(front.h, 10)

    def test_split_top_void_position(self):
        void = Void(0, 0, 0, 20, 15, 10)
        result = _split_void(void, (10, 8, 5))
        top = [v for v in result if v.z == 5][0]
        self.assertEqual(top.l, 20)
        self.assertEqual(top.w, 15)
        self.assertEqual(top.h, 5)

    def test_split_item_uses_full_width_skips_front_void(self):
        void = Void(0, 0, 0, 20, 15, 10)
        result = _split_void(void, (10, 15, 5))
        self.assertEqual(len(result), 2)
        self.assertFalse(any(v.y != 0 for v in result if v.x != 10))


class CanFitTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Widget", length=10, width=8, height=5, weight=200
        )
        self.box = Box.objects.create(
            name="Test Box", length=30, width=20, height=15, max_weight=3000, cost=Decimal("5.00")
        )

    def test_single_product_fits(self):
        fits, placements = can_fit([(self.product, 1)], self.box)
        self.assertTrue(fits)
        self.assertEqual(len(placements), 1)

    def test_exact_fit(self):
        box = Box.objects.create(
            name="Exact Box", length=10, width=8, height=5, max_weight=1000, cost=Decimal("3.00")
        )
        fits, placements = can_fit([(self.product, 1)], box)
        self.assertTrue(fits)
        self.assertEqual(len(placements), 1)

    def test_product_too_large(self):
        box = Box.objects.create(
            name="Tiny Box", length=5, width=5, height=5, max_weight=1000, cost=Decimal("1.00")
        )
        fits, _ = can_fit([(self.product, 1)], box)
        self.assertFalse(fits)

    def test_exceeds_weight_capacity(self):
        box = Box.objects.create(
            name="Weak Box", length=50, width=50, height=50, max_weight=100, cost=Decimal("2.00")
        )
        fits, _ = can_fit([(self.product, 1)], box)
        self.assertFalse(fits)

    def test_rod_fits_with_rotation(self):
        rod = Product.objects.create(
            name="Rod", length=120, width=10, height=10, weight=500
        )
        box = Box.objects.create(
            name="Long Box", length=10, width=10, height=130, max_weight=5000, cost=Decimal("6.00")
        )
        fits, placements = can_fit([(rod, 1)], box)
        self.assertTrue(fits)
        self.assertEqual(len(placements), 1)
        placed = placements[0]
        self.assertEqual(placed.h, 120)

    def test_rod_too_long_for_any_orientation(self):
        rod = Product.objects.create(
            name="Long Rod", length=200, width=10, height=10, weight=500
        )
        box = Box.objects.create(
            name="Small Box", length=100, width=100, height=100, max_weight=5000, cost=Decimal("6.00")
        )
        fits, _ = can_fit([(rod, 1)], box)
        self.assertFalse(fits)

    def test_multiple_quantity(self):
        fits, placements = can_fit([(self.product, 3)], self.box)
        self.assertTrue(fits)
        self.assertEqual(len(placements), 3)
        positions = {
            (p.x, p.y, p.z)
            for p in placements
        }
        self.assertEqual(len(positions), 3)

    def test_multiple_different_products(self):
        small = Product.objects.create(
            name="Mini", length=5, width=5, height=5, weight=50
        )
        fits, placements = can_fit([(self.product, 1), (small, 2)], self.box)
        self.assertTrue(fits)
        self.assertEqual(len(placements), 3)

    def test_large_product_and_small_product(self):
        box = Box.objects.create(
            name="Cube Box", length=10, width=10, height=10, max_weight=5000, cost=Decimal("4.00")
        )
        large = Product.objects.create(
            name="Large", length=8, width=8, height=8, weight=300
        )
        small = Product.objects.create(
            name="Small", length=2, width=10, height=10, weight=100
        )
        fits, _ = can_fit([(small, 1), (large, 1)], box)
        self.assertTrue(fits)

    def test_awkward_shape_orientation(self):
        box = Box.objects.create(
            name="Flat Box 2", length=15, width=20, height=10, max_weight=5000, cost=Decimal("4.00")
        )
        awkward = Product.objects.create(
            name="Awkward", length=20, width=15, height=10, weight=500
        )
        fits, placements = can_fit([(awkward, 1)], box)
        self.assertTrue(fits)
        self.assertEqual(len(placements), 1)

    def test_empty_product_list(self):
        fits, placements = can_fit([], self.box)
        self.assertTrue(fits)
        self.assertEqual(placements, [])

    def test_quantity_respects_weight_limit(self):
        heavy = Product.objects.create(
            name="Heavy", length=5, width=5, height=5, weight=1000
        )
        box = Box.objects.create(
            name="Box", length=50, width=50, height=50, max_weight=2500, cost=Decimal("5.00")
        )
        fits, _ = can_fit([(heavy, 3)], box)
        self.assertFalse(fits)

    def test_flat_product_fits_flat_box(self):
        box = Box.objects.create(
            name="Flat Box", length=100, width=100, height=1, max_weight=5000, cost=Decimal("4.00")
        )
        flat = Product.objects.create(
            name="Flat Mat", length=50, width=50, height=1, weight=200
        )
        fits, placements = can_fit([(flat, 1)], box)
        self.assertTrue(fits)
        self.assertEqual(len(placements), 1)


class PlacementDataTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Widget", length=10, width=8, height=5, weight=200
        )
        self.box = Box.objects.create(
            name="Test Box", length=30, width=20, height=15, max_weight=3000, cost=Decimal("5.00")
        )

    def test_placement_has_correct_product_id(self):
        _, placements = can_fit([(self.product, 1)], self.box)
        self.assertEqual(placements[0].product_id, self.product.id)

    def test_placement_dimensions_match_product_orientation(self):
        _, placements = can_fit([(self.product, 1)], self.box)
        placed = placements[0]
        self.assertEqual(placed.l * placed.w * placed.h, 10 * 8 * 5)
