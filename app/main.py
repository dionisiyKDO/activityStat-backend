# app/main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils import (
    get_spent_time,
    get_daily_app_usage,
    get_dataset_metadata,
    get_flatten_apps_to_title_map,
    get_flatten_title_to_apps_map,
    build_flatten_title_to_apps_map,
    build_flatten_apps_to_title_map,
    init_db,
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/app_list")
def app_list():
    return get_flatten_title_to_apps_map()


# TODO: Spent tim get's app executable, only one, windows's
@app.get("/spent_time")
def spent_time():
    return get_spent_time().to_dict(orient="records")


@app.get("/daily_app_usage/{app_name}")
def daily_app_usage(app_name: str):
    return get_daily_app_usage(app_name).to_dict(orient="records")


@app.get("/dataset_metadata")
def dataset_metadata():
    return get_dataset_metadata()


if __name__ == "__main__":
    build_flatten_title_to_apps_map()
    build_flatten_apps_to_title_map()
    init_db()

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
