from decimal import Decimal

from django.test import TestCase

from boxes.models import Box
from orders.models import Order, OrderItem
from products.models import Product

from ..services.box_selector import recommend_box


class RecommendBoxTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Widget", length=10, width=8, height=5, weight=200
        )
        self.big_product = Product.objects.create(
            name="Big Widget", length=25, width=15, height=10, weight=800
        )
        self.rod = Product.objects.create(
            name="Rod", length=120, width=20, height=20, weight=500
        )

        self.small_box = Box.objects.create(
            name="Small", length=20, width=15, height=10,
            max_weight=1000, cost=Decimal("2.50"),
        )
        self.medium_box = Box.objects.create(
            name="Medium", length=30, width=20, height=15,
            max_weight=3000, cost=Decimal("4.00"),
        )
        self.large_box = Box.objects.create(
            name="Large", length=50, width=40, height=30,
            max_weight=10000, cost=Decimal("6.00"),
        )

    def _create_order(self, product_qty_pairs):
        order = Order.objects.create()
        for product, qty in product_qty_pairs:
            OrderItem.objects.create(order=order, product=product, quantity=qty)
        return order

    def test_returns_cheapest_fitting_box(self):
        order = self._create_order([(self.product, 1)])
        result = recommend_box(order.id)
        self.assertIsNotNone(result)
        self.assertEqual(result["box_id"], self.small_box.id)

    def test_returns_none_for_impossible_product(self):
        order = self._create_order([(self.rod, 1)])
        result = recommend_box(order.id)
        self.assertIsNone(result)

    def test_returns_none_for_empty_order(self):
        order = Order.objects.create()
        result = recommend_box(order.id)
        self.assertIsNone(result)

    def test_prefers_cheaper_box_over_larger(self):
        order = self._create_order([(self.product, 1)])
        result = recommend_box(order.id)
        self.assertEqual(result["box_id"], self.small_box.id)
        self.assertEqual(result["cost"], "2.50")

    def test_selects_larger_box_when_smaller_too_small(self):
        order = self._create_order([(self.big_product, 1)])
        result = recommend_box(order.id)
        self.assertEqual(result["box_id"], self.medium_box.id)

    def test_handles_multiple_quantity_correctly(self):
        order = self._create_order([(self.product, 3)])
        result = recommend_box(order.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result["placements"]), 3)

    def test_volume_utilization_is_reasonable(self):
        order = self._create_order([(self.product, 1)])
        result = recommend_box(order.id)
        pct = result["volume_utilization_pct"]
        self.assertGreater(pct, 0)
        self.assertLessEqual(pct, 100)

    def test_returns_expected_response_structure(self):
        order = self._create_order([(self.product, 1)])
        result = recommend_box(order.id)
        self.assertIn("box_id", result)
        self.assertIn("box_name", result)
        self.assertIn("cost", result)
        self.assertIn("box_dimensions", result)
        self.assertIn("box_max_weight", result)
        self.assertIn("volume_utilization_pct", result)
        self.assertIn("placements", result)
        for placement in result["placements"]:
            self.assertIn("product_id", placement)
            self.assertIn("position", placement)
            self.assertIn("orientation", placement)

    def test_expensive_box_not_chosen_when_cheaper_fits(self):
        cheap_box = Box.objects.create(
            name="Cheap", length=15, width=10, height=8,
            max_weight=500, cost=Decimal("1.00"),
        )
        order = self._create_order([(self.product, 1)])
        result = recommend_box(order.id)
        self.assertEqual(result["box_id"], cheap_box.id)


class OrderNotFoundTest(TestCase):
    def test_nonexistent_order_raises_404(self):
        with self.assertRaises(Exception):
            recommend_box(9999)
