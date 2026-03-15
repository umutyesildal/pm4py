"""End-to-end tests for pm4py_spatial after deep-research fixes."""

import numpy as np
import pandas as pd
import pm4py_spatial


def test_non_mutating_normalize_types():
    print("=== Test 1: normalize_types does not mutate input ===")
    df = pd.DataFrame({
        "case:concept:name": ["c1", "c1"],
        "concept:name": ["A", "B"],
        "space:x": ["1.5", "2.5"],
        "space:y": ["3.5", "4.5"],
    })
    result = pm4py_spatial.normalize_types(df)
    assert df["space:x"].dtype == object, "Input should still be strings"
    assert result["space:x"].dtype == float, "Output should be floats"
    print("  PASS")


def test_non_mutating_normalize_crs():
    print("=== Test 2: normalize_crs does not mutate input ===")
    df = pd.DataFrame({
        "case:concept:name": ["c1"],
        "concept:name": ["A"],
        "space:x": [-73.98566],
        "space:y": [40.74838],
    })
    x_before = df["space:x"].iloc[0]
    result = pm4py_spatial.normalize_crs(df, "EPSG:32618", log_crs="EPSG:4326")
    assert df["space:x"].iloc[0] == x_before, "Input x should not change"
    assert result["space:x"].iloc[0] != x_before, "Output x should be transformed"
    print(f"  PASS: original x={x_before}, transformed x={result['space:x'].iloc[0]:.1f}")


def test_local_meters_transform_error():
    print("=== Test 3: LOCAL_METERS transform raises error ===")
    df = pd.DataFrame({
        "case:concept:name": ["c1"],
        "concept:name": ["A"],
        "space:x": [10.0],
        "space:y": [20.0],
    })
    try:
        pm4py_spatial.normalize_crs(df, "EPSG:4326", log_crs="LOCAL_METERS")
        print("  FAIL: should have raised")
        return False
    except pm4py_spatial.SpatialValidationError as e:
        print(f"  PASS: {e}")
    return True


def test_nan_inf_detection():
    print("=== Test 4: NaN/inf detection ===")
    for val, label in [(float("inf"), "inf"), (float("-inf"), "-inf"), (float("nan"), "NaN")]:
        df = pd.DataFrame({
            "case:concept:name": ["c1"],
            "concept:name": ["A"],
            "space:x": [val],
            "space:y": [1.0],
        })
        try:
            pm4py_spatial.validate(df, log_crs="EPSG:4326")
            print(f"  FAIL: {label} should have raised")
            return False
        except pm4py_spatial.SpatialValidationError:
            print(f"  PASS: {label} detected")
    return True


def test_strict_mode_range_check():
    print("=== Test 5: Strict mode range check ===")
    # y=latitude > 90 should fail
    df = pd.DataFrame({
        "case:concept:name": ["c1"],
        "concept:name": ["A"],
        "space:x": [-73.0],
        "space:y": [100.0],
    })
    try:
        pm4py_spatial.validate(df, log_crs="EPSG:4326", strict=True)
        print("  FAIL: should have raised for lat=100")
        return False
    except pm4py_spatial.SpatialValidationError as e:
        print(f"  PASS: {e}")

    # Valid coordinates should pass strict
    df_ok = pd.DataFrame({
        "case:concept:name": ["c1"],
        "concept:name": ["A"],
        "space:x": [-73.0],
        "space:y": [40.0],
    })
    pm4py_spatial.validate(df_ok, log_crs="EPSG:4326", strict=True)
    print("  PASS: valid coords pass strict mode")
    return True


def test_strip_spatial():
    print("=== Test 6: strip_spatial ===")
    df = pd.DataFrame({
        "case:concept:name": ["c1"],
        "concept:name": ["A"],
        "space:x": [1.0],
        "space:y": [2.0],
        "space:location": ["loc"],
        "space:level": ["Floor1"],
        "space:crs": ["EPSG:4326"],
    })
    result = pm4py_spatial.strip_spatial(df)
    spatial_remaining = [c for c in result.columns if c.startswith("space:")]
    assert len(spatial_remaining) == 0, f"Should have 0 spatial cols, got {spatial_remaining}"
    assert "space:x" in df.columns, "Original should be untouched"
    assert set(result.columns) == {"case:concept:name", "concept:name"}
    print("  PASS")


def test_is_transformable():
    print("=== Test 7: is_transformable ===")
    assert pm4py_spatial.is_transformable("EPSG:4326") is True
    assert pm4py_spatial.is_transformable("EPSG:32618") is True
    assert pm4py_spatial.is_transformable("LOCAL_METERS") is False
    assert pm4py_spatial.is_transformable("LOCAL_FEET") is False
    assert pm4py_spatial.is_transformable("LOCAL") is False
    assert pm4py_spatial.is_transformable("PIXEL") is False
    print("  PASS")


def test_xes_file_with_strict():
    print("=== Test 8: Validate synthetic XES with strict=True ===")
    import os
    import pm4py
    xes_path = os.path.join(os.path.dirname(__file__), "synthetic_spatial.xes")
    log = pm4py.read_xes(xes_path, return_legacy_log_object=True)
    pm4py_spatial.validate(log, strict=True)
    print("  PASS: synthetic XES passes strict validation")


if __name__ == "__main__":
    test_non_mutating_normalize_types()
    test_non_mutating_normalize_crs()
    test_local_meters_transform_error()
    test_nan_inf_detection()
    test_strict_mode_range_check()
    test_strip_spatial()
    test_is_transformable()
    test_xes_file_with_strict()
    print("\n✅ All tests passed!")
