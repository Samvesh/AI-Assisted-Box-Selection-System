"""Tests for packing.services.box_selector — the core recommendation logic.

These are pure-Python unit tests that don't require the database.
"""

from decimal import Decimal

from django.test import TestCase

from packing.services.box_selector import (
    BoxDims,
    ItemDims,
    item_fits_in_box,
    recommend_box,
)


def _box(id=1, name="Box", ln=30, w=20, h=15, max_w=5, cost="3.00"):
    """Helper to create a BoxDims."""
    return BoxDims(
        id=id, name=name,
        inner_length=Decimal(str(ln)), inner_width=Decimal(str(w)),
        inner_height=Decimal(str(h)), max_weight=Decimal(str(max_w)),
        cost=Decimal(str(cost)),
    )


def _item(sku="ITEM", name="Item", ln=10, w=5, h=3, weight="0.5", qty=1):
    """Helper to create an order item dict."""
    return {
        "sku": sku, "name": name,
        "length": Decimal(str(ln)), "width": Decimal(str(w)),
        "height": Decimal(str(h)), "weight": Decimal(str(weight)),
        "quantity": qty,
    }


class ItemFitsInBoxTests(TestCase):
    """Tests for the rotation-aware individual fit check."""

    def test_item_fits_without_rotation(self):
        item = ItemDims("X", "X", Decimal("10"), Decimal("5"), Decimal("3"), Decimal("1"))
        box = _box(ln=10, w=5, h=3)
        self.assertTrue(item_fits_in_box(item, box))

    def test_item_fits_only_when_rotated(self):
        """Item 3×10×5 doesn't fit in 10×5×3 without rotation, but sorted dims match."""
        item = ItemDims("X", "X", Decimal("3"), Decimal("10"), Decimal("5"), Decimal("1"))
        box = _box(ln=10, w=5, h=3)
        self.assertTrue(item_fits_in_box(item, box))

    def test_item_does_not_fit(self):
        item = ItemDims("X", "X", Decimal("15"), Decimal("10"), Decimal("5"), Decimal("1"))
        box = _box(ln=10, w=10, h=10)
        self.assertFalse(item_fits_in_box(item, box))

    def test_item_exactly_equals_box_size(self):
        """Item dimensions exactly match box dimensions — should fit."""
        item = ItemDims("X", "X", Decimal("30"), Decimal("20"), Decimal("15"), Decimal("1"))
        box = _box(ln=30, w=20, h=15)
        self.assertTrue(item_fits_in_box(item, box))

    def test_item_one_dim_too_large(self):
        """Item is 0.01 cm too long in one dimension."""
        item = ItemDims(
            "X", "X", Decimal("30.01"), Decimal("20"), Decimal("15"), Decimal("1")
        )
        box = _box(ln=30, w=20, h=15)
        self.assertFalse(item_fits_in_box(item, box))


class RecommendBoxEmptyOrderTests(TestCase):
    """Edge case: empty order."""

    def test_empty_items_list(self):
        result = recommend_box([], [_box()])
        self.assertFalse(result.fits)
        self.assertIn("empty", result.explanation.lower())


class RecommendBoxNoBoxesTests(TestCase):
    """Edge case: no active boxes available."""

    def test_no_active_boxes(self):
        result = recommend_box([_item()], [])
        self.assertFalse(result.fits)
        self.assertIn("no active boxes", result.explanation.lower())


