# BPI Challenge 2015 — Spatial Sample

## Dataset

**Domain:** Building & environmental permit applications in Dutch municipalities  
**Source folder:** `data/Event_Logs/BPI-2015/`  
**Data origin:** Real (BPI Challenge 2015 benchmark)

## Sample File

| File | Traces | Events per Trace | Description |
|------|--------|------------------|-------------|
| `BPI2015_SpatialSample.xes` | 3 | 10–30 | One trace from each of Municipalities 1, 2, and 3 |

The sample was extracted from `BPIC2015_MergedMini_Zone_100traces.xes` (100 traces, 20 per municipality). Traces were selected to represent different municipalities and varying process complexity.

## Spatial Attributes

| Attribute | Type | Level | Example |
|-----------|------|-------|---------|
| `space:zone_id` | string | Trace | `"Municipality_1"` |
| `space:zone_type` | string | Trace | `"municipality"` |

**Spatial style:** Zone (administrative region)  
**CRS:** N/A (named zones)

Each trace carries its originating municipality as a zone identifier. The spatial concept here is which administrative zone handled the permit application.

## What This Sample Demonstrates

- Zone-based spatial attributes at the trace level
- Cross-municipality process comparison (same process type, different locations)
- Real-world public administration process data with spatial tagging
