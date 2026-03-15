# pm4py_spatial

Spatial-aware pre-processing layer for [PM4Py](https://pm4py.fit.fraunhofer.de/) event logs.

This package reads spatial attributes from XES logs using the `space:` extension and provides validation, type normalization, and CRS transformation — keeping output fully compatible with standard PM4Py pipelines.

## Spatial Attributes

The extension defines canonical attribute names, but the package **auto-detects** common alternatives found in real-world XES files:

| Role | Canonical key | Also detected | Description |
|------|--------------|---------------|-------------|
| CRS | `space:crs` | — | Coordinate Reference System (e.g. `EPSG:4326`) |
| X / Horizontal | `space:x` | `space:lon`, `space:longitude` | Horizontal coordinate |
| Y / Vertical | `space:y` | `space:lat`, `space:latitude` | Vertical coordinate |
| Level | `space:level` | `space:floor`, `space:z` | Vertical level / floor |
| Location | `space:location` | `space:zone_name`, `space:zone_id`, `space:node_id`, `space:station`, `space:room` | Discrete location ID |

All functions (`validate`, `normalize_types`, `normalize_crs`, etc.) automatically detect which columns are present — no manual column mapping required.

### Coordinate Convention

When using `space:x`/`space:y`, coordinates follow `always_xy` order — `space:x` is always the horizontal axis:

| CRS           | `space:x`  | `space:y`  |
|---------------|------------|------------|
| EPSG:4326     | longitude  | latitude   |
| UTM (e.g. 32618) | easting | northing   |
| LOCAL_METERS  | x-position | y-position |

When using `space:lon`/`space:lat`, the meaning is explicit in the column name.

### CRS Resolution

For each event the **effective CRS** is determined as:

```
effective_crs = event["space:crs"]  if present
              else log.attributes["space:crs"]
```

Event-level CRS overrides log-level. If neither exists, behavior depends on the `on_missing` parameter.

## Installation

```bash
cd pm4py_spatial
pip install -e .
```

For CRS transformation support (optional):

```bash
pip install -e ".[crs]"
```

## Dependencies

| Package  | Required | Purpose                |
|----------|----------|------------------------|
| pm4py    | yes      | Event log handling     |
| pandas   | yes      | DataFrame processing   |
| pyproj   | optional | CRS coordinate transforms |

## API

All functions accept both `EventLog` and `DataFrame` as input. When passing a DataFrame, provide `log_crs` explicitly since DataFrames don't carry log-level attributes.

```python
import pm4py
import pm4py_spatial

# Read XES (legacy EventLog preserves log-level space:crs)
log = pm4py.read_xes("my_log.xes", return_legacy_log_object=True)

# Auto-detect which spatial columns are present
cols = pm4py_spatial.detect_spatial_columns(pm4py.read_xes("my_log.xes"))
# → SpatialColumns(x='space:lon', y='space:lat', crs='space:crs', level=None, location='space:zone_name')

# Validate spatial attributes (auto-detects columns)
pm4py_spatial.validate(log)
pm4py_spatial.validate(log, strict=True)  # also checks coordinate ranges for known CRS

# Normalize types → returns new DataFrame (input not modified)
df = pm4py_spatial.normalize_types(log, on_error="raise")  # or "drop_event" / "drop_trace"

# Normalize CRS (requires: pip install pyproj)
# Non-transformable CRS (LOCAL_METERS, etc.) will raise a clear error
df = pm4py_spatial.normalize_crs(log, target_crs="EPSG:4326", on_missing="raise")

# Check if a CRS can be transformed
pm4py_spatial.is_transformable("EPSG:4326")    # True
pm4py_spatial.is_transformable("LOCAL_METERS")  # False

# Strip spatial columns before feeding into PM4Py algorithms
df_clean = pm4py_spatial.strip_spatial(df)

# Get effective CRS for a single event
crs = pm4py_spatial.effective_crs(log, event)

# DataFrame conversion
df = pm4py_spatial.to_dataframe(log)
log = pm4py_spatial.from_dataframe(df)

# DataFrame-first workflow (no legacy EventLog needed)
df = pm4py.read_xes("my_log.xes")  # returns DataFrame
pm4py_spatial.validate(df, log_crs="EPSG:4326")
df = pm4py_spatial.normalize_types(df)
```

## Verified Datasets

The package has been tested against these real-world and synthetic XES files:

| Dataset | Coordinate columns | CRS | Level / Location | Traces | Events |
|---------|--------------------|-----|------------------|--------|--------|
| **Synthetic Bottling Factory** | `space:x`, `space:y` | `LOCAL_METERS` (log) | `space:floor`, `space:node_id` | 3 | 28 |
| **Citibike NYC** | `space:lat`, `space:lon` | `EPSG:4326` (event+log) | `space:zone_name`, `space:zone_id` | 5 | 10 |
| **Truck Shipment (compact)** | `space:lat`, `space:lon` | `EPSG:4326` (event+log) | — | 2 | 25 |
| **Truck Shipment (extended)** | `space:lat`, `space:lon` | `EPSG:4326` (event+log) | — | 7 | 748 |

All datasets pass `validate()`, `validate(strict=True)`, `normalize_types()`, `strip_spatial()`, and `normalize_crs()` (for transformable CRS).

## Examples

```bash
# Validate + normalize the synthetic test log
python examples/01_validate_and_normalize.py

# Run PM4Py discovery on the bottling factory sample
python examples/02_discovery_after_spatial_normalize.py
```

## Tests

```bash
# Unit tests (synthetic data, edge cases)
python tests/test_all.py

# Integration tests (real-world XES files from traces/)
python tests/test_traces_integration.py
```

## Package Structure

```
pm4py_spatial/
  pyproject.toml
  README.md
  pm4py_spatial/
    __init__.py       # Public API re-exports
    constants.py      # Attribute key constants + alias definitions
    exceptions.py     # Custom exception classes
    spatial.py        # validate, normalize_types, normalize_crs, effective_crs,
                      # strip_spatial, detect_spatial_columns, SpatialColumns
    crs.py            # Transformer caching, coordinate transforms, CRS registry
    df.py             # DataFrame ↔ EventLog conversion
  examples/
    01_validate_and_normalize.py
    02_discovery_after_spatial_normalize.py
  tests/
    test_all.py                    # Unit tests
    test_traces_integration.py     # Integration tests (Bottling, Citibike, Truck)
    synthetic_spatial.xes          # Synthetic fixture
```
