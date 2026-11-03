# What I Learned

3D Packing: I learned that 3D packing3D Packing: I learned that 3D packing is an NP-hard problem, so a greedy approach is a practical choice. However, it can sometimes reject a box that could fit with a better arrangement.

Item Rotation: Sorting item and box dimensions makes it easier to check whether an item fits in any of the six possible orientations.

Code Structure: Keeping the box selection logic separate from Django makes it easier to test and maintain without needing database access.

Consistent Results and API Design: Using cost, volume and ID as tie-breakers keeps box selection consistent. I also learned that returning 200 with fits: false makes more sense when no box is suitable, since it is a valid business outcome.

Django and CI: I got a better understanding of how models, serializers, views and management commands work together. I also learned how GitHub Actions can automatically run Ruff and pytest whenever code is pushed.

Testing and AI: Testing edge cases such as exact fits, weight limits and empty orders helped me understand the importance of proper test coverage. I also learned to use AI in smaller steps and review its output instead of blindly trusting generated code.
