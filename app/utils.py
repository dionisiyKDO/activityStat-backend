import pandas as pd
import numpy as np
import re
import os
import json
import sqlite3

import warnings
import logging
import colorlog

warnings.simplefilter(action="ignore", category=FutureWarning)
pd.options.mode.chained_assignment = None
pd.options.display.precision = 2

#region Logging configuration

# Define a custom logging format
log_format = (
    "%(log_color)s%(levelname)s%(reset)s: %(asctime)s.%(msecs)03d - %(message)s%(reset)s"
)

# Configure colorlog to add colors to different levels
color_formatter = colorlog.ColoredFormatter(
    log_format,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create a handler for the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(color_formatter)

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler],
)

#endregion


data_path = os.path.join("app", "data", "export")
cache_path = os.path.join("app", "data", "cache")

title_map_path = os.path.join("app", "data", "app_title_map.json")

database_name = "data.db"
database_path = os.path.join("app", "data", database_name)

def create_app_title_mapping() -> dict:
    """Generates and saves a mapping of app executable names to user-friendly titles."""
    if os.path.exists(title_map_path):
        logging.info(f"App title mapping already exists at \"{title_map_path}\".")
        return
    
    # parse this too
    # {'app': 'steam_app_3557620', 'duration': 86.2310852778, 'title': None}
    # {'app': 'vlc', 'duration': 86.1167513889, 'title': None}
    # {'app': 'BrownDust II.exe', 'duration': 43.53955, 'title': None}
    # {'app': 'code-oss', 'duration': 31.9545716667, 'title': None}
    # {'app': 'r5apex_dx12.exe', 'duration': 28.6704352778, 'title': None}
    # {'app': 'factorio', 'duration': 25.8147738889, 'title': None}
    # {'app': 'discord', 'duration': 24.6170216667, 'title': None}
    # {'app': 'code', 'duration': 20.9713025, 'title': None}
    # {'app': 'org.telegram.desktop', 'duration': 19.4591188889, 'title': None}
    # {'app': 'obsidian', 'duration': 15.2051855556, 'title': None}
    # {'app': 'Flow.Launcher.exe', 'duration': 14.9335838889, 'title': None}
    # {'app': 'devenv.exe', 'duration': 14.5573625, 'title': None}
    # {'app': 'SplitFiction.exe', 'duration': 13.2099805556, 'title': None}
    # {'app': 'Alacritty', 'duration': 12.0729144444, 'title': None}
    # {'app': 'Spotify', 'duration': 11.0964413889, 'title': None}
    
    # TODO: auto-generate this from the data
    app_title_map = [
        {'app': 'chrome.exe', 'title': 'Google Chrome'},
        {'app': 'Discord.exe', 'title': 'Discord'},
        {'app': 'StarRail.exe', 'title': 'Honkai: Star Rail'},
        {'app': 'GenshinImpact.exe', 'title': 'Genshin Impact'},
        {'app': 'League of Legends.exe', 'title': 'League of Legends'},
        {'app': 'Telegram.exe', 'title': 'Telegram'},
        {'app': 'dnplayer.exe', 'title': 'LDPlayer'},
        {'app': 'Spotify.exe', 'title': 'Spotify'},
        {'app': 'Code.exe', 'title': 'Visual Studio Code'},
        {'app': 'explorer.exe', 'title': 'File Explorer'},
        {'app': 'bg3_dx11.exe', 'title': "Baldur's Gate 3"},
        {'app': 'WINWORD.EXE', 'title': 'Microsoft Word'},
        {'app': 'Obsidian.exe', 'title': 'Obsidian'},
        {'app': 'reverse1999.exe', 'title': 'Reverse 1999'},
        {'app': 'FortniteClient-Win64-Shipping.exe', 'title': 'Fortnite'},
        {'app': 'Client-Win64-Shipping.exe', 'title': 'Wuthering Waves'},
        {'app': 'nikke.exe', 'title': 'Goddess of Victory: Nikke'},
        {'app': 'ZenlessZoneZero.exe', 'title': 'Zenless Zone Zero'},
        {'app': 'LeagueClientUx.exe', 'title': 'League Client'},
        {'app': 'Overwatch.exe', 'title': 'Overwatch'},
        {'app': 'Risk of Rain 2.exe', 'title': 'Risk of Rain 2'},
        {'app': 'steamwebhelper.exe', 'title': 'Steam Web Helper'},
        {'app': 'Gunfire Reborn.exe', 'title': 'Gunfire Reborn'},
        {'app': 'Hades2.exe', 'title': 'Hades 2'},
        {'app': 'msedge.exe', 'title': 'Microsoft Edge'},
        {'app': 'ShellExperienceHost.exe', 'title': 'Windows Shell Experience'},
        {'app': 'vlc.exe', 'title': 'VLC Media Player'},
        {'app': 'r5apex.exe', 'title': 'Apex Legends'},
        {'app': 'VALORANT-Win64-Shipping.exe', 'title': 'Valorant'},
        {'app': 'EXCEL.EXE', 'title': 'Microsoft Excel'},
        {'app': 'DevilMayCry5.exe', 'title': 'Devil May Cry 5'},
        {'app': 'Risk of Rain Returns.exe', 'title': 'Risk of Rain Returns'},
        {'app': 'dotnet.exe', 'title': '.NET Core'},
        {'app': 'AniLibrix.exe', 'title': 'AniLibrix'},
        {'app': 'sai2.exe', 'title': 'PaintTool SAI 2'},
        {'app': 'acad.exe', 'title': 'AutoCAD'},
        {'app': 'Zoom.exe', 'title': 'Zoom'},
        {'app': 'OuterWilds.exe', 'title': 'Outer Wilds'},
        {'app': 'ui32.exe', 'title': 'Wallpaper Engine'},
        {'app': 'Heretics Fork.exe', 'title': "Heretic's Fork"},
        {'app': 'zen.exe', 'title': 'Zen Browser'},
        {'app': 'METAPHOR.exe', 'title': 'Metaphor Refantazio'},
        {'app': 'X6Game-Win64-Shipping.exe', 'title': 'Infinity Nikki'},
        {'app': 'factorio.exe', 'title': 'Factorio'},
        {'app': 'P3R.exe', 'title': 'P3Reload'},
        {'app': 'NineSols.exe', 'title': 'Nine Sols'},
        {'app': 'GF2_Exilium.exe', 'title': 'GF2 Exilium'},
        {'app': 'SndVol.exe', 'title': 'Sound Volume Control'},
        {'app': 'ItTakesTwo.exe', 'title': 'It Takes Two'},
        {'app': 'VirtualBoxVM.exe', 'title': 'VirtualBox VM'},
        {'app': 'thunderbird.exe', 'title': 'Mozilla Thunderbird'},
        {'app': 'ApplicationFrameHost.exe', 'title': 'Application Frame Host'},
        {'app': 'xtop.exe', 'title': 'PTC Creo'}
    ]

    try:
        with open(title_map_path, "w") as json_file:
            json.dump(app_title_map, json_file, indent=4)
        logging.info(f"App title mapping saved to {title_map_path}", )
    except IOError as e:
        logging.error(f"Failed to save app title mapping to {title_map_path}: {e}")



