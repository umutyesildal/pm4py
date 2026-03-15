"""Public API: validate, normalize_types, normalize_crs, effective_crs, strip_spatial, detect_spatial_columns."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
from pm4py.objects.log.obj import EventLog

from pm4py.spatial.constants import (
    SPACE_CRS,
    SPACE_X,
    SPACE_Y,
    SPACE_LEVEL,
    SPACE_LOCATION,
    X_ALIASES,
    Y_ALIASES,
    LEVEL_ALIASES,
    LOCATION_ALIASES,
)
from pm4py.spatial.exceptions import (
    SpatialValidationError,
    MissingSpatialAttributeError,
    MissingCRSError,
)
from pm4py.spatial.df import to_dataframe, from_dataframe, get_log_crs, LogInput
from pm4py.spatial.crs import transform_coords, is_transformable

# Spatial column prefixes used by strip_spatial
_SPATIAL_PREFIX = "space:"


# ---------------------------------------------------------------------------
# Column detection
# ---------------------------------------------------------------------------

class SpatialColumns:
    """Resolved spatial column names for a given DataFrame."""

    __slots__ = ("x", "y", "crs", "level", "location")

    def __init__(
        self,
        x: str | None,
        y: str | None,
        crs: str | None,
        level: str | None,
        location: str | None,
    ):
        self.x = x
        self.y = y
        self.crs = crs
        self.level = level
        self.location = location

    def has_coords(self) -> bool:
        return self.x is not None and self.y is not None

    def __repr__(self) -> str:
        return (
            f"SpatialColumns(x={self.x!r}, y={self.y!r}, crs={self.crs!r}, "
            f"level={self.level!r}, location={self.location!r})"
        )


def _find_col(df: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    """Return the first alias that exists as a column in df, or None."""
    for alias in aliases:
        if alias in df.columns:
            return alias
    return None


def detect_spatial_columns(df: pd.DataFrame) -> SpatialColumns:
    """Auto-detect which spatial columns are present in the DataFrame.

    Checks known aliases for x/y coordinates, level, and location columns.
    CRS is always looked up by the canonical key ``space:crs``.
    """
    return SpatialColumns(
        x=_find_col(df, X_ALIASES),
        y=_find_col(df, Y_ALIASES),
        crs=SPACE_CRS if SPACE_CRS in df.columns else None,
        level=_find_col(df, LEVEL_ALIASES),
        location=_find_col(df, LOCATION_ALIASES),
    )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def effective_crs(log: LogInput, event: dict | pd.Series, *, log_crs: str | None = None) -> str | None:
    """Return the CRS for a single event: event-level overrides log-level."""
    event_crs = event.get(SPACE_CRS)
    if event_crs is not None and str(event_crs).strip() and str(event_crs) != "nan":
        return str(event_crs).strip()
    return get_log_crs(log, log_crs)


def strip_spatial(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the DataFrame with all space:* columns removed."""
    spatial_cols = [c for c in df.columns if c.startswith(_SPATIAL_PREFIX)]
    return df.drop(columns=spatial_cols)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(
    log: LogInput,
    *,
    log_crs: str | None = None,
    strict: bool = False,
) -> None:
    """Validate spatial attributes in all events.

    Auto-detects coordinate columns (space:x/y, space:lat/lon, etc.).
    Accepts EventLog or DataFrame.  For DataFrame input, pass log_crs if
    the log-level CRS is not stored in event rows.

    strict=True enables CRS-aware range checks (e.g. latitude in [-90,90]
    for EPSG:4326).

    Raises SpatialValidationError (or subclass) on the first problem found.
    """
    df = to_dataframe(log)
    resolved_log_crs = get_log_crs(log, log_crs)
    cols = detect_spatial_columns(df)

    for idx, row in df.iterrows():
        case_id = row.get("case:concept:name", "?")
        _loc = f"case '{case_id}', row {idx}"

        has_x = cols.x is not None and pd.notna(row.get(cols.x))
        has_y = cols.y is not None and pd.notna(row.get(cols.y))

        # x/y must appear together
        if has_x != has_y:
            present = cols.x if has_x else cols.y
            missing = cols.y if has_x else cols.x
            missing_label = missing if missing else ("y-coordinate" if has_x else "x-coordinate")
            raise MissingSpatialAttributeError(
                f"{_loc}: '{present}' present but '{missing_label}' is missing."
            )

        # x/y must be convertible to float and finite
        if has_x:
            for key in (cols.x, cols.y):
                try:
                    val = float(row[key])
                except (ValueError, TypeError):
                    raise SpatialValidationError(
                        f"{_loc}: '{key}' value {row[key]!r} is not a valid number."
                    )
                if not np.isfinite(val):
                    raise SpatialValidationError(
                        f"{_loc}: '{key}' value {val} is not finite (NaN or inf)."
                    )

        # CRS resolvable when coordinates exist
        if has_x:
            evt_crs = row.get(SPACE_CRS)
            evt_crs_str = None
            if pd.notna(evt_crs) and str(evt_crs).strip():
                evt_crs_str = str(evt_crs).strip()

            eff_crs = evt_crs_str or resolved_log_crs
            if eff_crs is None:
                raise MissingCRSError(
                    f"{_loc}: coordinates present but no CRS found "
                    f"(neither event-level nor log-level)."
                )

            # Strict mode: CRS-aware range checks
            if strict and eff_crs:
                _validate_ranges(row, cols, eff_crs, _loc)

        # Optional string-like fields
        for key in (cols.level, cols.location):
            if key is not None and key in df.columns and pd.notna(row.get(key)):
                val = row[key]
                if not isinstance(val, str):
                    try:
                        str(val)
                    except Exception:
                        raise SpatialValidationError(
                            f"{_loc}: '{key}' value {val!r} is not string-like."
                        )


