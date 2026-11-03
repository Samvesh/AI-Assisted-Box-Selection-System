"""Box selection service — pure Python logic, no Django view/request handling.

This module implements the core box recommendation algorithm for an e-commerce
warehouse packing system. Given a list of order items (product + quantity),
it determines which active shipping box best fits the order.

Algorithm overview
==================
The selector uses a **greedy layer-packing heuristic**:

1. **Weight check**: Total order weight must be ≤ box max_weight.
2. **Individual fit check**: Each item, when optimally rotated, must fit inside
   the box dimensions. We check all 6 axis-aligned orientations by sorting
   item dims and box dims descending and comparing pairwise.
3. **Volume check**: Sum of all item volumes must be ≤ box inner volume.
4. **Layer-packing heuristic** (multi-item spatial feasibility):
   - Sort items by volume descending (largest first).
   - Pack items into horizontal layers along the box height axis.
   - Within each layer, place items in rows using a shelf algorithm.
   - Items may be rotated to choose the orientation that best uses the
     remaining layer/row space.
   - If all items are placed without exceeding the box dimensions, the
     box passes.

What this heuristic **can** guarantee:
  - If it says "fits", the items genuinely fit (dimensions are respected).
  - It always finds a valid packing when items are uniform or nearly so.

What it **cannot** guarantee:
  - It may reject boxes that a more sophisticated algorithm (or a human)
    could pack successfully. 3D bin packing is NP-hard, and this greedy
    approach does not explore all possible arrangements.
  - It does not account for irregular shapes, fragile items, or padding.

Selection priority (among passing boxes):
  1. Cheapest cost
  2. Smallest inner volume (tie-break)
  3. Lowest database id (final tie-break for determinism)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from itertools import permutations


@dataclass
class ItemDims:
    """Dimensions and weight of a single physical item."""

    sku: str
    name: str
    length: Decimal
    width: Decimal
    height: Decimal
    weight: Decimal

    @property
    def volume(self) -> Decimal:
        return self.length * self.width * self.height

    @property
    def sorted_dims(self) -> tuple[Decimal, Decimal, Decimal]:
        """Dimensions sorted descending."""
        d = sorted([self.length, self.width, self.height], reverse=True)
        return (d[0], d[1], d[2])


@dataclass
class BoxDims:
    """Dimensions, capacity, and cost of a shipping box."""

    id: int
    name: str
    inner_length: Decimal
    inner_width: Decimal
    inner_height: Decimal
    max_weight: Decimal
    cost: Decimal

    @property
    def volume(self) -> Decimal:
        return self.inner_length * self.inner_width * self.inner_height

    @property
    def sorted_dims(self) -> tuple[Decimal, Decimal, Decimal]:
        d = sorted([self.inner_length, self.inner_width, self.inner_height], reverse=True)
        return (d[0], d[1], d[2])


@dataclass
class RejectionReason:
    """Why a specific box was rejected."""

    box_name: str
    reason: str


@dataclass
class RecommendationResult:
    """Result of a box recommendation attempt."""

    fits: bool
    recommended_box: BoxDims | None = None
    total_weight: Decimal = Decimal("0")
    total_volume: Decimal = Decimal("0")
    box_volume: Decimal = Decimal("0")
    utilisation_pct: Decimal = Decimal("0")
    explanation: str = ""
    rejections: list[RejectionReason] = field(default_factory=list)


def item_fits_in_box(item: ItemDims, box: BoxDims) -> bool:
    """Check if a single item fits in any of the 6 axis-aligned orientations.

    Sorting both item and box dims descending and comparing pairwise is
    equivalent to testing all 6 rotation permutations.
    """
    item_d = item.sorted_dims
    box_d = box.sorted_dims
    return item_d[0] <= box_d[0] and item_d[1] <= box_d[1] and item_d[2] <= box_d[2]


def _best_orientation(
    item: ItemDims, available_l: Decimal, available_w: Decimal, available_h: Decimal
) -> tuple[Decimal, Decimal, Decimal] | None:
    """Find the rotation that fits in the available space and minimises wasted footprint."""
    dims = [item.length, item.width, item.height]
    best: tuple[Decimal, Decimal, Decimal] | None = None
    best_waste = None
    for perm in permutations(dims):
        pl, pw, ph = perm
        if pl <= available_l and pw <= available_w and ph <= available_h:
            waste = (available_l - pl) * (available_w - pw)
            if best is None or waste < best_waste:
                best = (pl, pw, ph)
                best_waste = waste
    return best


def _shelf_pack(items: list[ItemDims], box: BoxDims) -> bool:
    """Greedy shelf-layer packing heuristic.

    Layers stack along Z (height). Within each layer, shelves run along Y (width).
    Items are placed along X (length) within each shelf, rotated to minimise waste.
    See module docstring for guarantees and limitations.
    """
    if not items:
        return True

    sorted_items = sorted(items, key=lambda it: it.volume, reverse=True)

    box_l = box.inner_length
    box_w = box.inner_width
    box_h = box.inner_height

    used_height = Decimal("0")
    layer_max_h = Decimal("0")
    shelf_cursor_y = Decimal("0")
    shelf_depth = Decimal("0")
    shelf_cursor_x = Decimal("0")

    items_remaining = list(sorted_items)

    while items_remaining:
        placed_this_pass = []
        not_placed = []

        for itm in items_remaining:
            placed = False

            # Try to fit in current shelf
            avail_x = box_l - shelf_cursor_x
            avail_y = shelf_depth if shelf_depth > 0 else (box_w - shelf_cursor_y)
            avail_z = box_h - used_height

            if avail_z <= 0:
                not_placed.append(itm)
                continue

            orient = _best_orientation(itm, avail_x, avail_y, avail_z)
            if orient is not None:
                ol, ow, oh = orient
                if shelf_depth == Decimal("0"):
                    # Starting a new shelf — set its depth
                    shelf_depth = ow
                shelf_cursor_x += ol
                if oh > layer_max_h:
                    layer_max_h = oh
                placed = True
            else:
                # Try starting a new shelf in the same layer
                new_shelf_y = shelf_cursor_y + shelf_depth
                avail_y_new = box_w - new_shelf_y
                orient2 = _best_orientation(itm, box_l, avail_y_new, avail_z)
                if orient2 is not None and avail_y_new > 0:
                    ol, ow, oh = orient2
                    # Move to new shelf
                    shelf_cursor_y = new_shelf_y
                    shelf_depth = ow
                    shelf_cursor_x = ol
                    if oh > layer_max_h:
                        layer_max_h = oh
                    placed = True
                else:
                    # Try starting a new layer
                    new_used_height = used_height + layer_max_h
                    avail_z_new = box_h - new_used_height
                    orient3 = _best_orientation(itm, box_l, box_w, avail_z_new)
                    if orient3 is not None and avail_z_new > 0:
                        ol, ow, oh = orient3
                        # Start new layer
                        used_height = new_used_height
                        layer_max_h = oh
                        shelf_cursor_y = Decimal("0")
                        shelf_depth = ow
                        shelf_cursor_x = ol
                        placed = True

            if placed:
                placed_this_pass.append(itm)
            else:
                not_placed.append(itm)

        if not placed_this_pass:
            # No progress — can't fit remaining items
            return False

        items_remaining = not_placed

    return True


def recommend_box(
    order_items: list[dict],
    boxes: list[BoxDims],
) -> RecommendationResult:
    """Recommend the best shipping box for the given order items.

    Pure function — takes pre-fetched data (not Django querysets) so it can
    be tested without a database.
    """
    if not order_items:
        return RecommendationResult(
            fits=False,
            explanation="Cannot recommend a box for an empty order.",
        )

    expanded_items: list[ItemDims] = []
    total_weight = Decimal("0")
    total_volume = Decimal("0")

    for entry in order_items:
        qty = entry.get("quantity", 1)
        if qty < 1:
            return RecommendationResult(
                fits=False,
                explanation=f"Invalid quantity ({qty}) for SKU {entry['sku']}.",
            )
        item = ItemDims(
            sku=entry["sku"],
            name=entry.get("name", entry["sku"]),
            length=Decimal(str(entry["length"])),
            width=Decimal(str(entry["width"])),
            height=Decimal(str(entry["height"])),
            weight=Decimal(str(entry["weight"])),
        )
        for _ in range(qty):
            expanded_items.append(item)
        total_weight += item.weight * qty
        total_volume += item.volume * qty

    if not boxes:
        return RecommendationResult(
            fits=False,
            total_weight=total_weight,
            total_volume=total_volume,
            explanation="No active boxes available in the system.",
        )

    rejections: list[RejectionReason] = []
    candidates: list[BoxDims] = []

    for box in boxes:
        # Rule 2: Weight check
        if total_weight > box.max_weight:
            rejections.append(RejectionReason(
                box_name=box.name,
                reason=(
                    f"Total weight {total_weight} kg exceeds "
                    f"max weight {box.max_weight} kg."
                ),
            ))
            continue

        # Rule 3: Individual item fit (with rotation)
        item_too_large = False
        for item in expanded_items:
            if not item_fits_in_box(item, box):
                rejections.append(RejectionReason(
                    box_name=box.name,
                    reason=(
                        f"Item '{item.sku}' ({item.length}×{item.width}×{item.height} cm) "
                        f"does not fit even when rotated."
                    ),
                ))
                item_too_large = True
                break
        if item_too_large:
            continue

        # Rule 4: Volume check
        if total_volume > box.volume:
            rejections.append(RejectionReason(
                box_name=box.name,
                reason=(
                    f"Total item volume {total_volume} cm³ exceeds "
                    f"box volume {box.volume} cm³."
                ),
            ))
            continue

        # Rule 5: Spatial feasibility heuristic (multi-item)
        if len(expanded_items) == 1:
            # Single item already passed individual fit — guaranteed to fit
            candidates.append(box)
        else:
            if _shelf_pack(expanded_items, box):
                candidates.append(box)
            else:
                rejections.append(RejectionReason(
                    box_name=box.name,
                    reason="Items do not fit together (layer-packing heuristic failed).",
                ))

    if not candidates:
        # Build a helpful reason
        reasons_summary = "; ".join(f"{r.box_name}: {r.reason}" for r in rejections)
        # Check specific failure modes for a clear top-level message
        all_weight = all("weight" in r.reason.lower() for r in rejections)
        all_too_large = all("does not fit" in r.reason for r in rejections)

        if all_weight and rejections:
            top_reason = (
                f"Total weight ({total_weight} kg) exceeds the capacity of all active boxes."
            )
        elif all_too_large and rejections:
            top_reason = "At least one item is too large for every available box."
        else:
            top_reason = "No box can accommodate this order."

        return RecommendationResult(
            fits=False,
            total_weight=total_weight,
            total_volume=total_volume,
            explanation=f"{top_reason} Details: {reasons_summary}",
            rejections=rejections,
        )

    # Rule 6: Pick cheapest; tie-break by smallest volume, then lowest id
    candidates.sort(key=lambda b: (b.cost, b.volume, b.id))
    winner = candidates[0]

    utilisation = (total_volume / winner.volume * 100).quantize(Decimal("0.1"))

    # Build explanation
    others = [c for c in candidates if c.id != winner.id]
    explanation_parts = [
        f"Recommended '{winner.name}' (cost: {winner.cost}, "
        f"volume: {winner.volume} cm³).",
        f"Order: {len(expanded_items)} item(s), "
        f"{total_weight} kg, {total_volume} cm³.",
        f"Utilisation: {utilisation}%.",
    ]
    if others:
        other_names = ", ".join(f"'{c.name}' (cost: {c.cost})" for c in others)
        explanation_parts.append(
            f"Other viable boxes (more expensive or larger): {other_names}."
        )
    if rejections:
        rej_summary = "; ".join(f"'{r.box_name}': {r.reason}" for r in rejections[:3])
        explanation_parts.append(f"Rejected: {rej_summary}")

    return RecommendationResult(
        fits=True,
        recommended_box=winner,
        total_weight=total_weight,
        total_volume=total_volume,
        box_volume=winner.volume,
        utilisation_pct=utilisation,
        explanation=" ".join(explanation_parts),
        rejections=rejections,
    )
