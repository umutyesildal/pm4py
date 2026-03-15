# Native Spatial Extension for PM4Py (Update Report)

**Date:** March 15, 2026  
**Branch:** `pm4py_spatial`

## Overview

This report details the architectural migration and native integration of the **XES Spatial Extension** capabilities directly into the core [PM4Py](https://pm4py.fit.fraunhofer.de/) library. 

Previously, spatial functionalities were housed in a secondary, parallel package (`pm4py_spatial`). By moving these features natively into the repository, we eliminate external dependencies, allow native interpretation of spatial extensions by the PM4Py XML parsers, and simplify the developer workflow for spatial-aware process mining.

## 1. Native PM4Py Core Integration

The fundamental breakthrough was making PM4Py recognize the XES `space:` extension at the foundational object level.

- **`XESExtension` Expansion:** 
  The default PM4Py XES Extension `Enum` located at `pm4py.objects.log.obj` was updated to explicitly include the `Space` extension.
  ```python
  Space = ("Space", "space", "space.xesext")
  ```
- **Automated Lifecycle Processing:** By registering this enum, PM4Py’s built-in parsers (`iterparse`, `etree`) and writers automatically acknowledge, capture, and rewrite the `<extension name="Space" prefix="space" uri="space.xesext" />` XES headers. There is no longer a need to "hack" the extension into memory manually.

## 2. API Restructuring & Import Porting

The standalone `pm4py_spatial` library structure was fully ported and merged inside standard PM4Py:

- **Moved Library Source:** Copied `spatial_analysis/pm4py_spatial/` logic directly into `pm4py/spatial/`.
- **Top-Level Exposure:** To guarantee ease-of-use, the module is exposed natively at the library's root interface in `pm4py/__init__.py`. Users can immediately leverage spatial tooling right alongside legacy packages:
  ```python
  import pm4py
  
  # The spatial package is instantly reachable
  columns = pm4py.spatial.detect_spatial_columns(log)
  df = pm4py.spatial.normalize_types(log)
  ```
- **Namespaces Fixed:** All internal module imports within the integrated files were modified from local absolute syntax (`import pm4py_spatial.crs`) to the package-native syntax (`import pm4py.spatial.crs`), cementing them within the repository.
- **DataFrame Hook Removal:** With the enum now natively available, the manual dictionary injection workaround used previously during `from_dataframe()` conversions was completely purged from `pm4py/spatial/df.py`. PM4Py's `to_event_log` handles the XES mapping intrinsically.

## 3. Test Integrations and Trace Routing

The testing architectures were brought into PM4Py’s native automated testbed.

- **Copied Unit & Integration Tests:** The verification scripts (`test_all.py` and `test_traces_integration.py`) and their mock file data (`synthetic_spatial.xes`) were assimilated straight into the main `pm4py/tests/` pipeline.
- **Routing Patches:** Paths calling the realistic project mocks (e.g. `Synthetic_Bottling_Factory`, `Citibike`, `Truck_Shipment`) were realigned dynamically to resolve pointing into `spatial_analysis/traces/` accurately from the deeper execution context.
- **String Types Resolution:** `test_all.py` was patched to appropriately conform to the latest Pandas standard (`<StringDtype>`), preserving logic robustness. 
- **Verifications Passed:** Running the new spatial test suite completes seamlessly (`12 passed`), definitively validating:
  - Strict/Loose Type validations
  - Datasets detection mechanisms
  - Safe CRS transformations

### How to Run the Spatial Tests Locally

To execute the integrated spatial tests and verify the module logic on your local machine, run the following command from the root `pm4py` directory:

```bash
python3 -m pytest -v -s tests/test_all.py tests/test_traces_integration.py
```

*Note: The `-s` flag ensures the console prints out the visual step-by-step progress headers (e.g., `=== Test 1: normalize_types does not mutate input ===`), and `-v` provides verbose output to trace exactly which tests pass.*

## 4. Git Ignore Additions

To comply with the dataset tracking hygiene, rules suppressing the inclusion of heavy telemetry `.xes` datasets belonging to `Truck_Shipment` and `TruckShipment_ExtendedSpatialSample` were actively codified into `.gitignore`.

## Conclusion 

The SAEL-IMPL project's goal of structured spatial location enhancement is now fully native to PM4Py. Developers no longer need a custom fork or an independently managed module to utilize features handling spatial coordinate structures (`space:x`, `space:y`) or dynamic CRS transformations (`EPSG:4326`, `LOCAL_METERS`). The spatial logic is ready for upstream contribution or distribution.