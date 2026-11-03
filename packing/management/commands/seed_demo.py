"""Seed the database with demo products, boxes, and a sample order.

Safe to run multiple times — existing data with the same SKU/name is skipped.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from packing.models import Box, Order, OrderItem, Product

PRODUCTS = [
    {
        "sku": "PHONE-01",
        "name": "Smartphone",
        "length": Decimal("15.0"),
        "width": Decimal("7.5"),
        "height": Decimal("0.8"),
        "weight": Decimal("0.200"),
    },
    {
        "sku": "LAPTOP-01",
        "name": "Laptop 15-inch",
        "length": Decimal("36.0"),
        "width": Decimal("25.0"),
        "height": Decimal("2.0"),
        "weight": Decimal("2.100"),
    },
    {
        "sku": "BOOK-01",
        "name": "Hardcover Book",
        "length": Decimal("24.0"),
        "width": Decimal("16.0"),
        "height": Decimal("3.0"),
        "weight": Decimal("0.600"),
    },
    {
        "sku": "MUG-01",
        "name": "Ceramic Mug",
        "length": Decimal("12.0"),
        "width": Decimal("10.0"),
        "height": Decimal("10.0"),
        "weight": Decimal("0.350"),
    },
    {
        "sku": "KEYBOARD-01",
        "name": "Mechanical Keyboard",
        "length": Decimal("44.0"),
        "width": Decimal("14.0"),
        "height": Decimal("4.0"),
        "weight": Decimal("1.100"),
    },
    {
        "sku": "HEADPHONES-01",
        "name": "Over-Ear Headphones",
        "length": Decimal("20.0"),
        "width": Decimal("18.0"),
        "height": Decimal("8.0"),
        "weight": Decimal("0.380"),
    },
    {
        "sku": "MONITOR-01",
        "name": "27-inch Monitor",
        "length": Decimal("65.0"),
        "width": Decimal("40.0"),
        "height": Decimal("15.0"),
        "weight": Decimal("6.500"),
    },
    {
        "sku": "MOUSE-01",
        "name": "Wireless Mouse",
        "length": Decimal("12.0"),
        "width": Decimal("6.5"),
        "height": Decimal("4.0"),
        "weight": Decimal("0.085"),
    },
]

BOXES = [
    {
        "name": "Small Mailer",
        "inner_length": Decimal("20.0"),
        "inner_width": Decimal("15.0"),
        "inner_height": Decimal("10.0"),
        "max_weight": Decimal("2.000"),
        "cost": Decimal("1.50"),
    },
    {
        "name": "Medium Box",
        "inner_length": Decimal("35.0"),
        "inner_width": Decimal("25.0"),
        "inner_height": Decimal("15.0"),
        "max_weight": Decimal("5.000"),
        "cost": Decimal("3.00"),
    },
    {
        "name": "Large Box",
        "inner_length": Decimal("50.0"),
        "inner_width": Decimal("35.0"),
        "inner_height": Decimal("25.0"),
        "max_weight": Decimal("10.000"),
        "cost": Decimal("5.50"),
    },
    {
        "name": "Extra-Large Box",
        "inner_length": Decimal("70.0"),
        "inner_width": Decimal("45.0"),
        "inner_height": Decimal("30.0"),
        "max_weight": Decimal("15.000"),
        "cost": Decimal("8.00"),
    },
    {
        "name": "Flat Pack",
        "inner_length": Decimal("40.0"),
        "inner_width": Decimal("30.0"),
        "inner_height": Decimal("5.0"),
        "max_weight": Decimal("4.000"),
        "cost": Decimal("2.50"),
    },
]


class Command(BaseCommand):
    help = "Seed the database with demo products, boxes, and a sample order."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # Products
        for p_data in PRODUCTS:
            obj, created = Product.objects.get_or_create(
                sku=p_data["sku"], defaults=p_data
            )
            status = "created" if created else "already exists"
            self.stdout.write(f"  Product {obj.sku}: {status}")

        # Boxes
        for b_data in BOXES:
            obj, created = Box.objects.get_or_create(
                name=b_data["name"], defaults=b_data
            )
            status = "created" if created else "already exists"
            self.stdout.write(f"  Box '{obj.name}': {status}")

        # Sample order
        order, created = Order.objects.get_or_create(reference="DEMO-001")
        if created:
            phone = Product.objects.get(sku="PHONE-01")
            book = Product.objects.get(sku="BOOK-01")
            OrderItem.objects.create(order=order, product=phone, quantity=1)
            OrderItem.objects.create(order=order, product=book, quantity=2)
            self.stdout.write("  Order DEMO-001: created (1× phone, 2× book)")
        else:
            self.stdout.write("  Order DEMO-001: already exists")

        self.stdout.write(self.style.SUCCESS("\nDone! Try:"))
        self.stdout.write("  curl http://localhost:8000/api/orders/DEMO-001/recommend-box/")
        self.stdout.write(
            '  curl -X POST http://localhost:8000/api/recommend-box/ '
            '-H "Content-Type: application/json" '
            '-d \'{"items": [{"sku": "LAPTOP-01", "quantity": 1}]}\''
        )