class RecommendBoxWeightTests(TestCase):
    """Weight-related checks."""

    def test_weight_exactly_at_limit(self):
        """Total weight exactly equals max_weight — should fit."""
        items = [_item(weight="5.000", qty=1)]
        boxes = [_box(max_w=5)]
        result = recommend_box(items, boxes)
        self.assertTrue(result.fits)

    def test_weight_exceeds_all_boxes(self):
        items = [_item(weight="10", qty=1)]
        boxes = [_box(max_w=5, name="SmallBox"), _box(id=2, max_w=8, name="BigBox")]
        result = recommend_box(items, boxes)
        self.assertFalse(result.fits)
        self.assertIn("weight", result.explanation.lower())

    def test_quantity_multiplies_weight(self):
        """3 items at 2kg each = 6kg total, exceeds 5kg box."""
        items = [_item(weight="2", qty=3)]
        boxes = [_box(max_w=5)]
        result = recommend_box(items, boxes)
        self.assertFalse(result.fits)

    def test_quantity_weight_fits(self):
        """2 items at 2kg each = 4kg total, fits in 5kg box."""
        items = [_item(weight="2", qty=2, ln=5, w=5, h=5)]
        boxes = [_box(max_w=5, ln=30, w=20, h=15)]
        result = recommend_box(items, boxes)
        self.assertTrue(result.fits)


class RecommendBoxVolumeTests(TestCase):
    """Volume-related checks."""

    def test_total_volume_exceeds_box(self):
        """Many items whose volume sum exceeds the box."""
        items = [_item(ln=10, w=10, h=10, weight="0.1", qty=5)]  # 5000 cm³
        boxes = [_box(ln=10, w=10, h=10)]  # 1000 cm³
        result = recommend_box(items, boxes)
        self.assertFalse(result.fits)
        self.assertIn("volume", result.explanation.lower())


class RecommendBoxCheapestTests(TestCase):
    """Selection priority: cheapest, then smallest, then lowest id."""

    def test_cheapest_box_selected(self):
        items = [_item(ln=5, w=5, h=5, weight="0.5")]
        boxes = [
            _box(id=1, name="Expensive", ln=30, w=20, h=15, cost="10"),
            _box(id=2, name="Cheap", ln=30, w=20, h=15, cost="2"),
            _box(id=3, name="Medium", ln=30, w=20, h=15, cost="5"),
        ]
        result = recommend_box(items, boxes)
        self.assertTrue(result.fits)
        self.assertEqual(result.recommended_box.name, "Cheap")

    def test_tiebreak_smallest_volume(self):
        """Same cost → smaller volume wins."""
        items = [_item(ln=5, w=5, h=5, weight="0.5")]
        boxes = [
            _box(id=1, name="Big", ln=30, w=30, h=30, cost="3"),
            _box(id=2, name="Small", ln=20, w=20, h=20, cost="3"),
        ]
        result = recommend_box(items, boxes)
        self.assertEqual(result.recommended_box.name, "Small")

    def test_tiebreak_lowest_id(self):
        """Same cost, same volume → lowest id wins."""
        items = [_item(ln=5, w=5, h=5, weight="0.5")]
        boxes = [
            _box(id=5, name="BoxB", ln=20, w=20, h=20, cost="3"),
            _box(id=2, name="BoxA", ln=20, w=20, h=20, cost="3"),
        ]
        result = recommend_box(items, boxes)
        self.assertEqual(result.recommended_box.name, "BoxA")
        self.assertEqual(result.recommended_box.id, 2)


class RecommendBoxRotationTests(TestCase):
    """Tests that items are properly rotated to fit."""

    def test_rotation_allows_fit(self):
        """Item 20×5×3 in a box 10×20×5 — only fits rotated (sorted: 20,5,3 vs 20,10,5)."""
        items = [_item(ln=20, w=5, h=3, weight="0.5")]
        boxes = [_box(ln=10, w=20, h=5)]
        result = recommend_box(items, boxes)
        self.assertTrue(result.fits)

    def test_no_rotation_helps(self):
        """Item 25×15×10 in a box 20×20×5 — no rotation can fix this."""
        items = [_item(ln=25, w=15, h=10, weight="0.5")]
        boxes = [_box(ln=20, w=20, h=5)]
        result = recommend_box(items, boxes)
        self.assertFalse(result.fits)


