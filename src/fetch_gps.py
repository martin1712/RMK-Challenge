import os
import pandas as pd
from datetime import datetime
import requests
import io

def read_and_filter_gps(
    url: str = "https://transport.tallinn.ee/gps.txt",
    line_number: int = 8,
    transport_type: int = 2
) -> pd.DataFrame:
    """
    Fetches live GPS data from Tallinn's endpoint, filters for a specific bus line,
    and returns a cleaned DataFrame.

    This simpler approach loads the entire file into memory, which
    is acceptable for moderate file sizes (~MBs).
    """
    cols = [
        'transport_type', 'line', 'lat_micro', 'lon_micro',
        'speed', 'heading', 'vehicle_id', 'vehicle_type',
        'stop_sequence', 'stop_name'
    ]

    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp.raise_for_status()

    text_stream = io.StringIO(resp.text)

    dataframe = pd.read_csv(
        text_stream,
        names=cols,
        header=None,
        usecols=cols,
        dtype=str,
        low_memory=False
    )

    dataframe['transport_type'] = pd.to_numeric(dataframe['transport_type'], errors='coerce')
    dataframe['line'] = pd.to_numeric(dataframe['line'], errors='coerce')

    dataframe = dataframe[(dataframe['transport_type'] == transport_type) & (dataframe['line'] == line_number)].copy()

    dataframe['latitude'] = pd.to_numeric(dataframe['lat_micro'], errors='coerce') / 1e6
    dataframe['longitude'] = pd.to_numeric(dataframe['lon_micro'], errors='coerce') / 1e6
    dataframe.drop(columns=['lat_micro', 'lon_micro'], inplace=True)

    dataframe['snapshot_time'] = datetime.now()

    cols_out = [
        'transport_type', 'line', 'speed', 'heading', 'vehicle_id',
        'vehicle_type', 'stop_sequence', 'stop_name',
        'latitude', 'longitude', 'snapshot_time'
    ]
    return dataframe[cols_out]


if __name__ == '__main__':
    out = 'data/processed/bus8_snapshot.csv'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df = read_and_filter_gps()
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} records for line 8 to {out}")
