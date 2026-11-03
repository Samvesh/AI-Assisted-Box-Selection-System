from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    """A product that can be shipped. Dimensions in cm, weight in kg."""

    sku = models.CharField(max_length=50, unique=True, help_text="Unique stock-keeping unit")
    name = models.CharField(max_length=200)
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Length in cm",
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Width in cm",
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Height in cm",
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
        help_text="Weight in kg",
    )

    class Meta:
        ordering = ["sku"]
        constraints = [
            models.CheckConstraint(condition=models.Q(length__gt=0), name="product_length_positive"),
            models.CheckConstraint(condition=models.Q(width__gt=0), name="product_width_positive"),
            models.CheckConstraint(condition=models.Q(height__gt=0), name="product_height_positive"),
            models.CheckConstraint(condition=models.Q(weight__gt=0), name="product_weight_positive"),
        ]

    def __str__(self) -> str:
        return f"{self.sku} – {self.name}"


class Box(models.Model):
    """A shipping box. Dimensions are internal dimensions in cm."""

    name = models.CharField(max_length=200)
    inner_length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Inner length in cm",
    )
    inner_width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Inner width in cm",
    )
    inner_height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Inner height in cm",
    )
    max_weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
        help_text="Maximum weight capacity in kg",
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Cost per box in currency units",
    )
    is_active = models.BooleanField(default=True, help_text="Inactive boxes are not considered")

    class Meta:
        ordering = ["cost", "name"]
        verbose_name_plural = "boxes"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(inner_length__gt=0), name="box_inner_length_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(inner_width__gt=0), name="box_inner_width_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(inner_height__gt=0), name="box_inner_height_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(max_weight__gt=0), name="box_max_weight_positive"
            ),
            models.CheckConstraint(condition=models.Q(cost__gt=0), name="box_cost_positive"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.inner_length}×{self.inner_width}×{self.inner_height} cm)"

    @property
    def volume(self) -> Decimal:
        """Internal volume in cm³."""
        return self.inner_length * self.inner_width * self.inner_height


class Order(models.Model):
    """A customer order."""

    reference = models.CharField(max_length=100, unique=True, help_text="Unique order reference")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order {self.reference}"


class OrderItem(models.Model):
    """A line item in an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of units",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gte=1), name="orderitem_qty_min_1"),
        ]

    def __str__(self) -> str:
        return f"{self.quantity}× {self.product.sku} in {self.order.reference}"
