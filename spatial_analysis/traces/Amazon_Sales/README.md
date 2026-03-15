# Amazon Sales — Spatial Sample

## Dataset

**Domain:** E-commerce order fulfillment (Amazon India, March–June 2022)  
**Source folder:** `data/Event_Logs/Amazon_Sales/`  
**Data origin:** Real CSV data; lifecycle events are synthetic

## Sample File

| File | Traces | Events | Description |
|------|--------|--------|-------------|
| `Amazon_Sales_SpatialSample.xes` | 3 | ~8–12 | Small sample with diverse order statuses (Delivered, Cancelled, Shipped) |

The sample was extracted from `Amazon_Sales_SyntheticLifecycle.xes` (120,229 traces). Traces were selected to cover different final statuses and geographic diversity.

## Spatial Attributes

| Attribute | Type | Level | Example |
|-----------|------|-------|---------|
| `space:city` | string | Trace | `"MUMBAI"` |
| `space:state` | string | Trace | `"MAHARASHTRA"` |
| `space:postal_code` | string | Trace | `"400001"` |
| `space:country` | string | Trace | `"IN"` |

**Spatial style:** Zone (symbolic administrative location)  
**CRS:** N/A (named places, not coordinates)

All spatial attributes are **real** — taken directly from the Amazon India order CSV. They represent the shipping destination of each order while lifecycle events (OrderPlaced → Shipped → Delivered) are synthetically generated.

## What This Sample Demonstrates

- Symbolic/zone-based spatial representation (city, state, postal code)
- Trace-level spatial attributes (all events in a trace share the same location)
- Multiple order lifecycle paths (successful delivery, cancellation, in-transit)
