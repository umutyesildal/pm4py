# Spatial Sample Traces

> **Project:** SAEL-IMPL — Extending XES and pm4py for Spatial-Aware Process Mining  
> **Last Updated:** February 2026

This folder contains **spatial sample XES files** — small, curated extracts from each dataset in the project, standardized with the `space:` namespace convention. Each subfolder has its own README with full details on attributes, data origin, and what the sample demonstrates.

---

## Dataset Overview

| # | Folder | Domain | Spatial Style | CRS | Traces | Events |
|---|--------|--------|--------------|-----|--------|--------|
| D1 | [Amazon_Sales](Amazon_Sales/) | E-commerce (India) | Zone (city/state) | N/A | 3 | ~10 |
| D2 | [BPI-2015](BPI-2015/) | Permit applications (NL) | Zone (municipality) | N/A | 3 | 30–90 |
| D3 | [Brazilian_Court](Brazilian_Court/) | Judicial process (BR) | Zone (court dept.) | N/A | 3 | 15–60 |
| D4 | [Citibike](Citibike/) | Bike-sharing (NYC) | Point + Zone (dual) | EPSG:4326 | 5 | 10 |
| D5 | [Football](Football/) | Sports analytics (DFL) | Point (local 2D) | LOCAL:pitch | 1 | 15 |
| D6 | [Synthetic_Bottling_Factory](Synthetic_Bottling_Factory/) | Manufacturing | Point + Network | LOCAL_METERS | 3 | 28 |
| D7 | [UCI_ADL](UCI_ADL/) | Smart home (ADL) | Zone (room) | N/A | 3 | varies |
| D8 | [Truck_Shipment](Truck_Shipment/) | Logistics (EU) | Trajectory (GPS) | EPSG:4326 | 2 + 7 | 25 + 748 |

---

## Spatial Styles Covered

| Style | Description | Datasets |
|-------|-------------|----------|
| **Zone** | Named area / symbolic region | D1, D2, D3, D7 |
| **Point (GPS)** | WGS84 latitude/longitude | D4, D8 |
| **Point (Local 2D)** | Local coordinate system | D5, D6 |
| **Point + Zone (Dual)** | Both coordinates and named zone | D4 |
| **Point + Network** | Coordinates + topological graph | D6 |
| **Trajectory** | Sequential GPS forming a path | D8 |

---

## The `space:` Namespace

All spatial attributes follow a consistent namespace convention (ad-hoc; formal `.xesext` planned):

### Core Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `space:lat` / `space:lon` | float | WGS84 coordinates |
| `space:x` / `space:y` | float | Local 2D coordinates |
| `space:crs` | string | Coordinate reference system |
| `space:zone_id` | string | Zone/area identifier |
| `space:zone_name` | string | Human-readable zone name |
| `space:zone_type` | string | Zone classification |
| `space:floor` | string | Floor/level identifier |
| `space:node_id` | string | Network node identifier |
| `space:city` / `space:state` / `space:country` | string | Administrative location |
| `space:postal_code` | string | Postal/ZIP code |

### Extended Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `space:x_source` / `space:y_source` | float | Origin coordinates (e.g., pass start) |
| `net:edge_id` | string | Network edge identifier |
| `net:fraction` | float | Position along edge (0–1) |
| `telemetry:speed` | float | Vehicle speed (km/h) |
| `telemetry:mileage` | float | Cumulative distance (km) |

### CRS Values

| CRS | Description | Datasets |
|-----|-------------|----------|
| `EPSG:4326` | WGS84 (standard GPS) | D4, D8 |
| `LOCAL:pitch` | Football pitch (105 × 68 m) | D5 |
| `LOCAL_METERS` | Factory floor plan (meters) | D6 |

---

## Data Origin

| Dataset | Spatial Data | Events |
|---------|-------------|--------|
| Amazon Sales | Real (CSV addresses) | Synthetic lifecycle |
| BPI-2015 | Derived (municipality tag) | Real (BPI Challenge) |
| Brazilian Court | Derived (court dept.) | Real (court records) |
| Citibike | Real (station GPS) | Real (trip records) |
| Football | Real (DFL tracking) | Real (match events) |
| Bottling Factory | Synthetic | Synthetic |
| UCI ADL | Derived (activity→room) | Real (UCI repository) |
| Truck Shipment | Real (GPS telemetry) | Real (shipment logs) |

---

## Removed Dataset

**CASAS Smart Home CSVs** were removed — raw sensor streams with no room mapping, redundant with UCI ADL. See individual folder READMEs for full dataset details.

---

## Source Data

Full datasets are in `data/Event_Logs/`. These samples are small extracts (2–7 traces each) for development and testing of the spatial XES extension.
