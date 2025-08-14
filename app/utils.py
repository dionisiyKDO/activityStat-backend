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
        logging.info(f"App title mapping already exists at {title_map_path}.")
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
    app_title_map = {
        "chrome.exe": "Google Chrome",
        "Discord.exe": "Discord",
        "StarRail.exe": "Honkai: Star Rail",
        "GenshinImpact.exe": "Genshin Impact",
        "League of Legends.exe": "League of Legends",
        "Telegram.exe": "Telegram",
        "dnplayer.exe": "LDPlayer",
        "Spotify.exe": "Spotify",
        "Code.exe": "Visual Studio Code",
        "explorer.exe": "File Explorer",
        "bg3_dx11.exe": "Baldur's Gate 3",
        "WINWORD.EXE": "Microsoft Word",
        "Obsidian.exe": "Obsidian",
        "reverse1999.exe": "Reverse 1999",
        "FortniteClient-Win64-Shipping.exe": "Fortnite",
        "Client-Win64-Shipping.exe": "Wuthering Waves",
        "nikke.exe": "Goddess of Victory: Nikke",
        "ZenlessZoneZero.exe": "Zenless Zone Zero",
        "LeagueClientUx.exe": "League Client",
        "Overwatch.exe": "Overwatch",
        "Risk of Rain 2.exe": "Risk of Rain 2",
        "steamwebhelper.exe": "Steam Web Helper",
        "Gunfire Reborn.exe": "Gunfire Reborn",
        "Hades2.exe": "Hades 2",
        "msedge.exe": "Microsoft Edge",
        "ShellExperienceHost.exe": "Windows Shell Experience",
        "vlc.exe": "VLC Media Player",
        "r5apex.exe": "Apex Legends",
        "VALORANT-Win64-Shipping.exe": "Valorant",
        "EXCEL.EXE": "Microsoft Excel",
        "DevilMayCry5.exe": "Devil May Cry 5",
        "Risk of Rain Returns.exe": "Risk of Rain Returns",
        "dotnet.exe": ".NET Core",
        "AniLibrix.exe": "AniLibrix",
        "sai2.exe": "PaintTool SAI 2",
        "acad.exe": "AutoCAD",
        "Zoom.exe": "Zoom",
        "OuterWilds.exe": "Outer Wilds",
        "ui32.exe": "Wallpaper Engine",
        "Heretics Fork.exe": "Heretic's Fork",
        "zen.exe": "Zen Browser",
        "METAPHOR.exe": "Metaphor Refantazio",
        "X6Game-Win64-Shipping.exe": "Infinity Nikki",
        "factorio.exe": "Factorio",
        "P3R.exe": "P3Reload",
        "NineSols.exe": "Nine Sols",
        "GF2_Exilium.exe": "GF2 Exilium",
        "SndVol.exe": "Sound Volume Control",
        "ItTakesTwo.exe": "It Takes Two",
        "VirtualBoxVM.exe": "VirtualBox VM",
        "thunderbird.exe": "Mozilla Thunderbird",
        "ApplicationFrameHost.exe": "Application Frame Host",
        "xtop.exe": "PTC Creo",
    }

    app_title_list = [
        {"app": app, "title": title} for app, title in app_title_map.items()
    ]

    try:
        with open(title_map_path, "w") as json_file:
            json.dump(app_title_list, json_file, indent=4)
        logging.info("App title mapping saved to %s", title_map_path)
    except IOError as e:
        logging.error("Failed to save app title mapping to %s: %s", title_map_path, e)



def __get_df(path=data_path) -> pd.DataFrame:
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
                df = __extract_window_events(df)
                df_result = pd.concat([df_result, df], ignore_index=True)
        logging.info(f"Successfully loaded {len(df_result)} events from {path}")
        return df_result
    except ValueError as e:
        logging.error(f"Invalid JSON format in files from {path}: {e}")
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Unexpected error while loading data from {path}: {e}")
        return pd.DataFrame()

def __extract_window_events(df_og: pd.DataFrame) -> pd.DataFrame:
    """Extracts specific fields ('timestamp', 'duration', 'app', 'title') from event data."""
    regex_pattern = r"aw-watcher-window_[A-Za-z0-9-]+"
    parse_buckets_id = [ind for ind in df_og.index if re.match(regex_pattern, ind)]
    logging.info(f"Found {len(parse_buckets_id)} buckets matching the pattern '{regex_pattern}'")
    
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
                logging.warning(f"Unknown OS for hostname: {hostname}")
                logging.warning(f"Using hostname value as OS name for bucket {bucket_id}")
                platform = hostname
        except (IndexError, TypeError) as e:
            logging.warning(f"Hostname not found or invalid in bucket {bucket_id}: {e}")
            logging.warning(f"Using 'Unknown' as OS name for bucket {bucket_id}")
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



def __save_cache(data: pd.DataFrame, cache_file_path: str):
    """Saves data to a specified cache file."""
    full_path = os.path.join(cache_path, cache_file_path)
    try:
        os.makedirs( os.path.dirname(full_path), exist_ok=True )  # Ensure the directory exists
        logging.info(f"Saving cache to {full_path}")
        with open(full_path, "w") as f:
            if isinstance(data, pd.DataFrame):
                json.dump(data.to_json(orient="records"), f)
            else:
                json.dump(data, f)
        logging.info(f"Cache successfully saved to {full_path}")
    except IOError as e:
        logging.error(f"Failed to save cache to {full_path}: {e}")

