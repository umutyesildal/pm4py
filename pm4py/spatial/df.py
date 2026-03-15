"""DataFrame ↔ PM4Py EventLog conversions preserving spatial attributes."""

from __future__ import annotations

from typing import Union

import pandas as pd
import pm4py
from pm4py.objects.log.obj import EventLog


LogInput = Union[EventLog, pd.DataFrame]


def to_dataframe(log: LogInput) -> pd.DataFrame:
    """Convert a PM4Py EventLog (or passthrough a DataFrame) to a DataFrame."""
    if isinstance(log, pd.DataFrame):
        return log
    return pm4py.convert.convert_to_dataframe(log)


def from_dataframe(
    df: pd.DataFrame,
    *,
    case_id_key: str = "case:concept:name",
) -> EventLog:
    """Convert a DataFrame back to a PM4Py EventLog."""
    return pm4py.convert.convert_to_event_log(df, case_id_key=case_id_key)


def get_log_crs(log: LogInput, log_crs: str | None = None) -> str | None:
    """Extract the log-level CRS from an EventLog or use the provided fallback."""
    if log_crs is not None:
        return log_crs
    if isinstance(log, EventLog):
        val = log.attributes.get("space:crs")
        if val is not None:
            return str(val).strip() or None
    return None
