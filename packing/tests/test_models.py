"""Tests for packing.models — validation, constraints, and properties."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from packing.models import Box, Order, OrderItem, Product


class ProductModelTests(TestCase):
    """Tests for the Product model."""

    def test_create_valid_product(self):
        p = Product.objects.create(
            sku="TEST-01", name="Test Product",
            length=Decimal("10"), width=Decimal("5"), height=Decimal("3"),
            weight=Decimal("0.5"),
        )
        self.assertEqual(str(p), "TEST-01 – Test Product")

    def test_sku_uniqueness(self):
        Product.objects.create(
            sku="UNIQUE", name="First",
            length=Decimal("1"), width=Decimal("1"), height=Decimal("1"),
            weight=Decimal("0.1"),
        )
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                sku="UNIQUE", name="Duplicate",
                length=Decimal("1"), width=Decimal("1"), height=Decimal("1"),
                weight=Decimal("0.1"),
            )

    def test_zero_dimension_fails_validation(self):
        p = Product(
            sku="ZERO", name="Zero Length",
            length=Decimal("0"), width=Decimal("5"), height=Decimal("3"),
            weight=Decimal("0.5"),
        )
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_negative_weight_fails_validation(self):
        p = Product(
            sku="NEG", name="Negative Weight",
            length=Decimal("10"), width=Decimal("5"), height=Decimal("3"),
            weight=Decimal("-1"),
        )
        with self.assertRaises(ValidationError):
            p.full_clean()


class BoxModelTests(TestCase):
    """Tests for the Box model."""

    def test_create_valid_box(self):
        b = Box.objects.create(
            name="Test Box",
            inner_length=Decimal("30"), inner_width=Decimal("20"),
            inner_height=Decimal("15"), max_weight=Decimal("5"),
            cost=Decimal("3.50"),
        )
        self.assertEqual(b.volume, Decimal("9000"))
        self.assertTrue(b.is_active)

    def test_zero_cost_fails_validation(self):
        b = Box(
            name="Free Box",
            inner_length=Decimal("10"), inner_width=Decimal("10"),
            inner_height=Decimal("10"), max_weight=Decimal("5"),
            cost=Decimal("0"),
        )
        with self.assertRaises(ValidationError):
            b.full_clean()

    def test_negative_dimension_fails_validation(self):
        b = Box(
            name="Bad Box",
            inner_length=Decimal("-5"), inner_width=Decimal("10"),
            inner_height=Decimal("10"), max_weight=Decimal("5"),
            cost=Decimal("2.00"),
        )
        with self.assertRaises(ValidationError):
            b.full_clean()

    def test_box_ordering(self):
        Box.objects.create(
            name="Expensive", inner_length=Decimal("10"), inner_width=Decimal("10"),
            inner_height=Decimal("10"), max_weight=Decimal("5"), cost=Decimal("10"),
        )
        Box.objects.create(
            name="Cheap", inner_length=Decimal("10"), inner_width=Decimal("10"),
            inner_height=Decimal("10"), max_weight=Decimal("5"), cost=Decimal("1"),
        )
        boxes = list(Box.objects.values_list("name", flat=True))
        self.assertEqual(boxes[0], "Cheap")


class OrderModelTests(TestCase):
    """Tests for Order and OrderItem models."""

    def test_create_order_with_items(self):
        product = Product.objects.create(
            sku="P1", name="Product 1",
            length=Decimal("10"), width=Decimal("5"), height=Decimal("3"),
            weight=Decimal("0.5"),
        )
        order = Order.objects.create(reference="ORD-001")
        item = OrderItem.objects.create(order=order, product=product, quantity=3)
        self.assertEqual(str(item), "3× P1 in ORD-001")
        self.assertEqual(order.items.count(), 1)

    def test_order_reference_unique(self):
        Order.objects.create(reference="UNIQUE-REF")
        with self.assertRaises(IntegrityError):
            Order.objects.create(reference="UNIQUE-REF")

