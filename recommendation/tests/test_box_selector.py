from decimal import Decimal
from unittest.mock import patch

from django.http import Http404
from django.test import TestCase

from boxes.models import Box
from orders.models import Order, OrderItem
from products.models import Product

from ..services.ai_explainer import AIRecommendationExplainer
from ..services.box_selector import recommend_box


class RecommendBoxTest(TestCase):
    """Tests for recommend_box(): selects the cheapest box that can fit all items."""

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

    def test_returns_none_for_impossible_product(self):
        """No box can fit the product dimensions → returns None."""
        order = self._create_order([(self.rod, 1)])
        result = recommend_box(order.id)
        self.assertIsNone(result)

    def test_returns_none_for_empty_order(self):
        """Order with no items → returns None."""
        order = Order.objects.create()
        result = recommend_box(order.id)
        self.assertIsNone(result)

    def test_prefers_cheaper_box_over_larger(self):
        """Among multiple fitting boxes, the cheapest cost is chosen."""
        order = self._create_order([(self.product, 1)])
        result = recommend_box(order.id)
        self.assertEqual(result["box_id"], self.small_box.id)
        self.assertEqual(result["cost"], "2.50")

    def test_selects_larger_box_when_smaller_too_small(self):
        """When the smallest box is too small, the next cheapest that fits is chosen."""
        order = self._create_order([(self.big_product, 1)])
        result = recommend_box(order.id)
        self.assertEqual(result["box_id"], self.medium_box.id)

    def test_quantity_affects_box_selection(self):
        """Multiple items increase weight/volume — smallest box no longer fits."""
        order = self._create_order([(self.product, 6)])
        result = recommend_box(order.id)
        self.assertIsNotNone(result)
        self.assertNotEqual(result["box_id"], self.small_box.id)

    def test_skips_box_with_insufficient_weight_capacity(self):
        """Box with max_weight < total_weight is excluded from results."""
        heavy = Product.objects.create(
            name="Heavy", length=5, width=5, height=5, weight=1500
        )
        order = self._create_order([(heavy, 1)])
        result = recommend_box(order.id)
        self.assertIsNotNone(result)
        self.assertEqual(result["box_id"], self.medium_box.id)

    def test_volume_utilization_is_reasonable(self):
        """Volume utilization percentage is between 0% and 100%."""
        order = self._create_order([(self.product, 1)])
        result = recommend_box(order.id)
        pct = result["volume_utilization_pct"]
        self.assertGreater(pct, 0)
        self.assertLessEqual(pct, 100)

    def test_returns_expected_response_structure(self):
        """Response dict contains all expected keys with correct nested structure."""
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
        self.assertIn("explanation", result)

    def test_ai_explanation_included_when_api_key_set(self):
        """AI explanation is generated when GEMINI_API_KEY is configured."""
        mock_response = {
            "recommended_box": "Small",
            "reason": "Small box fits all items, supports total weight and has the lowest cost."
        }
        with patch.object(AIRecommendationExplainer, "explain", return_value=mock_response):
            with self.settings(GEMINI_API_KEY="sk-test"):
                order = self._create_order([(self.product, 1)])
                result = recommend_box(order.id)
                self.assertEqual(result["explanation"], mock_response)

class OrderNotFoundTest(TestCase):
    """Tests for invalid order ID handling."""

    def test_nonexistent_order_raises_404(self):
        """Calling recommend_box with a non-existent ID raises an exception."""
        with self.assertRaises(Http404):
            recommend_box(9999)
