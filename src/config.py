# config.py
"""
Project‐wide constants and parameters.

This file collects:
  - API URLs and CSV‐parsing indices,
  - Stop IDs for “Zoo” and “Toompark”,
  - Walking durations (seconds),
  - Monte Carlo settings,
  - Jitter settings, etc.
"""

from datetime import time

# ┌───────────────────────────────────────────────────────────────────────────┐
# │                          API + CSV Constants                              │
# └───────────────────────────────────────────────────────────────────────────┘
API_ENDPOINT_TEMPLATE = "https://transport.tallinn.ee/siri-stop-departures.php?stopid={stop_id}"
TARGET_BUS_LINE = "8"

# CSV field positions (fields are comma‐separated lines returned by the API).
BUS_TYPE_IDX = 0
ROUTE_NUM_IDX = 1
TIME_SECS_IDX = 2  # “seconds since midnight” field

# ┌───────────────────────────────────────────────────────────────────────────┐
# │                             Stop Identifiers                              │
# └───────────────────────────────────────────────────────────────────────────┘
ZOO_STOP_ID = 822
TOOMPARK_STOP_ID = 1769

# ┌───────────────────────────────────────────────────────────────────────────┐
# │                           Walk Durations (seconds)                        │
# └───────────────────────────────────────────────────────────────────────────┘
WALK_DURATION_HOME_TO_ZOO = 5 * 60  # 5 minutes (in seconds)
WALK_DURATION_TOOMPARK_TO_OFFICE = 4 * 60  # 4 minutes
BUS_TRAVEL_BASE_SECONDS = 720  # 12 minutes

# ┌───────────────────────────────────────────────────────────────────────────┐
# │                        Simulation Time Window                             │
# └───────────────────────────────────────────────────────────────────────────┘
# When to start checking departures (local time)
START_TIME = time(hour=20, minute=15)
# Deadline for arriving (local time)
MEETING_TIME = time(hour=21, minute=15)

# ┌───────────────────────────────────────────────────────────────────────────┐
# │                        Monte Carlo Parameters                             │
# └───────────────────────────────────────────────────────────────────────────┘
MONTE_CARLO_ITERATIONS = 200_000

# ┌───────────────────────────────────────────────────────────────────────────┐
# │                            Jitter Settings                                │
# └───────────────────────────────────────────────────────────────────────────┘
WALK_VARIABILITY_SECONDS = 30  # ±30s random walk jitter
BUS_TRAVEL_VARIABILITY_SECONDS = 60  # ±60s random bus–ride jitter
BUS_DEPARTURE_JITTER_SECONDS = 20  # ±20s bus departure jitter

# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         Simulation Granularity                            │
# └───────────────────────────────────────────────────────────────────────────┘
STEP_INTERVAL_SECONDS = 30  # Step simulation every 30 seconds