def _validate_ranges(row: pd.Series, cols: SpatialColumns, crs: str, loc: str) -> None:
    """CRS-aware coordinate range validation (called when strict=True)."""
    crs_upper = crs.upper()
    x_val = float(row[cols.x])
    y_val = float(row[cols.y])

    # EPSG:4326 (WGS84):
    #   If using always_xy columns (space:x / space:lon): x = longitude, y = latitude
    #   If using space:lat / space:lon directly: detect by column name
    if crs_upper == "EPSG:4326":
        # Determine which value is longitude and which is latitude
        # based on the actual column names
        if cols.x in ("space:lon", "space:longitude"):
            lon_val, lat_val = x_val, y_val
        elif cols.x in ("space:lat", "space:latitude"):
            # Unusual but possible: if x-alias matched lat first
            lat_val, lon_val = x_val, y_val
        else:
            # space:x / space:y with always_xy: x=lon, y=lat
            lon_val, lat_val = x_val, y_val

        if not (-180.0 <= lon_val <= 180.0):
            lon_col = cols.x if cols.x in ("space:lon", "space:longitude", "space:x") else cols.y
            raise SpatialValidationError(
                f"{loc}: {lon_col}={lon_val} out of range for {crs} "
                f"(longitude must be in [-180, 180])."
            )
        if not (-90.0 <= lat_val <= 90.0):
            lat_col = cols.y if cols.y in ("space:lat", "space:latitude", "space:y") else cols.x
            raise SpatialValidationError(
                f"{loc}: {lat_col}={lat_val} out of range for {crs} "
                f"(latitude must be in [-90, 90])."
            )


# ---------------------------------------------------------------------------
# Type normalization
# ---------------------------------------------------------------------------

