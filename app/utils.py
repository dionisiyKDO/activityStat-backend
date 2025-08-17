# app/utils.py
import pandas as pd
import re
import os
import json
import sqlite3

import warnings
import logging
import colorlog

from config import (data_path, database_path, flatten_apps_to_title_map, flatten_title_to_apps_map)

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

#region Title map helpers

def _get_app_map() -> dict:
    """Generates and saves a mapping of app executable names to user-friendly titles."""
    app_title_map = {
        "Windows": {
            "Browsers": {
                "chrome.exe": "Google Chrome",
                "msedge.exe": "Microsoft Edge",
                "zen.exe": "Zen Browser"
            },
            "Chat & Communication": {
                "Discord.exe": "Discord",
                "Telegram.exe": "Telegram",
                "thunderbird.exe": "Mozilla Thunderbird",
                "Zoom.exe": "Zoom"
            },
            "Games": {
                "StarRail.exe": "Honkai: Star Rail",
                "GenshinImpact.exe": "Genshin Impact",
                "BlueArchive.exe": "Blue Archive",
                "reverse1999.exe": "Reverse 1999",
                "League of Legends.exe": "League of Legends",
                "LeagueClientUx.exe": "League Client",
                "FortniteClient-Win64-Shipping.exe": "Fortnite",
                "Client-Win64-Shipping.exe": "Wuthering Waves",
                "nikke.exe": "Goddess of Victory: Nikke",
                "ZenlessZoneZero.exe": "Zenless Zone Zero",
                "Overwatch.exe": "Overwatch",
                "Risk of Rain 2.exe": "Risk of Rain 2",
                "Gunfire Reborn.exe": "Gunfire Reborn",
                "Hades2.exe": "Hades 2",
                "VALORANT-Win64-Shipping.exe": "Valorant",
                "DevilMayCry5.exe": "Devil May Cry 5",
                "Risk of Rain Returns.exe": "Risk of Rain Returns",
                "ItTakesTwo.exe": "It Takes Two",
                "bg3_dx11.exe": "Baldur's Gate 3",
                "X6Game-Win64-Shipping.exe": "Infinity Nikki",
                "P3R.exe": "P3Reload",
                "NineSols.exe": "Nine Sols",
                "GF2_Exilium.exe": "GF2 Exilium",
                "METAPHOR.exe": "Metaphor Refantazio",
                "Heretics Fork.exe": "Heretic's Fork",
                "BrownDust II.exe": "BrownDust II",
                "r5apex_dx12.exe": "Apex Legends",
                "SoTGame.exe": "Sea of Thieves",
                "Balatro.exe": "Balatro",
                "AWayOut.exe": "A Way Out",
                "TETR.IO.exe": "TETR.IO",
                "Terraria.exe": "Terraria",
                "Rungore.exe": "Rungore",
                "OuterWilds.exe": "Outer Wilds",
                "dnplayer.exe": "LDPlayer",
                "factorio.exe": "Factorio",
                "SplitFiction.exe": "Split Fiction",
                "Replicube.exe": "Replicube",
                "MiSideFull.exe": "MiSide",
                "FragPunk.exe": "FragPunk",
                "20SM.exe": "20 Small Mazes",
                "HYP.exe": "HoyoPlay Launcher",
                "launcher_main.exe": "Wuthering Waves Launcher",
            },
            "Editors & IDEs": {
                "Code.exe": "Visual Studio Code",
                "devenv.exe": "Visual Studio",
                "acad.exe": "AutoCAD",
                "sai2.exe": "PaintTool SAI 2",
                "Obsidian.exe": "Obsidian",
                "WINWORD.EXE": "Microsoft Word",
                "EXCEL.EXE": "Microsoft Excel",
                "POWERPNT.EXE": "Microsoft PowerPoint",
                "netbeans64.exe": "NetBeans IDE",
                "MATLAB.exe": "MATLAB",
                "godot.windows.opt.tools.64.exe": "Godot Engine",
                "pgAdmin4.exe": "pgAdmin 4",
                "xtop.exe": "PTC Creo",
            },
            "System & Utilities": {
                "explorer.exe": "File Explorer",
                "ShellExperienceHost.exe": "Windows Shell Experience",
                "ApplicationFrameHost.exe": "Application Frame Host",
                "SndVol.exe": "Sound Volume Control",
                "VirtualBoxVM.exe": "VirtualBox VM",
                "Taskmgr.exe": "Task Manager",
                "dotnet.exe": ".NET Core",
                "NVIDIA app.exe": "NVIDIA App",
                "mintty.exe": "MinTTY Terminal",
                "python.exe": "Python",
                "SnippingTool.exe": "Snipping Tool"
            },
            "Media & Players": {
                "Spotify.exe": "Spotify",
                "AniLibrix.exe": "AniLibrix",
                "vlc.exe": "VLC Media Player",
                "ui32.exe": "Wallpaper Engine",
                "Photos.exe": "Microsoft Photos",
                "obs64.exe": "OBS Studio"
            },
            "Other": {
                "Flow.Launcher.exe": "Flow Launcher",
                "steamwebhelper.exe": "Steam Web Helper",
            }
        },
        "Linux": {
            "Browsers": {
                "chrome": "Google Chrome",
                "firefox": "Mozilla Firefox",
                "zen": "Zen Browser"
            },
            "Chat & Communication": {
                "discord": "Discord",
                "org.telegram.desktop": "Telegram"
            },
            "Games": {
                "steam": "Steam",
                "steam_app_3557620": "Blue Archive",
                "steam_app_2357570": "Overwatch",
                "factorio": "Factorio",
            },
            "Editors & IDEs": {
                "code": "Visual Studio Code",
                "code-oss": "Visual Studio Code",
                "obsidian": "Obsidian",
            },
            "System & Utilities": {
                "Alacritty": "Alacritty Terminal",
                "org.gnome.Nautilus": "Files (Nautilus)"
            },
            "Media & Players": {
                "vlc": "VLC Media Player",
                "Spotify": "Spotify",
                "mpv": "mpv Media Player",
            }
        }
    }
    
    return app_title_map

