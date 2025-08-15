# app/config.py
import os

data_path = os.path.join("app", "data", "export")

flatten_apps_to_title_map = os.path.join("app", "data", "flatten_apps_to_title_map.json")
flatten_title_to_apps_map = os.path.join("app", "data", "flatten_title_to_apps_map.json")

database_name = "data.db"
database_path = os.path.join("app", "data", database_name)