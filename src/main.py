"""
Entry point for Rita’s Lateness Simulator.

This file orchestrates:
  1) Parsing command‐line arguments (start time, meeting time, step interval).
  2) Waiting until the specified “start” time‐of‐day.
  3) Sweeping departure times from “start” → “meeting” in `step` increments:
       • Refresh bus schedules every 5 minutes (if all known trips have passed).
       • For each departure time:
           – Simulate one sample path (walk→wait→ride→walk) and log details.
           – Run Monte Carlo to estimate P(late) ∈ [0,1].
           – Enforce monotonic non‐decrease on P(late).
  4) Plotting and saving the final P(late) curve (into `results/` with a timestamp).

Usage:
    python main.py --start 15:31 --meeting 16:31 --step 30
"""

import argparse
import logging
import os
import time
from datetime import datetime, date, timedelta
from typing import List, Tuple, Optional

from simulator import Simulator
from montecarlo import compute_lateness_probability
from config import (
    ZOO_STOP_ID,
    TOOMPARK_STOP_ID,
    START_TIME,
    MEETING_TIME,
    STEP_INTERVAL_SECONDS,
    WALK_DURATION_HOME_TO_ZOO,
    WALK_DURATION_TOOMPARK_TO_OFFICE,
    MONTE_CARLO_ITERATIONS
)
from fetcher import fetch_arrival_datetimes
from matcher import pair_departure_and_destination
from plotter import plot_curve


# ─────────────────────────────────────────────────────────────────────────────
#    Configure the root logger to print INFO+ messages to stdout
# ─────────────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)


def wait_until(target_time: datetime.time) -> datetime:
    """
    Pause execution until the next occurrence of `target_time` (today or, if past, tomorrow).
    Returns the datetime when we “wake up.”
    """
    now = datetime.now()
    today_target = datetime.combine(date.today(), target_time)
    if now > today_target:
        today_target += timedelta(days=1)

    sleep_secs = (today_target - now).total_seconds()
    logger.info(f"Sleeping {int(sleep_secs)}s until {today_target:%H:%M:%S}")
    time.sleep(sleep_secs)
    return today_target


def fetch_and_pair(last_fetch: datetime,
                   current: datetime) -> Tuple[List[Tuple[datetime, datetime]], datetime]:
    """
    Every 5 minutes (300s), refresh bus schedules:
      1) fetch_arrival_datetimes(ZOO_STOP_ID)  → list of zoo departures
      2) fetch_arrival_datetimes(TOOMPARK_STOP_ID) → list of Toompark arrivals
      3) pair_departure_and_destination(...) to build (zoo_dep, toompark_arr) pairs.

    Returns (new_trips, new_last_fetch) if >= 300s since last_fetch,
    otherwise just ([], last_fetch).
    """
    if (last_fetch is None) or ((current - last_fetch).seconds >= 300):
        deps = fetch_arrival_datetimes(ZOO_STOP_ID)
        arrs = fetch_arrival_datetimes(TOOMPARK_STOP_ID)
        return pair_departure_and_destination(deps, arrs), current
    return [], last_fetch


