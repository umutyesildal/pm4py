# XES Spatial Extension (v2.0)

> **Project:** SAEL-IMPL — Extending XES and pm4py for Spatial-Aware Process Mining  
> **Standard:** IEEE 1849-2023 (XES)  
> **Last Updated:** March 2026

## Overview

A single, minimal XES extension that records the spatial context of process-mining events.  
One `space:` prefix replaces the earlier three-extension approach (`space:` + `net:` + `telemetry:`).

**Key design decision:** coordinates are stored as a generic `x`/`y` pair.  
The CRS attribute specifies what they mean — `EPSG:4326` → x=latitude, y=longitude; `LOCAL_METERS` → x/y in local units, etc.  
This keeps the extension small and CRS-agnostic.

### File

| File | Prefix | URI |
|------|--------|-----|
| [space.xesext](space.xesext) | `space:` | `space.xesext` |

---

## Attributes

### Log-Level (1 attribute)

| Key | Type | Description |
|-----|------|-------------|
| `crs` | string | Default CRS for all events in this log |

### Event-Level (7 attributes)

| Key | Type | Description |
|-----|------|-------------|
| `x` | float | X coordinate (latitude for GPS, x for local) |
| `y` | float | Y coordinate (longitude for GPS, y for local) |
| `level` | string | Vertical level — floor, altitude band, z-layer |
| `crs` | string | CRS for this event (overrides log-level default) |
| `location` | string | Location identifier — station ID, node ID, zone code |
| `label` | string | Human-readable location name |
| `edge` | string | Network edge / link identifier |

**Total: 8 attributes** (1 log + 7 event).

---

## Dataset Mapping

How each dataset maps to the extension attributes:

### Citibike (GPS + station zones)

```xml
<string key="space:crs" value="EPSG:4326"/>          <!-- log level -->

<float  key="space:x"        value="40.69943"/>       <!-- latitude  -->
<float  key="space:y"        value="-73.91337"/>      <!-- longitude -->
<string key="space:location" value="4816.02"/>        <!-- station ID -->
<string key="space:label"    value="Myrtle Ave &amp; Linden St"/>
```

### Synthetic Bottling Factory (local coords + network graph)

```xml
<string key="space:crs" value="LOCAL_METERS"/>        <!-- log level -->

<float  key="space:x"        value="10"/>             <!-- x -->
<float  key="space:y"        value="5"/>              <!-- y -->
<string key="space:level"    value="F1"/>             <!-- floor -->
<string key="space:location" value="N2_DEPAL"/>       <!-- graph node -->
<string key="space:edge"     value="E1"/>             <!-- graph edge -->
```

### Truck Shipment (GPS trajectory)

```xml
<string key="space:crs" value="EPSG:4326"/>           <!-- log level -->

<float  key="space:x"        value="52.29576"/>       <!-- latitude  -->
<float  key="space:y"        value="4.77082"/>        <!-- longitude -->
```

---

## Design Rationale

1. **Single extension** — spatial position, named locations, and network topology are all aspects of "where."  
   Splitting them into separate prefixes added complexity without clear benefit.

2. **Generic coordinates** — `x`/`y` instead of separate `lat`/`lon`/`x`/`y`.  
   The CRS tells consumers how to interpret the values. One pair covers GPS, local, and projected systems.

3. **No telemetry** — speed, mileage, and similar motion metrics are domain-specific, not spatial metadata.  
   They can remain as regular (unprefixed) event attributes.

4. **No trace-level** — address fields (city, state, country) from the dropped datasets are removed.  
   All spatial data is at the event level, which is the natural granularity for location.

5. **Follows standard patterns** — structure mirrors the official `concept.xesext`, `time.xesext`, and `org.xesext` (same root element, alias format, 5 languages).

---

## Example: Full XES Log

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<log xes.version="1849-2016" xes.features="nested-attributes"
     xmlns="http://www.xes-standard.org/">

  <extension name="Concept"   prefix="concept"   uri="http://www.xes-standard.org/concept.xesext"/>
  <extension name="Time"      prefix="time"      uri="http://www.xes-standard.org/time.xesext"/>
  <extension name="Lifecycle" prefix="lifecycle"  uri="http://www.xes-standard.org/lifecycle.xesext"/>
  <extension name="Spatial"   prefix="space"      uri="space.xesext"/>

  <string key="space:crs" value="EPSG:4326"/>

  <trace>
    <string key="concept:name" value="TRIP_001"/>
    <event>
      <string key="concept:name"          value="Departure"/>
      <date   key="time:timestamp"        value="2026-01-15T08:30:00+01:00"/>
      <float  key="space:x"              value="52.520"/>
      <float  key="space:y"              value="13.405"/>
      <string key="space:location"        value="BER_HBF"/>
      <string key="space:label"           value="Berlin Hauptbahnhof"/>
    </event>
    <event>
      <string key="concept:name"          value="Arrival"/>
      <date   key="time:timestamp"        value="2026-01-15T12:15:00+01:00"/>
      <float  key="space:x"              value="48.137"/>
      <float  key="space:y"              value="11.576"/>
      <string key="space:location"        value="MUC_HBF"/>
      <string key="space:label"           value="München Hauptbahnhof"/>
    </event>
  </trace>
</log>
```
