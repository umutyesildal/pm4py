"""CRS helpers: effective CRS resolution and coordinate transformation."""

from __future__ import annotations

from pm4py.spatial.exceptions import SpatialValidationError

# CRS identifiers that are valid spatial references but cannot be
# transformed via pyproj because they lack Earth-anchored parameters.
NON_TRANSFORMABLE_CRS = frozenset({
    "LOCAL_METERS",
    "LOCAL_FEET",
    "LOCAL",
    "PIXEL",
})


def is_transformable(crs: str) -> bool:
    """Return True if the CRS can be resolved by pyproj."""
    return crs.upper() not in NON_TRANSFORMABLE_CRS


def _get_transformer(source_crs: str, target_crs: str):
    """Return a pyproj Transformer (lazy import, cached per pair)."""
    try:
        import pyproj
    except ImportError:
        raise ImportError(
            "pyproj is required for CRS normalization. "
            "Install it with:  pip install pyproj"
        )
    return pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)


# Simple in-memory cache: (src, tgt) -> Transformer
_transformer_cache: dict[tuple[str, str], object] = {}


def get_transformer(source_crs: str, target_crs: str):
    """Get or create a cached pyproj Transformer."""
    key = (source_crs, target_crs)
    if key not in _transformer_cache:
        _transformer_cache[key] = _get_transformer(source_crs, target_crs)
    return _transformer_cache[key]


def transform_coords(
    x_vals,
    y_vals,
    source_crs: str,
    target_crs: str,
):
    """Transform coordinate arrays from source_crs to target_crs.

    Returns (new_x, new_y) as lists.
    Raises SpatialValidationError if source or target is non-transformable.
    """
    if source_crs == target_crs:
        return list(x_vals), list(y_vals)
    if not is_transformable(source_crs):
        raise SpatialValidationError(
            f"Cannot transform from '{source_crs}': it is a local/non-geographic "
            f"CRS without Earth-anchored parameters. Convert to a standard EPSG "
            f"code first, or keep coordinates in their original CRS."
        )
    if not is_transformable(target_crs):
        raise SpatialValidationError(
            f"Cannot transform to '{target_crs}': it is a local/non-geographic "
            f"CRS without Earth-anchored parameters."
        )
    transformer = get_transformer(source_crs, target_crs)
    new_x, new_y = transformer.transform(list(x_vals), list(y_vals))
    return list(new_x), list(new_y)
