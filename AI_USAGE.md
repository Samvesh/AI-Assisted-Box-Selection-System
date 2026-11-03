# AI Usage

I used AI tools for this assignment. This file lists what they did, what I decided myself, and how I checked the result. The full conversations are in the exported chat transcript included in this repo.

## 1. AI tools used

- **Claude (claude.ai)**: read the assignment, helped me write the build prompt, advised on the cleanup pass, and drafted a shorter version of the README that I then edited.
- **Google Antigravity, with Claude Opus 4.6**: generated the Django project (models, selector logic, API, tests, CI file, seed command, README draft). Opus 4.6 was the only Claude model available in Antigravity, so I used that.

## 2. Prompts I used (summary)

1. **Build prompt.** A long, detailed prompt covering the stack (Django, DRF, pytest, Ruff, GitHub Actions), the four models, the box-selection rules (weight, rotation, volume, cheapest first, deterministic tie-break), the API endpoints, edge cases, seed data, test requirements and CI. It also told Antigravity **not** to write AI_USAGE.md, the transcript or my learnings.
2. **Run the server** so I could try the endpoints.
3. **Cleanup prompt.** Remove dead code, unused imports and redundant comments without changing behaviour, re-run ruff and tests, and list every change so I could review it.
4. **Targeted removal prompt.** Remove four specific unused members (see section 4), grep for usages first, remove the related tests, and re-run everything.

The exact wording is in the transcript.

## 3. What the AI produced and I accepted

- The overall structure: `Product`, `Box`, `Order`, `OrderItem` models, validators and DB constraints.
- The selector service in `packing/services/box_selector.py` (rotation check, shelf/layer packing heuristic, cheapest-then-smallest-then-lowest-id selection).
- The DRF endpoints, serializers, seed command, CI workflow and the first set of 52 tests.
- The cleanup results: removed the unused `_layer_pack()` function (about 81 lines), an unused `placed_count` variable, a pointless `200 if fits else 200` conditional, a redundant `validate_items()` (DRF's `allow_empty=False` already covers it), and repeated docstrings and divider comments.

## 4. What I changed or decided myself

- Reviewed the list of "candidate dead code" the AI left for me and **decided to remove** `Product.volume`, `Product.sorted_dims`, `Box.sorted_dims` and the standalone `OrderItemAdmin`. A grep showed they were only used by one test or not at all, and the order items are still editable through `OrderItemInline`. I had the related tests removed, so the suite went from 52 to 51 tests.
- Chose to keep `Box.volume` because the selection logic and its test use it.
- Edited the README into my own wording. [TODO: say what you rewrote]
- [TODO: add anything else you changed in the code or tests yourself, for example a new test or edge case]

## 5. Mistakes found

AI mistakes (reported by Antigravity during the build, and fixed):

1. Serializer used `decimal_places=2` for volume, but computed volumes can have more decimals. Changed to 6.
2. Used the deprecated `check=` argument in Django `CheckConstraint`. Changed to `condition=` after the warnings appeared.
3. Used `l` as a variable name, which Ruff flags as ambiguous (E741). Renamed.
4. Left dead code behind (see section 3), found in the cleanup pass.

Also, the explanation text in the API response shows volumes like `6000.000000 cm³`, which looks untidy. [TODO: say if you fixed this or left it]

Mistake in the advice I got: I was told newer Claude models might be available in Antigravity. They were not, so I used Opus 4.6.

## 6. How I verified it

- Ran `pytest` (52 tests at first, 51 after removing the unused helpers) and `ruff check .`. Output is in `TEST_OUTPUT.md`.
- Ran the server and opened the API root and `/api/orders/DEMO-001/recommend-box/`. I checked the numbers by hand: 2394 / 6000 = 39.9% utilisation, and "Small Mailer" was correctly rejected because the book (24 x 16 x 3 cm) does not fit in it.
- Before deleting code I had the AI grep the project for every usage first.
- [TODO: only keep the lines below if you actually did them]
  - Read the selector code and the full `git diff` of the cleanup.
  - Tried a bad request: unknown SKU / empty items / very large quantity.
  - Opened `/admin/` and added an order item through the inline.
  - Checked that no cheaper box than the recommended one could fit the demo order.