def _get_df(path: str = data_path) -> pd.DataFrame:
    """
    Reads all JSON files in the data_path and extracts window events.
    Files must start with "aw-buckets-export"
    """
    try:
        df_result = pd.DataFrame()
        files = os.listdir(path)
        logging.info(f"Found {len(files)} files in {path}")
        
        for file in files:
            if file.startswith("aw-buckets-export"):
                logging.info(f"Processing file: {file}")
                file_path = os.path.join(path, file)
                df = pd.read_json(file_path)
                df = _extract_window_events(df)
                df_result = pd.concat([df_result, df], ignore_index=True)
        logging.info(f"Successfully loaded {len(df_result)} events from {path}")
        return df_result
    except ValueError as e:
        logging.error(f"Invalid JSON format in files from {path}: {e}")
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Unexpected error while loading data from {path}: {e}")
        return pd.DataFrame()

def _extract_window_events(df_og: pd.DataFrame) -> pd.DataFrame:
    """Extracts specific fields ('timestamp', 'duration', 'app', 'title', 'platform') from event data."""
    regex_pattern = r"aw-watcher-window_[A-Za-z0-9-]+"
    parse_buckets_id = [ind for ind in df_og.index if re.match(regex_pattern, ind)]
    
    timestamp_arr, duration_arr, app_arr, title_arr, platform_arr = [], [], [], [], []

    #region
    # Example of df_bucket structure:
    # {"aw-watcher-window_DESKTOP-9NAUUF0": {
    #       "id": "aw-watcher-window_DESKTOP-9NAUUF0", 
    #       "created": "2024-12-22T09:01:05.443462+00:00", 
    #       "name": null, 
    #       "type": "currentwindow", 
    #       "client": "aw-watcher-window", 
    #       "hostname": "DESKTOP-9NAUUF0", 
    #       "data": {just empty dict for wharever reason, so we remove it},  
    #       "events": [ events are here, they are a list of dictionaries with 'timestamp', 'duration', 'data' keys ]
    # }}

    # Example of event structure:
    # "events": [   {"timestamp": "2025-01-12T14:26:07.798000+00:00", "duration": 0.0, "data": {"app": "zen.exe", "title": "Zen Browser"}}, 
    #               {"timestamp": "2025-01-12T14:26:05.760000+00:00", "duration": 1.018, "data": {"app": "explorer.exe", "title": ""}},     ]
    #endregion
    
    for bucket_id in parse_buckets_id:
        df_data = df_og["buckets"].get(bucket_id, {})  # i think it's safer to use get() because it will return an empty dict if the key is not found
        df_data.pop("data", None)  # remove 'data' key with empty dict (for some fucking reason it is here), so it wouldnt cause an error - "ValueError: Mixing dicts with non-Series may lead to ambiguous ordering."
        df_bucket = pd.DataFrame(df_data)
        
        try:
            hostname = df_bucket.get("hostname", [None])[0]  # Get hostname, if it exists
            hostname = hostname.lower()
            if hostname.startswith("desktop-") or hostname.startswith("laptop-") or hostname.startswith("wndws"):
                platform = "Windows"
            elif hostname in ["linux", "ubuntu", "arch", "endeavouros", "cachyos"]:
                platform = "Linux"
            elif hostname in ["macos", "mac", "macbook", "macbook pro", "macbook air", "osx"]:
                platform = "macOS"
            else:
                logging.warning(f"Unknown OS for bucket \"{bucket_id}\", Using hostname value \"{hostname}\", as an OS name for ")
                platform = hostname
        except (IndexError, TypeError) as e:
            logging.warning(f"Hostname not found or invalid in bucket {bucket_id}: {e}. Using \"Unknown\" as an OS name")
            platform = 'Unknown'

        for ind in df_bucket.index:
            event = df_bucket["events"][ind]
            
            try:
                timestamp_arr.append(event["timestamp"])
                duration_arr.append(event["duration"])
                app_arr.append(event["data"]["app"])
                title_arr.append(event["data"]["title"])
                platform_arr.append(platform)
            except KeyError as e:
                logging.warning(f"Missing key in event data: {e}")

    return pd.DataFrame(
        {
            "timestamp": timestamp_arr,
            "duration": duration_arr,
            "app": app_arr,
            "title": title_arr,
            "platform": platform_arr,
        }
    )


