"""DRF serializers for the packing app."""

from rest_framework import serializers

from .models import Box, Order, OrderItem, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "sku", "name", "length", "width", "height", "weight"]


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = [
            "id", "name", "inner_length", "inner_width", "inner_height",
            "max_weight", "cost", "is_active",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_sku", "product_name", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "reference", "created_at", "items"]


class RecommendItemInputSerializer(serializers.Serializer):
    sku = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class RecommendBoxInputSerializer(serializers.Serializer):
    items = RecommendItemInputSerializer(many=True, allow_empty=False)


class RejectionSerializer(serializers.Serializer):
    box_name = serializers.CharField()
    reason = serializers.CharField()


class RecommendedBoxSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    inner_length = serializers.DecimalField(max_digits=10, decimal_places=2)
    inner_width = serializers.DecimalField(max_digits=10, decimal_places=2)
    inner_height = serializers.DecimalField(max_digits=10, decimal_places=2)
    max_weight = serializers.DecimalField(max_digits=10, decimal_places=3)
    cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    volume = serializers.DecimalField(max_digits=20, decimal_places=6)


class RecommendationOutputSerializer(serializers.Serializer):
    fits = serializers.BooleanField()
    recommended_box = RecommendedBoxSerializer(allow_null=True)
    total_weight = serializers.DecimalField(max_digits=10, decimal_places=3)
    total_volume = serializers.DecimalField(max_digits=20, decimal_places=6)
    box_volume = serializers.DecimalField(max_digits=20, decimal_places=6)
    utilisation_pct = serializers.DecimalField(max_digits=5, decimal_places=1)
    explanation = serializers.CharField()
    rejections = RejectionSerializer(many=True)
