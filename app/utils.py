import pandas as pd
import numpy as np
import re
import os
import json
from modules.spent_time import spent_time
from modules.daily_app_usage import daily_app_usage

import warnings
import logging
import colorlog


warnings.simplefilter(action="ignore", category=FutureWarning)
pd.options.mode.chained_assignment = None
pd.options.display.precision = 2


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




data_path = os.path.join("app", "data", "export")
cache_path = os.path.join("app", "data", "cache")

title_map_path = os.path.join("app", "data", "app_title_map.json")

def create_app_title_mapping() -> dict:
    """Generates and saves a mapping of app executable names to user-friendly titles."""
    if os.path.exists(title_map_path):
        logging.info(f"App title mapping already exists at {title_map_path}.")
        return
    
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

    regex_pattern = r"aw-watcher-window_DESKTOP-[A-Za-z0-9]+"
    parse_buckets_id = [ind for ind in df_og.index if re.match(regex_pattern, ind)]

    timestamp_arr, duration_arr, app_arr, title_arr = [], [], [], []

    for bucket_id in parse_buckets_id:
        df_data = df_og["buckets"].get(bucket_id, {})  # i think it's safer to use get() because it will return an empty dict if the key is not found
        df_data.pop("data", None)  # remove 'data' key with empty dict (for some fucking reason it is here), so it wouldnt cause an error - "ValueError: Mixing dicts with non-Series may lead to ambiguous ordering."
        df_bucket = pd.DataFrame(df_data)

        for ind in df_bucket.index:
            event = df_bucket["events"][ind]
            try:
                timestamp_arr.append(event["timestamp"])
                duration_arr.append(event["duration"])
                app_arr.append(event["data"]["app"])
                title_arr.append(event["data"]["title"])
            except KeyError as e:
                logging.warning(f"Missing key in event data: {e}")

    return pd.DataFrame(
        {
            "timestamp": timestamp_arr,
            "duration": duration_arr,
            "app": app_arr,
            "title": title_arr,
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
    cache_file_path = "spent_time.json"
    if __is_cache_valid(cache_file_path):
        return __load_cache(cache_file_path).to_json(orient="records")
    
    df = __get_df()
    logging.info("Calculating spent time.")
    result = spent_time(df)
    logging.info("Spent time calculation completed.")
    
    __save_cache(data=result, cache_file_path=cache_file_path)
    return result.to_json(orient="records")

def get_daily_app_usage(app_name: str = "chrome.exe"):
    """Calculates the time spent on each application each day"""

    file_path = os.path.join("daily_app_usage", f"daily_app_usage_{app_name}.json")
    if __is_cache_valid(file_path):
        return __load_cache(file_path).to_json(orient="records")
    
    df = __get_df()
    logging.info(df.head())
    logging.info("Calculating daily app usage for %s.", app_name)
    result = daily_app_usage(df, app_name)
    logging.info("Daily app usage calculation completed for %s.", app_name)
    
    __save_cache(data=result, cache_file_path=file_path)
    return result.to_json(orient="records")

def get_dataset_metadata():
    """Fetch metadata about the dataset, such as the date range."""
    cache_file_path = "dataset_metadata.json"
    if __is_cache_valid(cache_file_path):
        return __load_cache(cache_file_path)
    
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
    __save_cache(data=metadata, cache_file_path=cache_file_path)
    return metadata

if __name__ == "__main__":
    ...