#region Database functions

def init_db():
    with sqlite3.connect(database_path) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            timestamp TEXT,
            duration REAL,
            app TEXT,
            title TEXT,
            platform TEXT,
            PRIMARY KEY (timestamp, app, title)
        )
        """)
    
    # Check if the database is empty then it was just created, so insert data
    with sqlite3.connect(database_path) as conn:
        curr = conn.cursor()
        curr.execute("SELECT EXISTS(SELECT 1 FROM events)")
        if curr.fetchone()[0] == 0:
            logging.info("New database created, inserting exported data...")
            insert_events(_get_df(data_path))

def insert_events(df): 
    with sqlite3.connect(database_path) as conn:
        conn.executemany("""
            INSERT OR IGNORE INTO events (timestamp, duration, app, title, platform)
            VALUES (?, ?, ?, ?, ?)
        """, df[["timestamp", "duration", "app", "title", "platform"]].to_records(index=False))
        conn.commit()

def get_events():
    with sqlite3.connect(database_path) as conn:
        return pd.read_sql("SELECT * FROM events", conn)

#endregion


def get_app_list() -> list[dict[str, str]]:
    """Loads the app title mapping from the JSON file."""
    try:
        with open(title_map_path, "r") as json_file:
            app_title_map = json.load(json_file)
        logging.info(f"Successfully loaded App title map from {title_map_path}")
        return app_title_map
    except IOError as e:
        logging.error(f"Failed to load app title map: {e}")
        return []

def get_spent_time() -> pd.DataFrame:
    """Queries the database for total time spent on each application."""
    logging.info("Calculating total time spent.")
    result = spent_time()
    return result

def get_daily_app_usage(app_name: str = "chrome.exe") -> pd.DataFrame:
    """Calculates the time spent on each application each day"""

    logging.info("Calculating daily app usage for %s.", app_name)
    result = daily_app_usage(app_name)
    logging.info("Daily app usage calculation completed for %s.", app_name)
    
    return result

def get_dataset_metadata() -> dict[str, str | int]:
    """Fetch metadata about the dataset, such as the date range."""
    query = """
    SELECT 
        MIN(timestamp) AS start_date, 
        MAX(timestamp) AS end_date, 
        COUNT(timestamp) AS total_records 
    FROM events
    """
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
    
    if row:
        metadata = {
            "start_date": row[0],
            "end_date": row[1],
            "total_records": row[2]  # SQLite returns count as int
        }
    else:
        metadata = {
            "start_date": None,
            "end_date": None,
            "total_records": 0
        }
    
    logging.info("Fetched dataset metadata: %s", metadata)
    return metadata




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

def spent_time(start_date=None, end_date=None, min_duration=10.0) -> pd.DataFrame:
    """Calculates the total time spent on each application"""
    where_clauses = []
    params = []

    if start_date:
        where_clauses.append("timestamp >= ?")
        params.append(start_date)
    if end_date:
        where_clauses.append("timestamp <= ?")
        params.append(end_date)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    query = f"""
        SELECT app, SUM(duration) AS duration
        FROM events
        {where_sql}
        GROUP BY app
        HAVING SUM(duration) >= ?
        ORDER BY duration DESC
    """
    params.append(min_duration * 3600)

    with sqlite3.connect(database_path) as conn:
        df_events = pd.read_sql_query(query, conn, params=params)

    df_events['duration'] = df_events['duration'] / 3600.0  # seconds to hours
    df_events['duration'] = df_events['duration'].round(2)  # round to 2 decimal places

    with open(title_map_path, 'r') as json_file:
        app_title_list = json.load(json_file)
    app_title_map = {item['app']: item['title'] for item in app_title_list}

    df_events['title'] = df_events['app'].map(app_title_map)

    return df_events




if __name__ == "__main__":
    ...
