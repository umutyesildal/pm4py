class SpatialValidationError(ValueError):
    """Raised when spatial attributes fail validation."""


class MissingSpatialAttributeError(SpatialValidationError):
    """Raised when a required spatial attribute is missing."""


class MissingCRSError(SpatialValidationError):
    """Raised when no CRS is available (neither event-level nor log-level)."""
