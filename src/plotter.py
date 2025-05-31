"""
Draw and save lateness‐probability curve,
with:
  - major ticks auto‐chosen (e.g. every 30 minutes or 1 hour),
  - minor ticks at every single minute,
  - grid lines for both major/minor ticks,
  - automatic rotation of X‐labels,
  - fixed Y‐range [0.0 − y_padding, 1.0 + y_padding].
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np


@dataclass(frozen=True)
class PlotConfig:
    style: str = "ggplot"
    figsize: Tuple[int, int] = (12, 6)
    dpi: int = 150
    y_padding: float = 0.05
    x_padding_days: float = 1e-4


def plot_curve(departure_datetimes: List[datetime],
               lateness_probabilities: List[float],
               filename: str = "lateness_curve.png",
               config: PlotConfig = PlotConfig()) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot Rita’s raw lateness‐probability curve.
    Adds minor ticks for every single minute along X.

    Args:
        departure_datetimes (List[datetime]): A list of departure times (sorted).
        lateness_probabilities (List[float]): A matching list of P(late) values ∈ [0,1].
        filename (str): The path where the PNG will be saved.
        config (PlotConfig): Plot settings.

    Returns:
        (fig, ax): The Matplotlib Figure and Axes.
    """
    # 1) Apply style if available
    try:
        plt.style.use(config.style)
    except OSError:
        pass

    # 2) Convert P(late) to a numpy array (dtype float)
    y_raw = np.array(lateness_probabilities, dtype=float)
    x_nums = mdates.date2num(departure_datetimes)

    # 3) Create a single figure/axes
    fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
    ax.plot(x_nums, y_raw, '-o', lw=2, color='steelblue', label='P(late)')

    # 4) Major ticks: AutoDateLocator chooses hour/min intervals
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # 5) Minor ticks: force tick at every single minute
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=1))

    # 6) X‐limits padded slightly
    ax.set_xlim(
        x_nums[0] - config.x_padding_days,
        x_nums[-1] + config.x_padding_days
    )

    # 7) Y‐axis: [−padding, 1+padding], with MajorLocator every 0.1
    ax.set_ylim(-config.y_padding, 1.0 + config.y_padding)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))

    # 8) Labels, title, legend
    ax.set_xlabel("Time Leaving Home")
    ax.set_ylabel("Probability of Being Late")
    ax.set_title("Rita’s Meeting Punctuality")
    ax.grid(which='major', linestyle='--', alpha=0.6)
    ax.grid(which='minor', linestyle=':', alpha=0.3)
    ax.legend(loc='upper left')

    # 9) Rotate X‐labels if needed
    fig.autofmt_xdate()
    plt.tight_layout()

    # 10) Save to file and close
    fig.savefig(filename, dpi=config.dpi)
    plt.close(fig)

    return fig, ax
