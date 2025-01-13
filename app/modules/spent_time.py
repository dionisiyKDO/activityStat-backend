import pandas as pd
import json

def spent_time(df_og: pd.DataFrame, start_date: str = None, end_date: str = None, min_duration: float = 10.0) -> pd.DataFrame:
    '''Calculates the total time spent on each application'''    
    # Convert 'timestamp' to datetime
    df_og['timestamp'] = pd.to_datetime(df_og['timestamp'], format='ISO8601')

    # Filter by start_date and end_date if provided
    if start_date:
        df_og = df_og[df_og['timestamp'] >= pd.to_datetime(start_date)]
    if end_date:
        df_og = df_og[df_og['timestamp'] <= pd.to_datetime(end_date)]
    
    if df_og.empty:
        return pd.DataFrame(columns=['app', 'duration'])

    # Group by 'app' and sum the 'duration'
    df_events = df_og.groupby(['app'], as_index=False).agg({'duration': 'sum'})

    df_events['duration'] = df_events['duration'] / 3600.0 # seconds to hours

    # Sort the results by 'duration' in descending order
    df_events.sort_values('duration', ascending=False, inplace=True)

    # Filter out apps with less than 10 hours of usage
    if min_duration:
        df_events = df_events[df_events['duration'] >= min_duration]

    # Sort again after possible aggregation
    df_events.sort_values('duration', ascending=False, inplace=True)

    # read app_title_map.json, listy of dictionaries
    with open('./app/data/app_title_map.json', 'r') as json_file:
        app_title_list = json.load(json_file)

    # convert from list of dictionaries to single dictionary
    app_title_map = {item['app']: item['title'] for item in app_title_list}

    # map app names to titles
    df_events['title'] = df_events['app'].map(app_title_map)

    return df_events