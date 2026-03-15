# Attribute keys matching the space.xesext extension (prefix "space:")
SPACE_CRS = "space:crs"
SPACE_X = "space:x"
SPACE_Y = "space:y"
SPACE_LEVEL = "space:level"
SPACE_LOCATION = "space:location"

# Known alternative column names used in real-world XES files.
# Each maps to the canonical constant above.
# Order matters: first match wins in auto-detection.
X_ALIASES = ("space:x", "space:lon", "space:longitude")
Y_ALIASES = ("space:y", "space:lat", "space:latitude")
LEVEL_ALIASES = ("space:level", "space:floor", "space:z")
LOCATION_ALIASES = (
    "space:location",
    "space:zone_name",
    "space:zone_id",
    "space:node_id",
    "space:station",
    "space:room",
)