def simulate_curve(start: datetime, end: datetime, step: int):
    """
    Sweep departure‐times from `start` → `end` in increments of `step` seconds.
    For each “current” departure:
      1) Attempt one sample path to see if Rita actually catches a bus (walk→wait→ride→walk).
         If that sample’s bus_dep < walk_end, we know **all** buses in this batch are gone.
         In that case, we immediately refresh schedule and re‐run one sample.
      2) Log that “valid” sample path (walk/wait/ride/walk).
      3) Run a Monte Carlo estimate of P(late) ∈ [0,1], enforce monotonic non‐decrease.
      4) Sleep until exactly “current + step” to keep pacing aligned with real time.
    """
    sim = Simulator(
        class_start=datetime.combine(start.date(), MEETING_TIME),
        walk_home_to_zoo=WALK_DURATION_HOME_TO_ZOO,
        walk_toompark_to_office=WALK_DURATION_TOOMPARK_TO_OFFICE
    )

    trips: List[Tuple[datetime, datetime]] = []
    times: List[datetime] = []
    probs: List[float] = []
    last_fetch: Optional[datetime] = None
    current = start

    logger.info("===== SIMULATION PHASE =====")
    logger.info(f"Window: {start:%H:%M:%S} → {end:%H:%M:%S} (step {step}s)\n")

    while current <= end:
        # 1) If no trips known OR attempts to catch a bus fail, refresh now
        if not trips:
            new_trips, last_fetch = fetch_and_pair(last_fetch, current)
            if new_trips:
                trips = new_trips
                logger.info("  [DATA] Refreshed bus schedule")

        # 2) Take one sample from current trips
        sample = sim.simulate_step(current, trips)

        # 3) If that sample’s bus_dep < walk_end, all buses in this batch are gone.
        #    → Force a schedule refresh, then re‐draw a new sample.
        if sample["bus_dep"] < sample["walk_end"]:
            new_trips, last_fetch = fetch_and_pair(last_fetch, current)
            if new_trips:
                trips = new_trips
                logger.info("  [DATA] Refreshed bus schedule")
            # Re‐draw a “valid” sample
            sample = sim.simulate_step(current, trips)

        # 4) Unpack & log
        walk_end = sample["walk_end"]
        walk_dur = sample["walk_dur"]
        bus_dep = sample["bus_dep"]
        wait_dur = sample["wait_dur"]
        ride_dur = sample["ride_dur"]
        bus_arr = sample["bus_arr"]
        arrival = sample["arrival"]

        logger.info(f"--- Departure at {current:%H:%M:%S} ---")
        logger.info(f"  • Walk to station: {int(walk_dur)}s → arrive at {walk_end:%H:%M:%S}")
        logger.info(f"  • Wait at station: {int(wait_dur)}s → bus at    {bus_dep:%H:%M:%S}")
        logger.info(f"  • Ride on bus:     {int(ride_dur)}s → arrive at {bus_arr:%H:%M:%S}")
        logger.info(f"  • Walk to meeting: {(arrival - bus_arr).seconds}s → arrive at {arrival:%H:%M:%S}")

        # 5) Monte Carlo estimate of P(late)
        raw_p = compute_lateness_probability(sim, current, trips, MONTE_CARLO_ITERATIONS)
        if probs:
            raw_p = max(raw_p, probs[-1])
        p_late = raw_p

        logger.info(f"  • Compute P(late): {p_late:.2f}\n")

        # 6) Store & sleep until the next “step”
        times.append(current)
        probs.append(p_late)

        next_target = current + timedelta(seconds=step)
        now = datetime.now()
        sleep_secs = (next_target - now).total_seconds()
        if sleep_secs > 0:
            time.sleep(sleep_secs)

        current = next_target

    logger.info(f"Simulated {len(times)} steps.")
    return times, probs


def parse_cli():
    """
    Parse command‐line arguments:
      --start   (HH:MM)  [default = START_TIME]
      --meeting (HH:MM)  [default = MEETING_TIME]
      --step    (seconds) [default = STEP_INTERVAL_SECONDS]
    """
    parser = argparse.ArgumentParser(description="Rita's Lateness Simulator")
    parser.add_argument(
        "--start",
        type=lambda s: datetime.strptime(s, "%H:%M").time(),
        default=START_TIME,
        help="Start departure time (HH:MM)"
    )
    parser.add_argument(
        "--meeting",
        type=lambda s: datetime.strptime(s, "%H:%M").time(),
        default=MEETING_TIME,
        help="Meeting time (HH:MM)"
    )
    parser.add_argument(
        "--step",
        type=int,
        default=STEP_INTERVAL_SECONDS,
        help="Simulation time step in seconds"
    )
    return parser.parse_args()


def main():
    args = parse_cli()

    # 1) Wait until “start” (e.g. 15:31:00)
    start = wait_until(args.start)
    end = datetime.combine(start.date(), args.meeting)

    # 2) Sweep departure times and collect (times, p_late)
    times, probs = simulate_curve(start, end, args.step)

    # 3) Create `results/` if needed, then save a timestamped PNG there
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"lateness_curve_{ts}.png"
    output_path = os.path.join(results_dir, output_filename)

    plot_curve(times, probs, filename=output_path)
    logger.info(f"\nSaved P(late) curve to: {output_path}")


if __name__ == "__main__":
    main()
