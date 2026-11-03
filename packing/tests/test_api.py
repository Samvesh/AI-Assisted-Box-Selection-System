"""Tests for the packing API endpoints."""

from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from packing.models import Box, Order, OrderItem, Product


class APITestBase(TestCase):
    """Base class with common setup for API tests."""

    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(
            sku="WIDGET-01", name="Widget",
            length=Decimal("10"), width=Decimal("5"), height=Decimal("3"),
            weight=Decimal("0.5"),
        )
        self.box = Box.objects.create(
            name="Standard Box",
            inner_length=Decimal("30"), inner_width=Decimal("20"),
            inner_height=Decimal("15"), max_weight=Decimal("5"),
            cost=Decimal("3.00"),
        )


class RecommendBoxAPITests(APITestBase):
    """Tests for POST /api/recommend-box/."""

    def test_success(self):
        resp = self.client.post(
            "/api/recommend-box/",
            {"items": [{"sku": "WIDGET-01", "quantity": 1}]},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["fits"])
        self.assertEqual(data["recommended_box"]["name"], "Standard Box")

    def test_unknown_sku(self):
        resp = self.client.post(
            "/api/recommend-box/",
            {"items": [{"sku": "NONEXISTENT", "quantity": 1}]},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("errors", data)
        self.assertIn("NONEXISTENT", data["errors"][0])

    def test_empty_items(self):
        resp = self.client.post(
            "/api/recommend-box/",
            {"items": []},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_missing_items_field(self):
        resp = self.client.post(
            "/api/recommend-box/",
            {},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_invalid_quantity(self):
        resp = self.client.post(
            "/api/recommend-box/",
            {"items": [{"sku": "WIDGET-01", "quantity": 0}]},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_multiple_items(self):
        Product.objects.create(
            sku="GADGET-01", name="Gadget",
            length=Decimal("8"), width=Decimal("4"), height=Decimal("2"),
            weight=Decimal("0.3"),
        )
        resp = self.client.post(
            "/api/recommend-box/",
            {"items": [
                {"sku": "WIDGET-01", "quantity": 2},
                {"sku": "GADGET-01", "quantity": 1},
            ]},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["fits"])

    def test_no_fit_returns_200_with_fits_false(self):
        """Even when nothing fits, we return 200 with fits=false, not 500."""
        Product.objects.create(
            sku="HUGE-01", name="Huge Item",
            length=Decimal("100"), width=Decimal("100"), height=Decimal("100"),
            weight=Decimal("50"),
        )
        resp = self.client.post(
            "/api/recommend-box/",
            {"items": [{"sku": "HUGE-01", "quantity": 1}]},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data["fits"])
        self.assertIsNone(data["recommended_box"])


class OrderRecommendBoxAPITests(APITestBase):
    """Tests for GET /api/orders/<reference>/recommend-box/."""

    def test_success(self):
        order = Order.objects.create(reference="TEST-001")
        OrderItem.objects.create(order=order, product=self.product, quantity=1)
        resp = self.client.get("/api/orders/TEST-001/recommend-box/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["fits"])

    def test_order_not_found(self):
        resp = self.client.get("/api/orders/NOPE/recommend-box/")
        self.assertEqual(resp.status_code, 404)

    def test_empty_order(self):
        Order.objects.create(reference="EMPTY-001")
        resp = self.client.get("/api/orders/EMPTY-001/recommend-box/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["fits"])


class ProductCRUDTests(TestCase):
    """Tests for the Product CRUD viewset."""

    def setUp(self):
        self.client = APIClient()

    def test_list_products(self):
        Product.objects.create(
            sku="P1", name="Product 1",
            length=Decimal("10"), width=Decimal("5"), height=Decimal("3"),
            weight=Decimal("0.5"),
        )
        resp = self.client.get("/api/products/")
        self.assertEqual(resp.status_code, 200)

    def test_create_product(self):
        resp = self.client.post(
            "/api/products/",
            {"sku": "NEW-01", "name": "New", "length": 10, "width": 5,
             "height": 3, "weight": "0.5"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)


class BoxCRUDTests(TestCase):
    """Tests for the Box CRUD viewset."""

    def setUp(self):
        self.client = APIClient()

    def test_list_boxes(self):
        resp = self.client.get("/api/boxes/")
        self.assertEqual(resp.status_code, 200)

    def test_create_box(self):
        resp = self.client.post(
            "/api/boxes/",
            {"name": "Test Box", "inner_length": 30, "inner_width": 20,
             "inner_height": 15, "max_weight": "5.0", "cost": "3.00",
             "is_active": True},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