def build_flatten_apps_to_title_map():
    """Flatten nested OS -> category -> app map into app -> title."""
    if os.path.exists(flatten_apps_to_title_map):
        logging.info(f"Apps to title mapping already exists at \"{flatten_apps_to_title_map}\".")
        return
    
    flat_map = {}
    for os_section in _get_app_map().values():
        for category in os_section.values():
            flat_map.update(category)
    
    try:
        with open(flatten_apps_to_title_map, "w") as json_file:
            json.dump(flat_map, json_file, indent=4)
        logging.info(f"Apps to title mapping saved to {flatten_apps_to_title_map}", )
    except IOError as e:
        logging.error(f"Failed to save Apps to title mapping to {flatten_apps_to_title_map}: {e}")

def build_flatten_title_to_apps_map() -> dict:
    """Flatten map to title -> app list"""
    if os.path.exists(flatten_title_to_apps_map):
        logging.info(f"Title to apps mapping already exists at \"{flatten_title_to_apps_map}\".")
        return
    
    title_to_apps = {}
    for os_dict in _get_app_map().values():
        for category_dict in os_dict.values():
            for app, title in category_dict.items():
                if title is None:
                    continue
                title_to_apps.setdefault(title, []).append(app)
    
    try:
        with open(flatten_title_to_apps_map, "w") as json_file:
            json.dump(title_to_apps, json_file, indent=4)
        logging.info(f"Title to apps mapping saved to {flatten_title_to_apps_map}", )
    except IOError as e:
        logging.error(f"Failed to save Title to apps mapping to {flatten_title_to_apps_map}: {e}")

#endregion


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

#region Get functions

def get_flatten_apps_to_title_map() -> list[dict[str, str]]:
    """Loads the app title mapping from the JSON file."""    
    try:
        with open(flatten_apps_to_title_map, "r") as json_file:
            app_title_map = json.load(json_file)
        logging.info(f"Successfully loaded Apps to title mapping from {flatten_apps_to_title_map}")
        return app_title_map
    except IOError as e:
        logging.error(f"Failed to load Apps to title mapping: {e}")
        return []

def get_flatten_title_to_apps_map() -> list[dict[str, str]]:
    """Loads the app title mapping from the JSON file."""    
    try:
        with open(flatten_title_to_apps_map, "r") as json_file:
            app_title_map_flatten = json.load(json_file)
        logging.info(f"Successfully loaded Title to apps mapping from {flatten_title_to_apps_map}")
        return app_title_map_flatten
    except IOError as e:
        logging.error(f"Failed to load Title to apps mapping: {e}")
        return []

def get_spent_time() -> pd.DataFrame:
    """Queries the database for total time spent on each application."""
    logging.info("Calculating total time spent.")
    result = spent_time()
    return result

