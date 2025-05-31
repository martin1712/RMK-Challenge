# Rita’s Lateness Simulator

Estimate the chance that **Rita** is late to her 9:05 AM meeting.  
She walks to bus stop **Zoo**, takes **bus #8** to **Toompark**, and walks to the office.  
This tool simulates that journey using real Tallinn bus data + randomness.

---

## What It Does

- Fetches **live bus #8 schedules** (Zoo → Toompark)
- Simulates 100k+ random journeys per departure time
- Outputs a **plot of P(late)** vs. time Rita leaves home

---

## How It Works 

1. **`config.py`** — sets base walk/bus times, jitter, iterations, start/end times  
2. **`fetcher.py`** — pulls live arrivals from Tallinn’s SIRI API  
3. **`matcher.py`** — matches Zoo departures with Toompark arrivals  
4. **`simulator.py`** — simulates one journey with jitter  
5. **`montecarlo.py`** — runs 100k simulations to estimate lateness  
6. **`main.py`** — loops over leave-times, logs results, plots PNG

---

## Output

Creates a graph:  
**"Probability Rita is late" vs. "Time she leaves home"**  
Stored in `results/lateness_curve_YYYYMMDD_HHMMSS.png`

---

## How to Run

```bash
# 1. Clone & setup
cd rita-lateness-simulator -> python3 -m venv .venv, source .venv/bin/activate
cd src -> pip install -r requirements.txt

# 2. Edit config.py 

open config.py and change configurations.

# 3. Run 

example:
python main.py --start 08:00 --meeting 09:05 --step 30