class RecommendBoxMultiItemTests(TestCase):
    """Multi-item spatial packing heuristic tests."""

    def test_two_items_fit_side_by_side(self):
        """Two 10×5×3 items in a 20×10×10 box — should fit."""
        items = [_item(sku="A", ln=10, w=5, h=3, weight="0.2", qty=2)]
        boxes = [_box(ln=20, w=10, h=10, max_w=5)]
        result = recommend_box(items, boxes)
        self.assertTrue(result.fits)

    def test_many_small_items_fit(self):
        """8 tiny cubes (2×2×2) in a 10×10×10 box. Volume OK (64/1000)."""
        items = [_item(ln=2, w=2, h=2, weight="0.01", qty=8)]
        boxes = [_box(ln=10, w=10, h=10, max_w=5)]
        result = recommend_box(items, boxes)
        self.assertTrue(result.fits)

    def test_items_individually_fit_but_not_together_by_volume(self):
        """Two 10×10×10 items (2000 cm³) in a 15×15×5 box (1125 cm³)."""
        items = [_item(ln=10, w=10, h=10, weight="0.1", qty=2)]
        boxes = [_box(ln=15, w=15, h=5)]
        result = recommend_box(items, boxes)
        self.assertFalse(result.fits)

    def test_duplicate_products_in_order(self):
        """Two entries for the same SKU — both should be counted."""
        items = [
            _item(sku="DUP", ln=10, w=5, h=3, weight="0.5", qty=1),
            _item(sku="DUP", ln=10, w=5, h=3, weight="0.5", qty=1),
        ]
        boxes = [_box(ln=20, w=10, h=10, max_w=5)]
        result = recommend_box(items, boxes)
        self.assertTrue(result.fits)
        self.assertEqual(result.total_weight, Decimal("1.0"))


class RecommendBoxNoFitTests(TestCase):
    """Tests for no-fit scenarios with clear reasons."""

    def test_item_too_large_message(self):
        items = [_item(sku="HUGE", ln=100, w=100, h=100, weight="0.1")]
        boxes = [_box(ln=50, w=50, h=50, name="OnlyBox")]
        result = recommend_box(items, boxes)
        self.assertFalse(result.fits)
        self.assertIn("HUGE", result.explanation)

    def test_all_weight_exceeded_message(self):
        items = [_item(weight="100")]
        boxes = [
            _box(id=1, name="Box1", max_w=5),
            _box(id=2, name="Box2", max_w=10),
        ]
        result = recommend_box(items, boxes)
        self.assertFalse(result.fits)
        self.assertIn("weight", result.explanation.lower())


class RecommendBoxUtilisationTests(TestCase):
    """Test that utilisation percentage is calculated correctly."""

    def test_utilisation_calculation(self):
        # Item volume = 10×10×10 = 1000, box volume = 20×20×20 = 8000
        items = [_item(ln=10, w=10, h=10, weight="0.5")]
        boxes = [_box(ln=20, w=20, h=20)]
        result = recommend_box(items, boxes)
        self.assertTrue(result.fits)
        self.assertEqual(result.utilisation_pct, Decimal("12.5"))

    def test_100_percent_utilisation(self):
        """Item fills the box completely."""
        items = [_item(ln=10, w=10, h=10, weight="0.5")]
        boxes = [_box(ln=10, w=10, h=10)]
        result = recommend_box(items, boxes)
        self.assertTrue(result.fits)
        self.assertEqual(result.utilisation_pct, Decimal("100.0"))


class RecommendBoxExplanationTests(TestCase):
    """Test that explanations are informative."""

    def test_explanation_includes_box_name(self):
        items = [_item(ln=5, w=5, h=5, weight="0.5")]
        boxes = [_box(name="Winner Box")]
        result = recommend_box(items, boxes)
        self.assertIn("Winner Box", result.explanation)

    def test_rejections_populated(self):
        items = [_item(ln=5, w=5, h=5, weight="0.5")]
        boxes = [
            _box(id=1, name="TooSmall", ln=3, w=3, h=3),
            _box(id=2, name="GoodBox", ln=20, w=20, h=20),
        ]
        result = recommend_box(items, boxes)
        self.assertTrue(result.fits)
        self.assertEqual(len(result.rejections), 1)
        self.assertEqual(result.rejections[0].box_name, "TooSmall")