def get_daily_app_usage(app_titles: list[str] = ["Zen Browser", "Google Chrome"]) -> pd.DataFrame:
    """Calculates the time spent on each application each day"""
    logging.info(f"Calculating daily app usage for {app_titles}.")
    result = daily_app_usage(app_titles)
    return result

def get_daily_os_usage() -> pd.DataFrame:
    """Calculates the time spent on each OS each day"""
    logging.info("Calculating daily OS usage.")
    result = daily_os_usage()
    return result

def get_dataset_metadata() -> dict[str, str | int]:
    """Fetch metadata about the dataset, such as the date range."""
    logging.info("Fetching dataset metadata")
    
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
    
    return metadata

#endregion

#region Helper functions

#TODO: I thinking about the need in this functions
# Why not merge them with `get_spent_time()` and `get_daily_app_usage()`?

def daily_app_usage(app_titles: str = ['Zen Browser', 'Google Chrome'], start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    Calculates the daily time spent on a specified application.
    """
    title_map = get_flatten_title_to_apps_map()
    apps_map = get_flatten_apps_to_title_map()
    
    all_execs = []
    for app_title in app_titles:
        all_execs += title_map.get(app_title, [app_title])
    
    placeholders = ','.join(['?'] * len(all_execs)) # question marks for query string 
    params = all_execs
    
    where_clauses = [f"app IN ({placeholders})"]
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
            app,
            SUM(duration) AS duration
        FROM events
        {where_sql}
        GROUP BY date, app
        ORDER BY date ASC
    """

    with sqlite3.connect(database_path) as conn:
        df = pd.read_sql_query(query, conn, params=params)

    if df.empty:
        return df
    
    # Map executables back to titles
    df['app'] = df['app'].map(apps_map)
    
    # Aggregate by title+date (sum diff executables)
    df = df.groupby(['date', 'app'], as_index=False)['duration'].sum()

    # Convert duration to hours + round
    df['duration'] = (df['duration'] / 3600.0).round(2)
    df['date'] = pd.to_datetime(df['date'])
    
    # Fill in missing dates using Pandas
    min_date = df['date'].min()
    max_date = df['date'].max()
    full_range = pd.date_range(start=min_date, end=max_date, freq='D')
    
    # Reindex separately per app, then concat back
    df_filled = []
    for app, group in df.groupby('app'):
        g = group.set_index('date').reindex(full_range).fillna(0).reset_index()
        g['app'] = app
        g = g.rename(columns={'index': 'date'})
        df_filled.append(g)

    df_result = pd.concat(df_filled, ignore_index=True)
    return df_result

def daily_os_usage(start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    Calculates the daily time spent on different OS.
    """
    params = []
    where_clauses = []
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
            platform,
            SUM(duration) AS duration
        FROM events
        { where_sql if where_clauses  else '' }
        GROUP BY date, platform
        ORDER BY date ASC
    """

    with sqlite3.connect(database_path) as conn:
        df = pd.read_sql_query(query, conn, params=params)

    if df.empty:
        return df
    
    # Convert duration to hours + round
    df['duration'] = (df['duration'] / 3600.0).round(2)
    df['date'] = pd.to_datetime(df['date'])
    
    # Fill in missing dates using Pandas
    min_date = df['date'].min()
    max_date = df['date'].max()
    full_range = pd.date_range(start=min_date, end=max_date, freq='D')
    
    df_filled = []
    for app, group in df.groupby('platform'):
        g = group.set_index('date').reindex(full_range).fillna(0).reset_index()
        g['platform'] = app
        g = g.rename(columns={'index': 'date'})
        df_filled.append(g)

    df_result = pd.concat(df_filled, ignore_index=True)
    return df_result

def spent_time(start_date: str = None, end_date: str = None, min_duration: float = 10.0) -> pd.DataFrame:
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


    app_title_map = get_flatten_apps_to_title_map()

    df_events['title'] = df_events['app'].map(app_title_map).fillna("Unknown")
    
    # group by title and sum durations
    df_events = df_events.groupby('title', as_index=False).agg({'duration': 'sum', 'app': 'first'})
    df_events = df_events.sort_values(by='duration', ascending=False).reset_index(drop=True)
    
    df_events['duration'] = (df_events['duration'] / 3600.0).round(2) # seconds to hours, round to 2 decimal places

    return df_events

#endregion


if __name__ == "__main__":
    build_flatten_title_to_apps_map()
    build_flatten_apps_to_title_map()
    init_db()
    ...