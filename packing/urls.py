"""URL configuration for the packing app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"products", views.ProductViewSet)
router.register(r"boxes", views.BoxViewSet)
router.register(r"orders", views.OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("recommend-box/", views.recommend_box_view, name="recommend-box"),
    path(
        "orders/<str:reference>/recommend-box/",
        views.order_recommend_box_view,
        name="order-recommend-box",
    ),
]

