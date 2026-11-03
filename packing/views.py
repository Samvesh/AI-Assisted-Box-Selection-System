"""DRF views for the packing app."""

from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Box, Order, Product
from .serializers import (
    BoxSerializer,
    OrderSerializer,
    ProductSerializer,
    RecommendationOutputSerializer,
    RecommendBoxInputSerializer,
)
from .services.box_selector import BoxDims, recommend_box


def _get_active_boxes() -> list[BoxDims]:
    """Fetch all active boxes as BoxDims dataclasses."""
    return [
        BoxDims(
            id=b.id,
            name=b.name,
            inner_length=b.inner_length,
            inner_width=b.inner_width,
            inner_height=b.inner_height,
            max_weight=b.max_weight,
            cost=b.cost,
        )
        for b in Box.objects.filter(is_active=True)
    ]


def _build_order_items_from_sku_list(items_data: list[dict]) -> tuple[list[dict], list[str]]:
    """Resolve SKUs to product data. Returns (order_items, errors)."""
    order_items = []
    errors = []
    for entry in items_data:
        sku = entry["sku"]
        qty = entry.get("quantity", 1)
        try:
            product = Product.objects.get(sku=sku)
        except Product.DoesNotExist:
            errors.append(f"Product with SKU '{sku}' not found.")
            continue
        order_items.append({
            "sku": product.sku,
            "name": product.name,
            "length": product.length,
            "width": product.width,
            "height": product.height,
            "weight": product.weight,
            "quantity": qty,
        })
    return order_items, errors


def _recommendation_to_response(result) -> Response:
    """Serialize a RecommendationResult to a DRF Response."""
    output_data = {
        "fits": result.fits,
        "recommended_box": None,
        "total_weight": result.total_weight,
        "total_volume": result.total_volume,
        "box_volume": result.box_volume,
        "utilisation_pct": result.utilisation_pct,
        "explanation": result.explanation,
        "rejections": [{"box_name": r.box_name, "reason": r.reason} for r in result.rejections],
    }
    if result.recommended_box:
        box = result.recommended_box
        output_data["recommended_box"] = {
            "id": box.id,
            "name": box.name,
            "inner_length": box.inner_length,
            "inner_width": box.inner_width,
            "inner_height": box.inner_height,
            "max_weight": box.max_weight,
            "cost": box.cost,
            "volume": box.volume,
        }
    serializer = RecommendationOutputSerializer(data=output_data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("items__product").all()
    serializer_class = OrderSerializer


@api_view(["POST"])
def recommend_box_view(request):
    serializer = RecommendBoxInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    items_data = serializer.validated_data["items"]
    order_items, errors = _build_order_items_from_sku_list(items_data)

    if errors:
        return Response(
            {"errors": errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    boxes = _get_active_boxes()
    result = recommend_box(order_items, boxes)
    return _recommendation_to_response(result)


@api_view(["GET"])
def order_recommend_box_view(request, reference):
    try:
        order = Order.objects.prefetch_related("items__product").get(reference=reference)
    except Order.DoesNotExist:
        return Response(
            {"error": f"Order '{reference}' not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    order_items_qs = order.items.select_related("product").all()
    if not order_items_qs.exists():
        return _recommendation_to_response(
            recommend_box([], _get_active_boxes())
        )

    order_items = [
        {
            "sku": oi.product.sku,
            "name": oi.product.name,
            "length": oi.product.length,
            "width": oi.product.width,
            "height": oi.product.height,
            "weight": oi.product.weight,
            "quantity": oi.quantity,
        }
        for oi in order_items_qs
    ]

    boxes = _get_active_boxes()
    result = recommend_box(order_items, boxes)
    return _recommendation_to_response(result)
