# Citi Bike NYC — Spatial Sample

## Dataset

**Domain:** Urban bike-sharing transportation (Citi Bike NYC, October 2025)  
**Source folder:** `data/Event_Logs/citibike/`  
**Data origin:** Real (actual Citi Bike trip records)

## Sample File

| File | Traces | Events per Trace | Description |
|------|--------|------------------|-------------|
| `Citibike_SpatialSample.xes` | 5 | 2 | Bike trips with start/end station coordinates |

The sample was extracted from `citibike-trip-data-lifecycle.xes` (1,000,000 traces, 2,000,000 events — the largest dataset in the project). Due to the file's size, extraction was done via XML streaming rather than pm4py in-memory parsing.

Each trip produces exactly 2 events:
1. **Trip Started** — with origin station coordinates and name
2. **Trip Ended** — with destination station coordinates and name

## Spatial Attributes

| Attribute | Type | Level | Example |
|-----------|------|-------|---------|
| `space:lat` | float | Event | `40.69943` |
| `space:lon` | float | Event | `-73.91337` |
| `space:crs` | string | Event | `"EPSG:4326"` |
| `space:zone_name` | string | Event | `"Myrtle Ave & Linden St"` |
| `space:zone_id` | string | Event | `"4816.02"` |

**Spatial style:** Dual — Point (GPS) + Zone (station)  
**CRS:** EPSG:4326 (WGS84)

This dataset demonstrates **dual spatial representation**: precise GPS coordinates alongside human-readable zone identifiers (station names and IDs).

## What This Sample Demonstrates

- Dual spatial representation (point coordinates + zone names)
- WGS84 GPS coordinates with explicit CRS tagging
- Origin–destination spatial pattern (start station → end station)
- Event-level spatial attributes that differ between events in the same trace
