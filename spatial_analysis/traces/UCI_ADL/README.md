# UCI Activities of Daily Living — Spatial Sample

## Dataset

**Domain:** Smart home activity monitoring (elderly individuals)  
**Source folder:** `data/Event_Logs/uci-activity-daily-life/`  
**Data origin:** Real (UCI Machine Learning Repository)

## Sample File

| File | Traces | Description |
|------|--------|-------------|
| `UCI_ADL_SpatialSample.xes` | 3 | Person-day traces with room-based spatial zones |

The sample was extracted from `activitylog_uci_detailed_labour_with_rooms_cleaned.xes` (25 weekday traces, 1,392 events). A separate weekend file exists in the source folder (10 traces, 488 events).

### Trace Structure
- **Trace** = one person's day
- **Events** = activity start/complete pairs (interval-based lifecycle)
- **Activities:** watchingtv, washing, toilet, grooming, snack, outdoors, sleeping, prepareBreakfast, eatingBreakfast, prepareLunch, eatingLunch, prepareDinner, eatingDinner, etc.

## Spatial Attributes

| Attribute | Type | Level | Example |
|-----------|------|-------|---------|
| `space:zone_id` | string | Event | `"Kitchen"`, `"Living_Room"`, `"Bedroom"` |
| `space:zone_type` | string | Event | `"room"` |

**Spatial style:** Zone (room-based)  
**CRS:** N/A (named rooms)

Room assignments are derived from activity-to-room mappings (e.g., cooking activities → Kitchen, sleeping → Bedroom). The full mapping is documented in `data/Event_Logs/uci-activity-daily-life/SPATIAL_LAYOUT_MAPPING.md`.

## What This Sample Demonstrates

- Indoor zone-based spatial representation (rooms in a smart home)
- Event-level spatial attributes (person moves between rooms during the day)
- Interval-based lifecycle events (start/complete pairs with possible overlaps)
- Activity-to-location semantic mapping
