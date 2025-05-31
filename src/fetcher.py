"""
Fetch upcoming bus‐arrival datetimes for a given stop ID.

Uses `requests` to call the remote API endpoint defined in API_ENDPOINT_TEMPLATE.
Filters only lines of type 'bus' and matching TARGET_BUS_LINE, then converts the
“seconds since midnight” field into a datetime for *today*.  Only future times
(after now) are returned, sorted ascending.
"""

import requests
from datetime import datetime, time as dt_time, timedelta
from typing import List

from config import API_ENDPOINT_TEMPLATE, TIME_SECS_IDX, BUS_TYPE_IDX, ROUTE_NUM_IDX, TARGET_BUS_LINE


def fetch_arrival_datetimes(stop_id: int) -> List[datetime]:
    """
    Fetch upcoming arrival times (as datetime objects) for a given bus stop (stop_id).

    Args:
        stop_id (int): The numeric ID of the stop (e.g. ZOO_STOP_ID or TOOMPARK_STOP_ID).

    Returns:
        List[datetime]: A sorted list of datetime objects representing each bus’s
                        arrival time later than the current moment. If any HTTP or
                        parsing error occurs, returns an empty list.
    """
    try:
        url = API_ENDPOINT_TEMPLATE.format(stop_id=stop_id)
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except requests.RequestException:
        # Network error, timeout, or non‐2xx HTTP status
        return []

    now = datetime.now()
    midnight_today = datetime.combine(now.date(), dt_time.min)
    future_arrivals: List[datetime] = []

    for line in resp.text.strip().splitlines():
        fields = line.split(",")
        # Guard: ensure enough fields
        if len(fields) <= TIME_SECS_IDX:
            continue

        # Must be a 'bus'
        if fields[BUS_TYPE_IDX] != "bus":
            continue

        # Must match the target bus line (e.g. '8')
        if fields[ROUTE_NUM_IDX] != TARGET_BUS_LINE:
            continue

        # Parse the “seconds since midnight” field
        try:
            secs = int(fields[TIME_SECS_IDX])
        except ValueError:
            continue

        arrival_dt = midnight_today + timedelta(seconds=secs)
        # Only keep future times (strictly greater than now)
        if arrival_dt > now:
            future_arrivals.append(arrival_dt)

    return sorted(future_arrivals)
