"""Example 01 – Validate and normalize a spatial XES log.

Reads the synthetic spatial test log, runs validation (including strict mode),
normalizes types, shows effective CRS per event, and demonstrates strip_spatial.
"""

import os
import pm4py
import pm4py_spatial

# ── 1. Read XES (PM4Py returns DataFrame by default) ─────────────────────────
xes_path = os.path.join(os.path.dirname(__file__), "..", "tests", "synthetic_spatial.xes")

# Use return_legacy_log_object=True so we can access log-level space:crs
log = pm4py.read_xes(xes_path, return_legacy_log_object=True)
print(f"Loaded {len(log)} traces")
print(f"Log-level CRS: {log.attributes.get('space:crs')}")

# ── 2. Validate (basic) ─────────────────────────────────────────────────────
try:
    pm4py_spatial.validate(log)
    print("\n✓ Basic validation passed")
except pm4py_spatial.SpatialValidationError as e:
    print(f"\n✗ Validation failed: {e}")

# ── 3. Validate (strict mode — CRS-aware range checks) ──────────────────────
try:
    pm4py_spatial.validate(log, strict=True)
    print("✓ Strict validation passed (coordinate ranges OK for EPSG:4326)")
except pm4py_spatial.SpatialValidationError as e:
    print(f"✗ Strict validation failed: {e}")

# ── 4. Normalize types → returns DataFrame ───────────────────────────────────
df = pm4py_spatial.normalize_types(log)
print(f"\n✓ Types normalized — DataFrame shape: {df.shape}")
print(f"  Log-level CRS preserved in attrs: {df.attrs.get('space:crs')}")

# ── 5. Inspect effective CRS per event ───────────────────────────────────────
print("\nEffective CRS per event:")
for _, row in df.iterrows():
    case_id = row["case:concept:name"]
    crs = pm4py_spatial.effective_crs(
        df, row, log_crs=df.attrs.get("space:crs")
    )
    x = row.get(pm4py_spatial.SPACE_X)
    y = row.get(pm4py_spatial.SPACE_Y)
    print(f"  {case_id} / {row['concept:name']}: CRS={crs}  x={x}  y={y}")

# ── 6. Show spatial columns ──────────────────────────────────────────────────
spatial_cols = [c for c in df.columns if c.startswith("space:")]
print(f"\nSpatial columns: {spatial_cols}")

# ── 7. strip_spatial — remove all spatial columns ────────────────────────────
df_clean = pm4py_spatial.strip_spatial(df)
remaining = [c for c in df_clean.columns if c.startswith("space:")]
print(f"\nAfter strip_spatial: {len(remaining)} spatial columns remain")
print(f"  Columns: {list(df_clean.columns)}")

# ── 8. Can also read as plain DataFrame (no log-level attrs) ─────────────────
print("\n--- Alternative: DataFrame-first workflow ---")
df_raw = pm4py.read_xes(xes_path)  # returns DataFrame
pm4py_spatial.validate(df_raw, log_crs="EPSG:4326")
print("✓ Validation passed with explicit log_crs='EPSG:4326'")

print("\nDone.")
