"""
Monte Carlo wrapper around Simulator.simulate_step(...) to estimate P(late).

Given a `Simulator` instance, a departure time, and a list of matched trips,
run MC_ITERATIONS trials.  Count how many produce `lateness > 0`.  Return
fraction ∈ [0.0, 1.0].
"""

from datetime import datetime
from typing import List, Tuple

from simulator import Simulator
from config import MONTE_CARLO_ITERATIONS


def compute_lateness_probability(sim: Simulator,
                                 departure: datetime,
                                 trips: List[Tuple[datetime, datetime]],
                                 mc_iterations: int = MONTE_CARLO_ITERATIONS) -> float:
    """
    Args:
        sim (Simulator):      A Simulator instance (holds class_start, walk times, etc.).
        departure (datetime): The departure time from home.
        trips (List[(datetime, datetime)]):
                              A list of (sched_dep, sched_arr) pairs, already matched by matcher.
        mc_iterations (int):  How many Monte Carlo samples to draw.

    Returns:
        float: The fraction of simulated trials where `lateness > 0` (i.e. Rita is late),
               clipped to [0.0, 1.0].
    """
    late_count = 0
    for _ in range(mc_iterations):
        sample = sim.simulate_step(departure, trips)
        if sample["lateness"] > 0:
            late_count += 1
    return late_count / mc_iterations
