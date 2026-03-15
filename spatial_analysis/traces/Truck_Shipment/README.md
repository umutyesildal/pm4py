# Truck Shipment Routes — Spatial Samples

## Dataset

**Domain:** European truck logistics (GPS telemetry)  
**Source folder:** `data/Event_Logs/Truck shipment routes/`  
**Data origin:** Real (actual truck shipment telemetry from CSV)

## Sample Files

| File | Traces | Events | Description |
|------|--------|--------|-------------|
| `TruckShipment_SpatialSample.xes` | 2 | 25 | Compact sample — Amsterdam→Liège + Frankfurt→Zurich |
| `TruckShipment_ExtendedSpatialSample.xes` | 7 | 748 | Extended sample — mix of short and long routes across Europe |

Both files were generated from `Truck-shipment-log.csv` (556 routes, 32,463 events, 22 activity types).

### Compact Sample (2 traces)
- **Route 100001074918** (14 events): Amsterdam → Liège — Load, Drive, TrafficJam, Border, Unload
- **Route 100001082381** (11 events): Frankfurt → Zurich — Load, Drive, Border, Rest, Unload

### Extended Sample (7 traces)
| Route | Events | Activities | Lat Range | Description |
|-------|--------|------------|-----------|-------------|
| 100001084384 | 288 | 13 | 40.5–52.3° | Longest route — wide European sweep |
| 185000055796 | 179 | 12 | 45.5–49.0° | Long Central European route |
| 151000020750 | 148 | 10 | 48.1–51.6° | Medium-long route |
| 100001082337 | 44 | — | 48.9–50.0° | Short regional route |
| 100001082414 | 39 | — | 45.7–47.5° | Short regional route |
| 100001082381 | 24 | — | 47.4–50.1° | Frankfurt → Zurich |
| 100001082397 | 26 | — | 51.4–52.4° | Short local route |

## Spatial Attributes

| Attribute | Type | Level | Example |
|-----------|------|-------|---------|
| `space:lat` | float | Event | `52.3676` (Amsterdam) |
| `space:lon` | float | Event | `4.9041` (Amsterdam) |
| `space:crs` | string | Event | `"EPSG:4326"` |
| `telemetry:speed` | float | Event | `85.0` (km/h) |
| `telemetry:mileage` | float | Event | `1234.5` (km cumulative) |

**Spatial style:** Trajectory (sequential GPS points forming a path)  
**CRS:** EPSG:4326 (WGS84 standard GPS)

### Activity Types
Load, Drive, TrafficJam, Border, Rest, Unload, Fuel, CouplingTrailer, UncouplingTrailer, Weighing, Customs, and others.

## What This Sample Demonstrates

- GPS trajectory data — sequential coordinates trace continuous paths across roads
- Telemetry attributes (speed, mileage) adding a motion dimension
- Diverse route lengths — from 24-event local deliveries to 288-event cross-European journeys
- Rich activity vocabulary — logistics operations (Load, Drive, Border, Rest, TrafficJam, etc.)
- The best example of spatial-temporal process mining in the project
