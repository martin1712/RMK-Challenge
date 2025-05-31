import pandas as pd
import requests
import io
from datetime import datetime


def read_and_filter_gps(url: str = "https://transport.tallinn.ee/gps.txt",
                        line_number: int = 8,
                        transport_type: int = 2) -> pd.DataFrame:
    # 1) Download the feed
    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp.raise_for_status()
    text_stream = io.StringIO(resp.text)

    # 2) Column names in the order the feed provides them
    cols = [
        'transport_type', 'line', 'lat_micro', 'lon_micro',
        'speed', 'heading', 'vehicle_id', 'vehicle_type',
        'stop_sequence', 'stop_name'
    ]

    # 3) Read everything in as strings, then filter
    dataframe = pd.read_csv(
        text_stream,
        names=cols,
        header=None,
        usecols=cols,
        dtype=str,
        low_memory=False
    )

    # 4) Keep only bus-type=2 and the desired line
    dataframe['transport_type'] = pd.to_numeric(dataframe['transport_type'], errors='coerce')
    dataframe['line'] = pd.to_numeric(dataframe['line'], errors='coerce')
    df = dataframe[
        (dataframe['transport_type'] == transport_type) &
        (dataframe['line'] == line_number)
    ].copy()

    # 5) **Swap** lat_micro ↔ lon_micro (the feed’s columns are flipped)
    df[['lat_micro', 'lon_micro']] = df[['lon_micro', 'lat_micro']]

    # 6) Convert micro-degrees to decimal degrees
    df['latitude'] = pd.to_numeric(df['lat_micro'], errors='coerce') / 1e6
    df['longitude'] = pd.to_numeric(df['lon_micro'], errors='coerce') / 1e6
    df.drop(columns=['lat_micro', 'lon_micro'], inplace=True)

    # 7) Filter and return columns
    df['snapshot_time'] = datetime.now()
    cols_out = [
        'transport_type', 'line', 'speed', 'heading', 'vehicle_id',
        'vehicle_type', 'stop_sequence', 'stop_name',
        'latitude', 'longitude', 'snapshot_time'
    ]
    return df[cols_out]
