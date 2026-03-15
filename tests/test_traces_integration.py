"""Integration tests for pm4py.spatial against real-world trace files.

Tests all three required datasets:
  1. Synthetic Bottling Factory  (space:x / space:y, LOCAL_METERS)
  2. Citibike NYC               (space:lat / space:lon, EPSG:4326)
  3. Truck Shipment Routes       (space:lat / space:lon, EPSG:4326)

Each dataset exercises:
  - detect_spatial_columns  (auto-detect the right column names)
  - validate                (basic + strict where applicable)
  - normalize_types         (coerce to float / str)
  - strip_spatial           (remove all space:* cols)
  - effective_crs           (resolve event vs log CRS)
  - normalize_crs           (CRS transformation, where possible)
"""

import os
import sys

import pm4py
import pm4py.spatial

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
TRACES = os.path.join(os.path.dirname(__file__), "..", "spatial_analysis", "traces")

BOTTLING_XES = os.path.join(TRACES, "Synthetic_Bottling_Factory", "Bottling_SpatialSample.xes")
CITIBIKE_XES = os.path.join(TRACES, "Citibike", "Citibike_SpatialSample.xes")
TRUCK_COMPACT_XES = os.path.join(TRACES, "Truck_Shipment", "TruckShipment_SpatialSample.xes")
TRUCK_EXTENDED_XES = os.path.join(TRACES, "Truck_Shipment", "TruckShipment_ExtendedSpatialSample.xes")


def _check_file(path: str) -> None:
    if not os.path.exists(path):
        print(f"  SKIP — file not found: {path}")
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════
# 1. Synthetic Bottling Factory
# ═══════════════════════════════════════════════════════════════════════════
def test_bottling():
    print("\n=== Running integration test for Bottling Factory traces ===")
    print("=" * 70)
    print("TEST SUITE: Synthetic Bottling Factory")
    print("  Attributes: space:x, space:y, space:floor, space:node_id")
    print("  CRS: LOCAL_METERS (log-level)")
    print("=" * 70)
    _check_file(BOTTLING_XES)

    # Load
    log = pm4py.read_xes(BOTTLING_XES, return_legacy_log_object=True)
    print(f"  Loaded: {len(log)} traces")
    log_crs = log.attributes.get("space:crs")
    print(f"  Log-level CRS: {log_crs}")

    # Detect columns
    df_raw = pm4py.read_xes(BOTTLING_XES)
    cols = pm4py.spatial.detect_spatial_columns(df_raw)
    print(f"\n  detect_spatial_columns → {cols}")
    assert cols.x == "space:x", f"Expected x='space:x', got {cols.x!r}"
    assert cols.y == "space:y", f"Expected y='space:y', got {cols.y!r}"
    assert cols.level == "space:floor", f"Expected level='space:floor', got {cols.level!r}"
    assert cols.location == "space:node_id", f"Expected location='space:node_id', got {cols.location!r}"
    print("  ✓ Column detection correct")

    # Validate (basic — should pass)
    pm4py.spatial.validate(log)
    print("  ✓ Basic validation passed")

    # Validate (strict — LOCAL_METERS has no range checks, should pass)
    pm4py.spatial.validate(log, strict=True)
    print("  ✓ Strict validation passed (no range rules for LOCAL_METERS)")

    # Normalize types
    df = pm4py.spatial.normalize_types(log)
    assert df["space:x"].dtype == float, f"Expected float, got {df['space:x'].dtype}"
    assert df["space:y"].dtype == float
    print(f"  ✓ normalize_types — shape {df.shape}, x/y are floats")
    print(f"    x range: [{df['space:x'].min():.1f}, {df['space:x'].max():.1f}]")
    print(f"    y range: [{df['space:y'].min():.1f}, {df['space:y'].max():.1f}]")
    print(f"    CRS in attrs: {df.attrs.get('space:crs')}")

    # Effective CRS
    for _, row in df.head(2).iterrows():
        crs = pm4py.spatial.effective_crs(df, row, log_crs=df.attrs.get("space:crs"))
        print(f"    effective_crs({row['concept:name']}): {crs}")
    print("  ✓ effective_crs works")

    # is_transformable — LOCAL_METERS should be False
    assert not pm4py.spatial.is_transformable("LOCAL_METERS")
    print("  ✓ is_transformable('LOCAL_METERS') = False")

    # normalize_crs — should raise for LOCAL_METERS → EPSG:4326
    try:
        pm4py.spatial.normalize_crs(log, "EPSG:4326")
        print("  ✗ FAIL: should have raised for LOCAL_METERS transform")
        return False
    except pm4py.spatial.SpatialValidationError as e:
        print(f"  ✓ normalize_crs raises for LOCAL_METERS: {e}")

    # strip_spatial
    df_clean = pm4py.spatial.strip_spatial(df)
    spatial_remaining = [c for c in df_clean.columns if c.startswith("space:")]
    assert len(spatial_remaining) == 0, f"Expected 0 spatial cols, got {spatial_remaining}"
    print(f"  ✓ strip_spatial — {len(df.columns) - len(df_clean.columns)} spatial cols removed")

    print("  ✅ Bottling: ALL TESTS PASSED\n")
    return True


