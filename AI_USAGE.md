# AI Usage

I used AI tools for this assignment. This file lists what they did, what I decided myself, and how the result was checked. The exported chats are in this repo, and where something here and a chat disagree, the chat is the record.

## 1. AI tools used

- **Google Antigravity, with Claude Opus 4.6.** Generated the Django project: models, selector logic, API, tests, CI file, seed command and a first README. Opus 4.6 was the only Claude model available in Antigravity, so I used that. I also used it for the cleanup, the git push, and to export its own session log as `CHAT_TRANSCRIPT.md`.
- **Claude (claude.ai).** Read the assignment with me, helped me write the build prompt for Antigravity, advised on the cleanup and git steps, drafted a shorter README and a first draft of this file.

## 2. Prompts I gave

Antigravity session (9 turns, 2026-11-02 and 2026-11-03, see `CHAT_TRANSCRIPT.md`):

1. **Build prompt.** One long prompt covering the stack (Django, DRF, pytest, Ruff, GitHub Actions), the four models, the box-selection rules, API endpoints, edge cases, seed data, test requirements and CI. It told Antigravity not to write AI_USAGE.md, a transcript, or my learnings. The prompt was written with Claude's help.
2. **"continue from it left"** (and later "continue from you left", twice). Antigravity stopped partway through a task and I had to tell it to carry on.
3. **"now run this locally"**, to start the dev server.
4. **Cleanup prompt.** Remove dead code, unused imports and redundant comments without changing behaviour, re-run ruff and tests, and list every change.
5. **Targeted removal prompt.** Remove `Product.volume`, `Product.sorted_dims`, `Box.sorted_dims` and the standalone `OrderItemAdmin`; grep for usages first; remove tests that only covered them; re-run everything.
6. **Git push.** I gave it the repo URL and asked it to put everything on GitHub.
7. **Transcript.** I asked it to make a transcript file of the chat. It wrote a small script that converts its own session log into `CHAT_TRANSCRIPT.md`.

Claude chat (exported separately as `CLAUDE_CHAT_TRANSCRIPT.md` [TODO: use your real filename]): the prompts I gave Claude were about the assignment, the Antigravity build prompt, model choice, the cleanup prompt, the README, this file, and the GitHub steps.

## 3. What the AI produced and I accepted

- The overall structure: `Product`, `Box`, `Order`, `OrderItem`, validators and DB constraints.
- The selector in `packing/services/box_selector.py` (rotation check, shelf/layer packing heuristic, cheapest, then smallest, then lowest-id selection).
- The DRF endpoints, serializers, seed command, CI workflow and the first 52 tests.
- The cleanup results: removed the unused `_layer_pack()` function, an unused `placed_count` variable, a leftover dangling `Decimal("0")` line, a `200 if fits else 200` conditional, the redundant `validate_items()` (DRF's `allow_empty=False` already covers it), and repeated docstrings and divider comments.

## 4. What I decided or changed myself

- After the cleanup, Antigravity listed some members as "candidates" and left them in. It even said the model properties were "reasonable" to keep. I decided to remove `Product.volume`, `Product.sorted_dims`, `Box.sorted_dims` and the standalone `OrderItemAdmin`. A grep showed they were only used by one test or not at all, and order items are still editable through `OrderItemInline`. The suite went from 52 to 51 tests.
- I kept `Box.volume`, because the selection logic and a test use it.
- Chose Opus 4.6 because nothing newer was available in Antigravity.
- README: [TODO: say whether you used Claude's shorter README or kept Antigravity's, and what you edited yourself]
- [TODO: add anything else you changed yourself, for example a test or edge case]

## 5. Mistakes found

By the AI, in the Antigravity session:

1. The serializer used `decimal_places=2` for volumes, but computed volumes can have more decimals. Changed to 6.
2. It used the deprecated `check=` in Django `CheckConstraint`. Changed to `condition=` after the warnings.
3. It used `l` as a variable name, which Ruff flags (E741). Renamed to `pl` / `ln`.
4. Its first command failed because it used `&&` in PowerShell, then it switched to `;`.
5. It ran `ruff --fix --unsafe-fixes`, which removed an unused variable and left a dangling `Decimal("0")` line behind. The cleanup pass caught it.
6. It left dead code in (`_layer_pack`, `placed_count`, the ternary and the redundant `validate_items`).
7. It pushed everything as a single commit.

Also: the explanation text in the API response shows volumes like `6000.000000 cm³`, which looks untidy. [TODO: say if you fixed it or left it]

By the AI in the Claude chat: I was told newer Claude models might be available in Antigravity. They were not. An earlier draft of this file also said I had checked some response numbers by hand, but it was Claude that checked them; I only looked at the response in the browser.

## 6. How it was verified

- `pytest` (52 tests at first, 51 after removing the unused members) and `ruff check .` were run by Antigravity. Output is in `TEST_OUTPUT.md`.
- I started the server and opened the API root and `/api/orders/DEMO-001/recommend-box/` in the browser. In the response, 2394 / 6000 = 39.9% utilisation matched, and "Small Mailer" was rejected because the book (24 x 16 x 3 cm) does not fit.
- Before deleting code, Antigravity grepped the project for every usage.
- [TODO: keep only the lines you really did]
  - Read the selector code and the `git diff` of the cleanup.
  - Tried a bad request: unknown SKU, empty `items`, or a very large quantity.
  - Opened `/admin/` and added an order item through the inline.
  - Checked that no cheaper box than the recommended one could fit the demo order.

## 7. A note on the transcripts

`CHAT_TRANSCRIPT.md` is the Antigravity session, converted from its own session log by a script that Antigravity wrote at my request. My prompts in it are word for word. Tool calls are shown as short summaries, not full output. The raw log is `transcript_full.jsonl` [TODO: add it to the repo if you want, or delete this sentence]. The Claude chat is exported separately.
