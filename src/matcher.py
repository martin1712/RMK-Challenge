"""
Pair each “departure‐stop” arrival with the earliest “destination‐stop” arrival ≥ it.

Given two sorted lists of datetime objects—one for departures from Zoo,
one for arrivals at Toompark—produce a list of (zoo_time, toompark_time)
pairs by “two‐pointer” logic.
"""

from datetime import datetime
from typing import List, Tuple

from config import BUS_TRAVEL_BASE_SECONDS, BUS_TRAVEL_VARIABILITY_SECONDS

_MIN_TRAVEL_SECONDS = BUS_TRAVEL_BASE_SECONDS - BUS_TRAVEL_VARIABILITY_SECONDS


def pair_departure_and_destination(
        departure_arrivals: List[datetime],
        destination_arrivals: List[datetime]
) -> List[Tuple[datetime, datetime]]:
    """
    Pair each departure‐stop arrival with the earliest “destination” arrival that
    is both ≥ departure_time AND at least _MIN_TRAVEL_SECONDS later.

    Both input lists must be sorted ascending.  We walk through both lists
    in one pass (two‐pointer logic):
      - Let i index departure_arrivals, j index destination_arrivals.
      - While i < len(departure_arrivals) and j < len(destination_arrivals):
          * Let depart_time = departure_arrivals[i]
          * Let dest_time   = destination_arrivals[j]
          * If (dest_time - depart_time) ≥ _MIN_TRAVEL_SECONDS:
                ➔ pair (depart_time, dest_time), then i += 1, j += 1
          * Else (dest_time too early to be that bus), increment j
            (i.e. skip this too‐soon destination).
      - If we exhaust destination_arrivals before pairing a given departure, that
        departure is dropped.

    Args:
        departure_arrivals (List[datetime]):
            Sorted list of times when buses are scheduled to depart Zoo.
        destination_arrivals (List[datetime]):
            Sorted list of times when buses arrive at Toompark.

    Returns:
        List[Tuple[datetime, datetime]]:
            A list of (departure_time_at_Zoo, arrival_time_at_Toompark), in ascending
            order by departure_time.  Only departures that find a “plausible” arrival
            ≥ (_MIN_TRAVEL_SECONDS after departure) appear.
    """
    paired: List[Tuple[datetime, datetime]] = []
    i, j = 0, 0
    n_dep = len(departure_arrivals)
    n_dest = len(destination_arrivals)

    while i < n_dep and j < n_dest:
        depart_time = departure_arrivals[i]
        dest_time = destination_arrivals[j]

        # Compute how many seconds elapse if that bus were used:
        dt = (dest_time - depart_time).total_seconds()

        if dt >= _MIN_TRAVEL_SECONDS:
            # Valid pairing: dest_time is far enough after depart_time
            paired.append((depart_time, dest_time))
            i += 1
            j += 1
        else:
            # dest_time < depart_time + _MIN_TRAVEL_SECONDS → cannot be that bus
            j += 1

    return paired