def __load_cache(cache_file_path: str):
    # TODO: check empty file
    full_path = os.path.join(cache_path, cache_file_path)
    try:
        logging.info(f"Loading cache from {full_path}")
        
        # Metadata is simple dictionary
        
        if cache_file_path.startswith("dataset_metadata"):
            with open(full_path, "r") as f:
                cache = json.load(f)
       
        # everything else is a dataframe
        else:
            with open(full_path, "r") as f:
                cache = pd.read_json(json.loads(f.read()))
        
        logging.info(f"Cache successfully loaded from {full_path}")
        return cache
    except ValueError as e:
        logging.error(f"Invalid cache file format at {full_path}: {e}")
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Failed to load cache from {full_path}: {e}")
        return pd.DataFrame()

def __is_cache_valid(cache_file_path: str):
    full_path = os.path.join(cache_path, cache_file_path)
    try:
        if not os.path.exists(full_path):
            logging.warning(f"Cache file does not exist: {full_path}")
            return False
        
        if os.path.getsize(full_path) == 0:
            logging.warning(f"Cache file is empty: {full_path}")
            return False

        source_mtime = max(os.path.getmtime(os.path.join(data_path, file)) for file in os.listdir(data_path))
        cache_mtime = os.path.getmtime(full_path)
        
        if cache_mtime > source_mtime:
            logging.info(f"Cache is up-to-date for {full_path}")
            return True
        
        logging.info(f"Cache {full_path} is outdated")
        return 
    except OSError as e:
        logging.error(f"Error checking cache validity: {e}")
        return False


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

def get_events():
    with sqlite3.connect(database_path) as conn:
        return pd.read_sql("SELECT * FROM events", conn)

# 5.8sec
def insert_events(df): 
    with sqlite3.connect(database_path) as conn:
        conn.executemany("""
            INSERT OR IGNORE INTO events (timestamp, duration, app, title, platform)
            VALUES (?, ?, ?, ?, ?)
        """, df[["timestamp", "duration", "app", "title", "platform"]].to_records(index=False))
        conn.commit()

# 26sec
# def insert_events(df): 
#     with sqlite3.connect(database_path) as conn:
#         for _, row in df.iterrows():
#             conn.execute("""
#                 INSERT OR IGNORE INTO events (timestamp, duration, app, title, platform)
#                 VALUES (?, ?, ?, ?, ?)
#             """, (row["timestamp"], row["duration"], row["app"], row["title"], row["platform"]))
#         conn.commit()
#endregion


def get_app_list():
    """Loads the app title mapping from the JSON file."""
    try:
        logging.info(f"Loading app title map from {title_map_path}")
        with open(title_map_path, "r") as json_file:
            app_title_map = json.load(json_file)
        logging.info("App title map successfully loaded.")
        return app_title_map
    except IOError as e:
        logging.error(f"Failed to load app title map: {e}")
        return {}

def get_spent_time():
    """Calculates and caches spent time data."""
    # TODO: different result with different hyperparameters, take this into account when saving cache
    # cache_file_path = "spent_time.json"
    # if __is_cache_valid(cache_file_path):
    #     return __load_cache(cache_file_path).to_json(orient="records")
    
    logging.info("Calculating spent time.")
    result = spent_time()
    logging.info("Spent time calculation completed.")
    
    # __save_cache(data=result, cache_file_path=cache_file_path)
    return result.to_json(orient="records")

def get_daily_app_usage(app_name: str = "chrome.exe"):
    """Calculates the time spent on each application each day"""

    # file_path = os.path.join("daily_app_usage", f"daily_app_usage_{app_name}.json")
    # if __is_cache_valid(file_path):
    #     return __load_cache(file_path).to_json(orient="records")
    
    # df = __get_df()
    # logging.info(df.head())
    logging.info("Calculating daily app usage for %s.", app_name)
    result = daily_app_usage(app_name)
    logging.info("Daily app usage calculation completed for %s.", app_name)
    
    # __save_cache(data=result, cache_file_path=file_path)
    return result

def get_dataset_metadata():
    """Fetch metadata about the dataset, such as the date range."""
    # cache_file_path = "dataset_metadata.json"
    # if __is_cache_valid(cache_file_path):
    #     return __load_cache(cache_file_path)
    
    df = __get_df()
    start_date: str = df['timestamp'].min()
    end_date: str = df['timestamp'].max()

    # start_date = pd.to_datetime(start_date, format='ISO8601')
    # end_date = pd.to_datetime(end_date, format='ISO8601')

    metadata = {
        # string to date
        "start_date": start_date,
        "end_date": end_date,
        "total_records": len(df),
    }

    logging.info("Fetched dataset metadata: %s", metadata)
    # __save_cache(data=metadata, cache_file_path=cache_file_path)
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
    print(query)
    params.append(min_duration * 3600)

    with sqlite3.connect(database_path) as conn:
        df_events = pd.read_sql_query(query, conn, params=params)

    df_events['duration'] = df_events['duration'] / 3600.0  # seconds to hours

    with open(title_map_path, 'r') as json_file:
        app_title_list = json.load(json_file)
    app_title_map = {item['app']: item['title'] for item in app_title_list}

    df_events['title'] = df_events['app'].map(app_title_map)

    return df_events




if __name__ == "__main__":
    ...
