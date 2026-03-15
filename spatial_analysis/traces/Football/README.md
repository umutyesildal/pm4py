# Football Match Event Data — Spatial Sample

## Dataset

**Domain:** Sports analytics (DFL Bundesliga, match DFL-MAT-J03WR9, November 11, 2022)  
**Source folder:** `data/Event_Logs/football/`  
**Data origin:** Real (DFL match event data)

## Sample File

| File | Traces | Events | Description |
|------|--------|--------|-------------|
| `Football_SpatialSample.xes` | 1 | 15 | Opening minutes of the match — 6 activity types |

The sample was created from `Football.xes` (1 trace, 1,452 events, 344 columns). The original file uses legacy attribute names (`X-Position`, `Y-Position`) instead of the `space:` namespace, so this sample remaps them to standardized names.

### Activities Covered
KickOff, Play, TacklingGame, GoalKick, OtherBallAction, ShotAtGoal (6 of 20 types)

## Spatial Attributes

| Attribute | Type | Level | Example |
|-----------|------|-------|---------|
| `space:x` | float | Event | `52.50` (centre circle) |
| `space:y` | float | Event | `34.00` (centre line) |
| `space:x_source` | float | Event | `81.86` (pass origin) |
| `space:y_source` | float | Event | `56.06` (pass origin) |
| `space:crs` | string | Event | `"LOCAL:pitch"` |

**Spatial style:** Point (local 2D coordinates)  
**CRS:** LOCAL:pitch — football pitch coordinate system (0–105 m × 0–68 m, origin at bottom-left)

### Source vs. Position Coordinates
Some events have `space:x_source` / `space:y_source` values that differ from `space:x` / `space:y`. These represent actions where the ball moves — e.g., a pass starts at the source position and arrives at the event position. This trajectory-within-event pattern is unique to this dataset.

## What This Sample Demonstrates

- Local 2D coordinate system (not GPS)
- Source/destination coordinates within a single event (pass trajectories)
- Dense spatial data — every event has coordinates
- Remapping from legacy attribute names to `space:` namespace