# ═══════════════════════════════════════════════════════════════════════════
# 2. Citibike NYC
# ═══════════════════════════════════════════════════════════════════════════
def test_citibike():
    print("\n=== Running integration test for Citibike traces ===")
    print("=" * 70)
    print("TEST SUITE: Citibike NYC")
    print("  Attributes: space:lat, space:lon, space:zone_name, space:zone_id")
    print("  CRS: EPSG:4326 (event-level + log-level)")
    print("=" * 70)
    _check_file(CITIBIKE_XES)

    # Load
    log = pm4py.read_xes(CITIBIKE_XES, return_legacy_log_object=True)
    print(f"  Loaded: {len(log)} traces")
    log_crs = log.attributes.get("space:crs")
    print(f"  Log-level CRS: {log_crs}")

    # Detect columns
    df_raw = pm4py.read_xes(CITIBIKE_XES)
    cols = pm4py.spatial.detect_spatial_columns(df_raw)
    print(f"\n  detect_spatial_columns → {cols}")
    assert cols.x == "space:lon", f"Expected x='space:lon', got {cols.x!r}"
    assert cols.y == "space:lat", f"Expected y='space:lat', got {cols.y!r}"
    assert cols.location == "space:zone_name", f"Expected location='space:zone_name', got {cols.location!r}"
    print("  ✓ Column detection correct (lon→x, lat→y)")

    # Validate (basic)
    pm4py.spatial.validate(log)
    print("  ✓ Basic validation passed")

    # Validate (strict — EPSG:4326 range checks)
    pm4py.spatial.validate(log, strict=True)
    print("  ✓ Strict validation passed (lat/lon in valid ranges)")

    # Normalize types
    df = pm4py.spatial.normalize_types(log)
    assert df["space:lon"].dtype == float
    assert df["space:lat"].dtype == float
    print(f"  ✓ normalize_types — shape {df.shape}, lat/lon are floats")
    print(f"    lon range: [{df['space:lon'].min():.5f}, {df['space:lon'].max():.5f}]")
    print(f"    lat range: [{df['space:lat'].min():.5f}, {df['space:lat'].max():.5f}]")

    # Effective CRS
    for _, row in df.head(2).iterrows():
        crs = pm4py.spatial.effective_crs(df, row, log_crs=df.attrs.get("space:crs"))
        assert crs == "EPSG:4326", f"Expected EPSG:4326, got {crs}"
    print("  ✓ effective_crs = EPSG:4326 for all events")

    # normalize_crs — transform EPSG:4326 → EPSG:32618 (UTM 18N for NYC)
    df_utm = pm4py.spatial.normalize_crs(log, "EPSG:32618")
    assert df_utm.attrs.get("space:crs") == "EPSG:32618"
    # UTM easting should be in 500000–600000 range for NYC
    x_min = df_utm["space:lon"].min()
    x_max = df_utm["space:lon"].max()
    print(f"  ✓ normalize_crs EPSG:4326→EPSG:32618 — x range: [{x_min:.0f}, {x_max:.0f}]")
    assert 500000 < x_min < 700000, f"UTM easting out of expected range: {x_min}"

    # strip_spatial
    df_clean = pm4py.spatial.strip_spatial(df)
    spatial_remaining = [c for c in df_clean.columns if c.startswith("space:")]
    assert len(spatial_remaining) == 0
    print(f"  ✓ strip_spatial — {len(df.columns) - len(df_clean.columns)} spatial cols removed")

    print("  ✅ Citibike: ALL TESTS PASSED\n")
    return True


