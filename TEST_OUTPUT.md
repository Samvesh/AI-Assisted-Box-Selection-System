# Test Output

> This is the **real, unedited** terminal output from running the test suite.
> Captured on 2026-11-03.

## Lint Check (`ruff check .`)

```
All checks passed!
```

## Test Run (`pytest --tb=short -v`)

```
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\Samvesh\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
django: version: 5.2.16, settings: boxsystem.settings (from ini)
rootdir: D:\AI-Assisted Box Selection System
configfile: pyproject.toml
plugins: django-4.14.0
collecting ... collected 51 items

packing/tests/test_api.py::RecommendBoxAPITests::test_empty_items PASSED [  1%]
packing/tests/test_api.py::RecommendBoxAPITests::test_invalid_quantity PASSED [  3%]
packing/tests/test_api.py::RecommendBoxAPITests::test_missing_items_field PASSED [  5%]
packing/tests/test_api.py::RecommendBoxAPITests::test_multiple_items PASSED [  7%]
packing/tests/test_api.py::RecommendBoxAPITests::test_no_fit_returns_200_with_fits_false PASSED [  9%]
packing/tests/test_api.py::RecommendBoxAPITests::test_success PASSED     [ 11%]
packing/tests/test_api.py::RecommendBoxAPITests::test_unknown_sku PASSED [ 13%]
packing/tests/test_api.py::OrderRecommendBoxAPITests::test_empty_order PASSED [ 15%]
packing/tests/test_api.py::OrderRecommendBoxAPITests::test_order_not_found PASSED [ 17%]
packing/tests/test_api.py::OrderRecommendBoxAPITests::test_success PASSED [ 19%]
packing/tests/test_api.py::ProductCRUDTests::test_create_product PASSED  [ 21%]
packing/tests/test_api.py::ProductCRUDTests::test_list_products PASSED   [ 23%]
packing/tests/test_api.py::BoxCRUDTests::test_create_box PASSED          [ 25%]
packing/tests/test_api.py::BoxCRUDTests::test_list_boxes PASSED          [ 27%]
packing/tests/test_box_selector.py::ItemFitsInBoxTests::test_item_does_not_fit PASSED [ 29%]
packing/tests/test_box_selector.py::ItemFitsInBoxTests::test_item_exactly_equals_box_size PASSED [ 31%]
packing/tests/test_box_selector.py::ItemFitsInBoxTests::test_item_fits_only_when_rotated PASSED [ 33%]
packing/tests/test_box_selector.py::ItemFitsInBoxTests::test_item_fits_without_rotation PASSED [ 35%]
packing/tests/test_box_selector.py::ItemFitsInBoxTests::test_item_one_dim_too_large PASSED [ 37%]
packing/tests/test_box_selector.py::RecommendBoxEmptyOrderTests::test_empty_items_list PASSED [ 39%]
packing/tests/test_box_selector.py::RecommendBoxNoBoxesTests::test_no_active_boxes PASSED [ 41%]
packing/tests/test_box_selector.py::RecommendBoxWeightTests::test_quantity_multiplies_weight PASSED [ 43%]
packing/tests/test_box_selector.py::RecommendBoxWeightTests::test_quantity_weight_fits PASSED [ 45%]
packing/tests/test_box_selector.py::RecommendBoxWeightTests::test_weight_exactly_at_limit PASSED [ 47%]
packing/tests/test_box_selector.py::RecommendBoxWeightTests::test_weight_exceeds_all_boxes PASSED [ 49%]
packing/tests/test_box_selector.py::RecommendBoxVolumeTests::test_total_volume_exceeds_box PASSED [ 50%]
packing/tests/test_box_selector.py::RecommendBoxCheapestTests::test_cheapest_box_selected PASSED [ 52%]
packing/tests/test_box_selector.py::RecommendBoxCheapestTests::test_tiebreak_lowest_id PASSED [ 54%]
packing/tests/test_box_selector.py::RecommendBoxCheapestTests::test_tiebreak_smallest_volume PASSED [ 56%]
packing/tests/test_box_selector.py::RecommendBoxRotationTests::test_no_rotation_helps PASSED [ 58%]
packing/tests/test_box_selector.py::RecommendBoxRotationTests::test_rotation_allows_fit PASSED [ 60%]
packing/tests/test_box_selector.py::RecommendBoxMultiItemTests::test_duplicate_products_in_order PASSED [ 62%]
packing/tests/test_box_selector.py::RecommendBoxMultiItemTests::test_items_individually_fit_but_not_together_by_volume PASSED [ 64%]
packing/tests/test_box_selector.py::RecommendBoxMultiItemTests::test_many_small_items_fit PASSED [ 66%]
packing/tests/test_box_selector.py::RecommendBoxMultiItemTests::test_two_items_fit_side_by_side PASSED [ 68%]
packing/tests/test_box_selector.py::RecommendBoxNoFitTests::test_all_weight_exceeded_message PASSED [ 70%]
packing/tests/test_box_selector.py::RecommendBoxNoFitTests::test_item_too_large_message PASSED [ 72%]
packing/tests/test_box_selector.py::RecommendBoxUtilisationTests::test_100_percent_utilisation PASSED [ 74%]
packing/tests/test_box_selector.py::RecommendBoxUtilisationTests::test_utilisation_calculation PASSED [ 76%]
packing/tests/test_box_selector.py::RecommendBoxExplanationTests::test_explanation_includes_box_name PASSED [ 78%]
packing/tests/test_box_selector.py::RecommendBoxExplanationTests::test_rejections_populated PASSED [ 80%]
packing/tests/test_models.py::ProductModelTests::test_create_valid_product PASSED [ 82%]
packing/tests/test_models.py::ProductModelTests::test_negative_weight_fails_validation PASSED [ 84%]
packing/tests/test_models.py::ProductModelTests::test_sku_uniqueness PASSED [ 86%]
packing/tests/test_models.py::ProductModelTests::test_zero_dimension_fails_validation PASSED [ 88%]
packing/tests/test_models.py::BoxModelTests::test_box_ordering PASSED    [ 90%]
packing/tests/test_models.py::BoxModelTests::test_create_valid_box PASSED [ 92%]
packing/tests/test_models.py::BoxModelTests::test_negative_dimension_fails_validation PASSED [ 94%]
packing/tests/test_models.py::BoxModelTests::test_zero_cost_fails_validation PASSED [ 96%]
packing/tests/test_models.py::OrderModelTests::test_create_order_with_items PASSED [ 98%]
packing/tests/test_models.py::OrderModelTests::test_order_reference_unique PASSED [100%]

============================= 51 passed in 0.78s ==============================
```

## Test Summary

| Category | Count | Status |
|---|---|---|
| Model validation tests | 11 | ✅ All passed |
| Box selector unit tests | 26 | ✅ All passed |
| API endpoint tests | 14 | ✅ All passed |
| **Total** | **51** | **✅ All passed** |
