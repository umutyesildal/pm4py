# Brazilian Court Judicial Process — Spatial Sample

## Dataset

**Domain:** Lawsuit movement histories in a Brazilian court system (2020)  
**Source folder:** `data/Event_Logs/Brazilian_Court/`  
**Data origin:** Real (Brazilian court records)

## Sample File

| File | Traces | Events per Trace | Description |
|------|--------|------------------|-------------|
| `BrazilianCourt_SpatialSample.xes` | 3 | 5–20 | Lawsuits moving across different court departments |

The sample was extracted from `Brazilian_Court_Judicial_Process.xes` (4,795 traces, 266,834 events). Traces were selected to show spatial diversity — lawsuits that traverse multiple court departments.

## Spatial Attributes

| Attribute | Type | Level | Example |
|-----------|------|-------|---------|
| `space:zone_id` | string | Event | Court department ID |
| `space:zone_type` | string | Event | `"court_department"` |

**Spatial style:** Zone (court department)  
**CRS:** N/A (named zones)

Unlike Amazon Sales or BPI-2015 where spatial attributes are at the trace level, here they are at the **event level** — each event may occur in a different court department, representing the lawsuit's movement through the judicial system.

## What This Sample Demonstrates

- Event-level spatial zone attributes (location changes between events)
- Spatial flow: cases moving across organizational zones
- Real judicial process data with corrected Brazilian date formatting (day-first)
