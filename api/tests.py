import json
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from boxes.models import Box
from orders.models import Order, OrderItem
from products.models import Product


def _data(resp):
    return json.loads(resp.content)


class ProductAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(
            name="Widget", length=10, width=8, height=5, weight=200
        )
        self.list_url = reverse("product-list")

    def test_list_products(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_create_product(self):
        data = {"name": "Gadget", "length": 15, "width": 10, "height": 8, "weight": 500}
        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_create_product_invalid_dimensions(self):
        data = {"name": "Bad", "length": "abc", "width": 10, "height": 8, "weight": 100}
        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_product(self):
        url = reverse("product-detail", args=[self.product.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Widget")

    def test_update_product(self):
        url = reverse("product-detail", args=[self.product.id])
        resp = self.client.patch(url, {"name": "Super Widget"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Super Widget")

    def test_delete_product(self):
        url = reverse("product-detail", args=[self.product.id])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_retrieve_nonexistent_product(self):
        url = reverse("product-detail", args=[999])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class BoxAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.box = Box.objects.create(
            name="Small Box", length=20, width=15, height=10,
            max_weight=1000, cost=Decimal("2.50"),
        )
        self.list_url = reverse("box-list")

    def test_list_boxes(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_create_box(self):
        data = {
            "name": "Medium Box", "length": 30, "width": 20, "height": 15,
            "max_weight": 3000, "cost": "4.00",
        }
        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Box.objects.count(), 2)

    def test_create_box_invalid_cost(self):
        data = {
            "name": "Bad Box", "length": 10, "width": 10, "height": 10,
            "max_weight": 500, "cost": "abc",
        }
        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_box(self):
        url = reverse("box-detail", args=[self.box.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Small Box")

    def test_update_box(self):
        url = reverse("box-detail", args=[self.box.id])
        resp = self.client.patch(url, {"cost": "3.00"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.box.refresh_from_db()
        self.assertEqual(self.box.cost, Decimal("3.00"))

    def test_delete_box(self):
        url = reverse("box-detail", args=[self.box.id])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Box.objects.count(), 0)


class OrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(
            name="Widget", length=10, width=8, height=5, weight=200
        )
        self.list_url = reverse("order-list")

    def test_create_order_with_items(self):
        data = {"items": [{"product": self.product.id, "quantity": 2}]}
        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_create_order_empty_items(self):
        data = {"items": []}
        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_list_orders(self):
        Order.objects.create()
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_retrieve_order(self):
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product, quantity=3)
        url = reverse("order-detail", args=[order.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["items"]), 1)
        self.assertEqual(resp.data["items"][0]["quantity"], 3)

    def test_delete_order_cascades_items(self):
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product, quantity=1)
        url = reverse("order-detail", args=[order.id])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_create_order_with_nonexistent_product(self):
        data = {"items": [{"product": 999, "quantity": 1}]}
        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_item_format(self):
        data = {"items": [{"product": "abc", "quantity": 1}]}
        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class RecommendBoxAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(
            name="Widget", length=10, width=8, height=5, weight=200
        )
        self.box = Box.objects.create(
            name="Small Box", length=20, width=15, height=10,
            max_weight=1000, cost=Decimal("2.50"),
        )
        self.url = reverse("recommend-box")

    def _create_order(self, product_qty_pairs):
        order = Order.objects.create()
        for product, qty in product_qty_pairs:
            OrderItem.objects.create(order=order, product=product, quantity=qty)
        return order

    def test_recommends_box(self):
        order = self._create_order([(self.product, 1)])
        resp = self.client.post(self.url, {"order_id": order.id}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(_data(resp)["recommendation"]["box_id"], self.box.id)

    def test_no_recommendation_for_empty_order(self):
        order = Order.objects.create()
        resp = self.client.post(self.url, {"order_id": order.id}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(_data(resp)["recommendation"])

    def test_no_recommendation_for_too_large_product(self):
        huge = Product.objects.create(
            name="Giant", length=100, width=100, height=100, weight=50000
        )
        order = self._create_order([(huge, 1)])
        resp = self.client.post(self.url, {"order_id": order.id}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(_data(resp)["recommendation"])

    def test_recommendation_response_structure(self):
        order = self._create_order([(self.product, 1)])
        resp = self.client.post(self.url, {"order_id": order.id}, format="json")
        rec = _data(resp)["recommendation"]
        self.assertIn("box_id", rec)
        self.assertIn("box_name", rec)
        self.assertIn("cost", rec)
        self.assertIn("box_dimensions", rec)
        self.assertIn("box_max_weight", rec)
        self.assertIn("volume_utilization_pct", rec)
        self.assertIn("placements", rec)

    def test_missing_order_id(self):
        resp = self.client.post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", _data(resp))

    def test_invalid_json(self):
        resp = self.client.post(
            self.url, "not json", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", _data(resp))

    def test_nonexistent_order_id(self):
        resp = self.client.post(self.url, {"order_id": 9999}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(_data(resp)["error"], "Order not found")

    def test_get_method_not_allowed(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
