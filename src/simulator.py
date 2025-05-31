import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple

from config import (
    WALK_VARIABILITY_SECONDS,
    BUS_DEPARTURE_JITTER_SECONDS,
    BUS_TRAVEL_VARIABILITY_SECONDS,
)


def _find_catchable_bus(arrive_zoo: datetime,
                        trips: List[Tuple[datetime, datetime]]) -> Tuple[datetime, datetime, float]:
    """
    Among the scheduled (sched_dep, sched_arr) in `trips`, add a random
    triangular jitter to each sched_dep.  Return the first (actual_dep, sched_arr, base_ride)
    such that actual_dep >= arrive_zoo.  If none qualifies, fall back to the last trip (forcing lateness).

    Returns:
      (bus_dep_actual, scheduled_arrival, base_ride_seconds)

    - bus_dep_actual:  a datetime = sched_dep + jitter
    - scheduled_arrival: the original sched_arr (datetime)
    - base_ride_seconds: (sched_arr - sched_dep).total_seconds()

    If `trips` is empty, returns (arrive_zoo, arrive_zoo, 0.0).
    """
    if not trips:
        # No scheduled trips at all: force lateness
        return arrive_zoo, arrive_zoo, 0.0

    # Try each scheduled departure in order:
    for sched_dep, sched_arr in trips:
        dep_jitter = np.random.triangular(-BUS_DEPARTURE_JITTER_SECONDS, 0, BUS_DEPARTURE_JITTER_SECONDS)
        actual_dep = sched_dep + timedelta(seconds=dep_jitter)
        if actual_dep >= arrive_zoo:
            base_ride = (sched_arr - sched_dep).total_seconds()
            return actual_dep, sched_arr, base_ride

    # If no bus (after jitter) departs after arrive_zoo, pick the last one:
    last_sched_dep, last_sched_arr = trips[-1]
    dep_jitter = np.random.triangular(-BUS_DEPARTURE_JITTER_SECONDS, 0, BUS_DEPARTURE_JITTER_SECONDS)
    actual_dep = last_sched_dep + timedelta(seconds=dep_jitter)
    base_ride = (last_sched_arr - last_sched_dep).total_seconds()
    return actual_dep, last_sched_arr, base_ride


class Simulator:
    def __init__(self,
                 class_start: datetime,
                 walk_home_to_zoo: float,
                 walk_toompark_to_office: float):
        """
        Args:
          class_start:            datetime at which Rita must be in the office by.
          walk_home_to_zoo:       base walking time from home→zoo (seconds).
          walk_toompark_to_office: base walking time from toompark→office (seconds).
        """
        self.class_start = class_start
        self.walk_home = walk_home_to_zoo
        self.walk_office = walk_toompark_to_office

    def simulate_step(self, departure: datetime, trips: List[Tuple[datetime, datetime]]) -> dict:
        """
        1) Jitter Rita’s walk from home → zoo.
        2) Find the next catchable bus *after* she arrives (including departure jitter).
        3) Jitter the bus’s ride time.
        4) Jitter the final walk from toompark → office.
        5) Compute lateness in seconds (clamped at zero).

        Returns a dict containing:
          "departure" : the departure time (datetime),
          "walk_end"  : when Rita arrives at the zoo stop (datetime),
          "walk_dur"  : (walk_end - departure).seconds,
          "bus_dep"   : actual bus departure time,
          "wait_dur"  : (bus_dep - walk_end).seconds,  # always ≥ 0
          "ride_dur"  : actual ride duration (seconds),
          "bus_arr"   : actual bus arrival at toompark (datetime),
          "arrival"   : final arrival at office (datetime),
          "lateness"  : max(0, (arrival - class_start).seconds)
        """
        # 1) Walk to station with triangular jitter
        walk_jitter = np.random.triangular(-WALK_VARIABILITY_SECONDS, 0, WALK_VARIABILITY_SECONDS)
        walk_end = departure + timedelta(seconds=self.walk_home + walk_jitter)
        walk_dur = (walk_end - departure).total_seconds()

        # 2) Select next catchable bus (including departure jitter)
        bus_dep_actual, sched_arrival, base_ride_seconds = _find_catchable_bus(walk_end, trips)
        wait_dur = max(0.0, (bus_dep_actual - walk_end).total_seconds())

        # 3) Jitter the ride time
        ride_jitter = np.random.triangular(-BUS_TRAVEL_VARIABILITY_SECONDS, 0, BUS_TRAVEL_VARIABILITY_SECONDS)
        ride_dur = base_ride_seconds + ride_jitter
        bus_arrival = bus_dep_actual + timedelta(seconds=ride_dur)

        # 4) Final walk with triangular jitter
        final_walk_jitter = np.random.triangular(
            -WALK_VARIABILITY_SECONDS,
            0,
            WALK_VARIABILITY_SECONDS
        )
        arrival = bus_arrival + timedelta(seconds=self.walk_office + final_walk_jitter)

        # 5) Compute lateness in seconds (clamped at zero)
        lateness_td = max(timedelta(), arrival - self.class_start)
        lateness_sec = lateness_td.total_seconds()

        return {
            "departure": departure,
            "walk_end":  walk_end,
            "walk_dur":  walk_dur,
            "bus_dep":   bus_dep_actual,
            "wait_dur":  wait_dur,
            "ride_dur":  ride_dur,
            "bus_arr":   bus_arrival,
            "arrival":   arrival,
            "lateness":  lateness_sec,
        }
