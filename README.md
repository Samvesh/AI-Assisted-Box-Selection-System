# Box Selection System

A small Django REST API that picks the cheapest shipping box for an order. You give it the items (SKU + quantity), it checks weight and size against the active boxes and tells you which box to use, or why nothing fits.

I built this as a take-home assignment. I used an AI coding tool for parts of it, and what it did and what I changed is written down in `AI_USAGE.md`.

## Setup

```bash
git clone <repo-url>
cd <repo-folder>

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Then open http://127.0.0.1:8000/api/ . Admin is at `/admin/` (run `python manage.py createsuperuser` first).

## Using the API

Recommend a box for any list of items:

```bash
curl -X POST http://127.0.0.1:8000/api/recommend-box/ \
  -H "Content-Type: application/json" \
  -d '{"items": [{"sku": "LAPTOP-01", "quantity": 1}]}'
```

Recommend a box for a saved order (the seed command creates `DEMO-001`):

```bash
curl http://127.0.0.1:8000/api/orders/DEMO-001/recommend-box/
```

On Windows PowerShell `curl` is not the real curl, so use Postman or the browsable API page instead.

Products, boxes and orders also have normal CRUD endpoints at `/api/products/`, `/api/boxes/` and `/api/orders/`.

### What comes back

- `fits`: true or false
- `recommended_box`: the chosen box (null if nothing fits)
- `total_weight`, `total_volume`, `box_volume`, `utilisation_pct`
- `explanation`: short text on why this box was picked
- `rejections`: list of boxes that were skipped and the reason

### Errors

- Unknown SKU or empty `items` gives a 400 with a message.
- Unknown order reference gives a 404.
- "Nothing fits" is **not** an error. It returns 200 with `fits: false`, because it is a normal result of the business logic and not a failure of the request.

## How the box is picked

The logic is in `packing/services/box_selector.py`. It works on plain Python data, not Django models, so it can be tested without a database.

For every active box it checks, in this order:

1. Total weight is within the box's `max_weight`.
2. Every item fits on its own, in any of the 6 rotations. I sort the item's dimensions and the box's dimensions and compare them one by one, which is the same as trying all rotations.
3. Total item volume is not more than the box volume.
4. For orders with more than one item, a packing check (below) confirms the items fit together.

From the boxes that pass, it picks the cheapest. If costs are equal it takes the smaller volume, then the lower id, so the same input always gives the same answer.

### The packing check

Real 3D bin packing is NP-hard, so I used a simple greedy approach: sort items largest first, put them in shelves along the width, stack shelves into layers along the height, and rotate each item to waste the least footprint.

What this means in practice:

- If it says the items fit, they do fit.
- It can say "doesn't fit" for a box that a smarter arrangement (or a person) could pack. It is conservative.

## Assumptions and limits

- Products are rigid boxes, no odd shapes, no padding or void fill.
- Items can be rotated freely (no "this side up").
- One box per order. Splitting an order across several boxes is not supported.
- Box dimensions are the inner, usable size.
- No authentication on the API.

## Tests

```bash
pytest -v
ruff check .
```

Tests are in `packing/tests/` (models, selector logic, API). CI runs lint and tests on every push (`.github/workflows/ci.yml`). A saved run is in `TEST_OUTPUT.md`.

## Seed data

`python manage.py seed_demo` adds 8 products, 5 boxes and one order, `DEMO-001` (1 smartphone and 2 hardcover books).

Boxes (inner size in cm, max weight in kg, cost):

| Name | Size | Max weight | Cost |
|---|---|---|---|
| Small Mailer | 20 x 15 x 10 | 2 | 1.50 |
| Flat Pack | 40 x 30 x 5 | 4 | 2.50 |
| Medium Box | 35 x 25 x 15 | 5 | 3.00 |
| Large Box | 50 x 35 x 25 | 10 | 5.50 |
| Extra-Large Box | 70 x 45 x 30 | 15 | 8.00 |

## Project layout

```
boxsystem/    project settings and urls
packing/      models, serializers, views, admin
  services/box_selector.py     the selection logic
  management/commands/seed_demo.py
  tests/
.github/workflows/ci.yml
AI_USAGE.md
TEST_OUTPUT.md
```