"""Example 02 – Process discovery on a spatial-enriched log.

Shows that a spatially-enriched DataFrame feeds directly into standard PM4Py
algorithms (inductive miner). Demonstrates strip_spatial to remove spatial
columns before discovery if desired.
Uses the Synthetic Bottling Factory sample from the project's traces/ folder.
"""

import os
import pm4py
import pm4py_spatial

# ── 1. Load XES ──────────────────────────────────────────────────────────────
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
xes_path = os.path.join(
    project_root, "traces", "Synthetic_Bottling_Factory", "Bottling_SpatialSample.xes"
)

if not os.path.exists(xes_path):
    print(f"XES file not found at {xes_path}")
    print("Make sure the traces/ folder exists in the project root.")
    raise SystemExit(1)

# Read as legacy EventLog to access log-level attributes
log = pm4py.read_xes(xes_path, return_legacy_log_object=True)
print(f"Loaded '{log.attributes.get('concept:name', '?')}': {len(log)} traces")
print(f"Log-level CRS: {log.attributes.get('space:crs')}")

# ── 2. Normalize types → DataFrame ──────────────────────────────────────────
df = pm4py_spatial.normalize_types(log)
print(f"✓ Types normalized — {len(df)} events")

# ── 3. Quick spatial summary ─────────────────────────────────────────────────
spatial_cols = [c for c in df.columns if c.startswith("space:")]
print(f"Spatial columns: {spatial_cols}")
if pm4py_spatial.SPACE_X in df.columns:
    print(f"  x range: [{df[pm4py_spatial.SPACE_X].min():.2f}, {df[pm4py_spatial.SPACE_X].max():.2f}]")
    print(f"  y range: [{df[pm4py_spatial.SPACE_Y].min():.2f}, {df[pm4py_spatial.SPACE_Y].max():.2f}]")

# ── 4. strip_spatial → clean DataFrame for mining ────────────────────────────
df_clean = pm4py_spatial.strip_spatial(df)
print(f"\nAfter strip_spatial: {len(df_clean.columns)} columns (was {len(df.columns)})")
print(f"  Remaining: {list(df_clean.columns)}")

# ── 5. Standard PM4Py discovery ──────────────────────────────────────────────
print("\nRunning Inductive Miner...")
net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(df_clean)
print(f"✓ Petri net: {len(net.places)} places, {len(net.transitions)} transitions")

# ── 6. Fitness check ─────────────────────────────────────────────────────────
fitness = pm4py.fitness_token_based_replay(df_clean, net, initial_marking, final_marking)
print(f"Token-based replay fitness: {fitness['average_trace_fitness']:.4f}")

print("\nDone — strip_spatial removed spatial columns cleanly before PM4Py mining.")
