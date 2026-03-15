# Synthetic Bottling Factory — Spatial Sample

## Dataset

**Domain:** Manufacturing / bottling line (2-story racetrack layout)  
**Source folder:** `data/Event_Logs/synthetic-bottling-factory/`  
**Data origin:** Entirely synthetic (fictional factory)

## Sample File

| File | Traces | Events | Description |
|------|--------|--------|-------------|
| `Bottling_SpatialSample.xes` | 3 | 28 | Three bottles traversing the production line |

This is a copy of `bottling_racetrack_2floor_sample.xes` from the source folder. The full dataset has 100 traces and 3,596 events.

### Process Flow
**Floor 1:** Infeed → Depalletize → Rinse → Fill → Cap → Label → Check → LiftUp → VerticalTransferUp  
**Floor 2:** Pack → Palletize → OutboundScan  
**Exceptions:** Recap loop (low torque retry), Reject lane (QC failure)

## Spatial Attributes

| Attribute | Type | Level | Example |
|-----------|------|-------|---------|
| `space:floor` | string | Event | `"F1"`, `"F2"` |
| `space:x` | float | Event | `20.0` |
| `space:y` | float | Event | `5.0` |
| `space:node_id` | string | Event | `"N3_RINSE"` |
| `net:edge_id` | string | Event | `"E2_3"` |
| `net:fraction` | float | Event | `0.5` (midpoint along conveyor) |
| `space:crs` | string | Event | `"LOCAL_METERS"` |

**Spatial style:** Point + Network (dual representation)  
**CRS:** LOCAL_METERS (factory floor plan in meters)

This is the most **spatially rich** dataset in the project — it combines geometric point coordinates with a topological network graph (nodes = stations, edges = conveyor segments). Supporting layout files (`layout_nodes.csv`, `layout_edges.csv`) define the factory graph.

## What This Sample Demonstrates

- Multi-floor spatial layout (vertical movement between floors)
- Dual representation: geometric coordinates + network graph topology
- Network attributes (`net:edge_id`, `net:fraction`) for position along conveyor segments
- Exception paths (recap, reject) that change spatial routing