def normalize_types(
    log: LogInput,
    *,
    on_error: Literal["raise", "drop_event", "drop_trace"] = "raise",
) -> pd.DataFrame:
    """Ensure coordinate columns are floats, level/location columns are strings.

    Auto-detects spatial column names (space:x/y, space:lat/lon, etc.).
    Returns a new DataFrame (input is not modified).  Log-level CRS is
    preserved in df.attrs["space:crs"].
    """
    df = to_dataframe(log).copy()
    log_crs_val = get_log_crs(log)
    cols = detect_spatial_columns(df)

    # Nothing to do if no coordinate columns detected
    if not cols.has_coords():
        if log_crs_val:
            df.attrs[SPACE_CRS] = log_crs_val
        return df

    bad_mask = pd.Series(False, index=df.index)

    for key in (cols.x, cols.y):
        if key is None or key not in df.columns:
            continue
        original = df[key].copy()
        df[key] = pd.to_numeric(df[key], errors="coerce")
        coercion_failed = df[key].isna() & original.notna()
        bad_mask |= coercion_failed

    # Coerce optional string fields
    for key in (cols.level, cols.location):
        if key is not None and key in df.columns:
            df[key] = df[key].astype(str).replace("nan", pd.NA)

    if bad_mask.any():
        if on_error == "raise":
            first_bad = df[bad_mask].iloc[0]
            raise SpatialValidationError(
                f"Cannot convert spatial values to float in case "
                f"'{first_bad.get('case:concept:name', '?')}'."
            )
        elif on_error == "drop_event":
            df = df[~bad_mask].reset_index(drop=True)
        elif on_error == "drop_trace":
            bad_cases = df.loc[bad_mask, "case:concept:name"].unique()
            df = df[~df["case:concept:name"].isin(bad_cases)].reset_index(drop=True)

    if log_crs_val:
        df.attrs[SPACE_CRS] = log_crs_val
    return df


# ---------------------------------------------------------------------------
# CRS normalization
# ---------------------------------------------------------------------------

def normalize_crs(
    log: LogInput,
    target_crs: str,
    *,
    log_crs: str | None = None,
    on_missing: Literal["raise", "skip"] = "raise",
) -> pd.DataFrame:
    """Transform all coordinate columns into target_crs.

    Auto-detects coordinate columns (space:x/y, space:lat/lon, etc.).
    Returns a new DataFrame (input is not modified) with all coordinates in
    target_crs. The event-level space:crs column is removed and
    df.attrs["space:crs"] is set to target_crs.

    Non-transformable CRS values (e.g. LOCAL_METERS) will raise a clear
    error if transformation is attempted.
    """
    df = to_dataframe(log).copy()
    resolved_log_crs = get_log_crs(log, log_crs)
    cols = detect_spatial_columns(df)

    if not cols.has_coords():
        df.attrs[SPACE_CRS] = target_crs
        return df

    # Resolve effective CRS per row
    if SPACE_CRS in df.columns:
        eff = df[SPACE_CRS].astype(str).replace("nan", "").replace("None", "").str.strip()
    else:
        eff = pd.Series("", index=df.index)

    # Fill blanks with log-level CRS
    if resolved_log_crs:
        eff = eff.where(eff != "", resolved_log_crs)

    has_coords = df[cols.x].notna() & df[cols.y].notna()
    missing_crs = has_coords & (eff == "")

    if missing_crs.any() and on_missing == "raise":
        first_bad = df[missing_crs].iloc[0]
        raise MissingCRSError(
            f"No CRS for event in case '{first_bad.get('case:concept:name', '?')}'. "
            f"Set log-level space:crs or provide event-level space:crs."
        )

    # Group by source CRS and batch-transform
    needs_transform = has_coords & (eff != "") & (eff != target_crs)
    for src_crs, group in df[needs_transform].groupby(eff[needs_transform]):
        new_x, new_y = transform_coords(
            group[cols.x].values,
            group[cols.y].values,
            str(src_crs),
            target_crs,
        )
        df.loc[group.index, cols.x] = new_x
        df.loc[group.index, cols.y] = new_y

    # Clean up: remove event-level CRS column
    if SPACE_CRS in df.columns:
        df.drop(columns=[SPACE_CRS], inplace=True)

    df.attrs[SPACE_CRS] = target_crs
    return df
