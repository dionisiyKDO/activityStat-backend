import pandas as pd
import sqlite3
import os

# def daily_app_usage(df_events: pd.DataFrame, app_name: str = 'chrome.exe'):
#     """Calculates the time spent on a specified application each day."""
#     # TODO: Add support for multiple apps (save cache for one app, multiple without cache)
    
#     # Check if the app_name is present in the DataFrame
#     if app_name not in df_events['app'].unique():
#         raise ValueError(f"The app_name '{app_name}' is not present in the DataFrame.")
    
#     # Ensure the necessary columns are present
#     required_columns = {'timestamp', 'app', 'duration'}
#     if not required_columns.issubset(df_events.columns):
#         raise ValueError(f"Input DataFrame must contain the following columns: {required_columns}")
    
#     # Convert 'timestamp' to datetime and extract date part
#     df_events['timestamp'] = pd.to_datetime(df_events['timestamp'], format='ISO8601').dt.date
    
#     # Generate date range covering all the dates in the DataFrame
#     date_range = pd.date_range(start=df_events['timestamp'].min(), end=df_events['timestamp'].max())
#     df_dates = pd.DataFrame(date_range, columns=['timestamp'])
#     df_dates['timestamp'] = df_dates['timestamp'].dt.date
#     df_dates['app'] = app_name
    
#     # Filter for the specific app
#     df_events = df_events[df_events['app'] == app_name]
    
#     # Group by 'timestamp' and 'app' and sum the 'duration'
#     df_time_sum = df_events.groupby(['timestamp', 'app'], as_index=False).agg({'duration': 'sum'})
    
#     # Convert duration from seconds to hours
#     df_time_sum['duration'] = df_time_sum['duration'] / 3600.0 # seconds to hours
    
#     # Merge with the date range DataFrame
#     df_time_sum = df_dates.merge(df_time_sum, on=['timestamp', 'app'], how='left')
    
#     # Fill missing values in 'duration' with 0
#     df_time_sum['duration'].fillna(0, inplace=True)
    
#     return df_time_sum

title_map_path = os.path.join("app", "data", "app_title_map.json")

database_name = "data.db"
database_path = os.path.join("app", "data", database_name)

def daily_app_usage(app_name: str = 'chrome.exe', start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    Calculates the daily time spent on a specified application using a direct SQL query.
    """
    where_clauses = ["app = ?"]
    params = [app_name]

    if start_date:
        where_clauses.append("timestamp >= ?")
        params.append(start_date)
    if end_date:
        where_clauses.append("timestamp <= ?")
        params.append(end_date)

    where_sql = f"WHERE {' AND '.join(where_clauses)}"

    query = f"""
        SELECT
            strftime('%Y-%m-%d', timestamp) AS date,
            SUM(duration) AS duration
        FROM events
        {where_sql}
        GROUP BY date
        ORDER BY date ASC
    """
    print(query)

    with sqlite3.connect(database_path) as conn:
        df_daily_usage = pd.read_sql_query(query, conn, params=params)

    # Convert duration from seconds to hours
    df_daily_usage['duration'] = df_daily_usage['duration'] / 3600.0

    # Fill in missing dates using Pandas
    if not df_daily_usage.empty:
        df_daily_usage['date'] = pd.to_datetime(df_daily_usage['date'])
        
        # Create a complete date range
        min_date = df_daily_usage['date'].min()
        max_date = df_daily_usage['date'].max()
        full_date_range = pd.date_range(start=min_date, end=max_date, freq='D')
        
        # Reindex the DataFrame to fill in missing dates
        df_daily_usage = df_daily_usage.set_index('date').reindex(full_date_range).fillna(0).reset_index()
        df_daily_usage = df_daily_usage.rename(columns={'index': 'date'})

    return df_daily_usage