# ═══════════════════════════════════════════════════════════════════════════
# 3. Truck Shipment Routes (compact sample)
# ═══════════════════════════════════════════════════════════════════════════
def test_truck_compact():
    print("\n=== Running integration test for Truck Compact traces ===")
    print("=" * 70)
    print("TEST SUITE: Truck Shipment Routes (compact, 2 traces)")
    print("  Attributes: space:lat, space:lon")
    print("  CRS: EPSG:4326 (event-level)")
    print("=" * 70)
    _check_file(TRUCK_COMPACT_XES)

    # Load
    log = pm4py.read_xes(TRUCK_COMPACT_XES, return_legacy_log_object=True)
    print(f"  Loaded: {len(log)} traces")
    log_crs = log.attributes.get("space:crs")
    print(f"  Log-level CRS: {log_crs}")

    # Detect columns
    df_raw = pm4py.read_xes(TRUCK_COMPACT_XES)
    cols = pm4py.spatial.detect_spatial_columns(df_raw)
    print(f"\n  detect_spatial_columns → {cols}")
    assert cols.x == "space:lon", f"Expected x='space:lon', got {cols.x!r}"
    assert cols.y == "space:lat", f"Expected y='space:lat', got {cols.y!r}"
    print("  ✓ Column detection correct")

    # Validate (basic)
    pm4py.spatial.validate(log)
    print("  ✓ Basic validation passed")

    # Validate (strict)
    pm4py.spatial.validate(log, strict=True)
    print("  ✓ Strict validation passed")

    # Normalize types
    df = pm4py.spatial.normalize_types(log)
    print(f"  ✓ normalize_types — shape {df.shape}")
    print(f"    lon range: [{df['space:lon'].min():.5f}, {df['space:lon'].max():.5f}]")
    print(f"    lat range: [{df['space:lat'].min():.5f}, {df['space:lat'].max():.5f}]")

    # Effective CRS
    for _, row in df.head(2).iterrows():
        crs = pm4py.spatial.effective_crs(df, row, log_crs=df.attrs.get("space:crs"))
        assert crs == "EPSG:4326", f"Expected EPSG:4326, got {crs}"
    print("  ✓ effective_crs = EPSG:4326")

    # normalize_crs — EPSG:4326 → EPSG:3857 (Web Mercator)
    df_mercator = pm4py.spatial.normalize_crs(log, "EPSG:3857")
    assert df_mercator.attrs.get("space:crs") == "EPSG:3857"
    print(f"  ✓ normalize_crs EPSG:4326→EPSG:3857 — transformed OK")
    print(f"    x range: [{df_mercator['space:lon'].min():.0f}, {df_mercator['space:lon'].max():.0f}]")
    print(f"    y range: [{df_mercator['space:lat'].min():.0f}, {df_mercator['space:lat'].max():.0f}]")

    # strip_spatial
    df_clean = pm4py.spatial.strip_spatial(df)
    spatial_remaining = [c for c in df_clean.columns if c.startswith("space:")]
    assert len(spatial_remaining) == 0
    print(f"  ✓ strip_spatial — {len(df.columns) - len(df_clean.columns)} spatial cols removed")

    print("  ✅ Truck (compact): ALL TESTS PASSED\n")
    return True


# ═══════════════════════════════════════════════════════════════════════════
# 4. Truck Shipment Routes (extended sample)
# ═══════════════════════════════════════════════════════════════════════════
def test_truck_extended():
    print("\n=== Running integration test for Truck Extended traces ===")
    print("=" * 70)
    print("TEST SUITE: Truck Shipment Routes (extended, 7 traces)")
    print("  Attributes: space:lat, space:lon")
    print("  CRS: EPSG:4326 (event-level)")
    print("=" * 70)
    _check_file(TRUCK_EXTENDED_XES)

    # Load
    log = pm4py.read_xes(TRUCK_EXTENDED_XES, return_legacy_log_object=True)
    print(f"  Loaded: {len(log)} traces")

    # Detect columns
    df_raw = pm4py.read_xes(TRUCK_EXTENDED_XES)
    cols = pm4py.spatial.detect_spatial_columns(df_raw)
    print(f"  detect_spatial_columns → {cols}")
    assert cols.x == "space:lon"
    assert cols.y == "space:lat"
    print("  ✓ Column detection correct")

    # Validate (basic + strict)
    pm4py.spatial.validate(log)
    print("  ✓ Basic validation passed")
    pm4py.spatial.validate(log, strict=True)
    print("  ✓ Strict validation passed")

    # Normalize types
    df = pm4py.spatial.normalize_types(log)
    print(f"  ✓ normalize_types — {len(df)} events across {df['case:concept:name'].nunique()} cases")
    print(f"    lon range: [{df['space:lon'].min():.5f}, {df['space:lon'].max():.5f}]")
    print(f"    lat range: [{df['space:lat'].min():.5f}, {df['space:lat'].max():.5f}]")

    # strip_spatial
    df_clean = pm4py.spatial.strip_spatial(df)
    spatial_remaining = [c for c in df_clean.columns if c.startswith("space:")]
    assert len(spatial_remaining) == 0
    print(f"  ✓ strip_spatial — {len(df.columns) - len(df_clean.columns)} spatial cols removed")

    # PM4Py discovery on stripped data
    net, im, fm = pm4py.discover_petri_net_inductive(df_clean)
    print(f"  ✓ Inductive Miner on stripped data: {len(net.places)} places, {len(net.transitions)} transitions")

    print("  ✅ Truck (extended): ALL TESTS PASSED\n")
    return True


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    results = {}
    results["Bottling"] = test_bottling()
    results["Citibike"] = test_citibike()
    results["Truck (compact)"] = test_truck_compact()
    results["Truck (extended)"] = test_truck_extended()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} — {name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n✅ ALL INTEGRATION TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
