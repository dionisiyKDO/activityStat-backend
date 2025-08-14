import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils import get_app_list, get_spent_time, get_daily_app_usage, get_dataset_metadata, create_app_title_mapping, init_db

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
    return JSONResponse(content=get_app_list())

@app.get("/spent_time")
def spent_time():
    return JSONResponse(content=get_spent_time())

@app.get("/daily_app_usage/{app_name}")
def daily_app_usage(app_name: str):
    return get_daily_app_usage(app_name)

@app.get("/dataset_metadata")
def dataset_metadata():
    """API endpoint to fetch metadata about the dataset."""
    return get_dataset_metadata()


if __name__ == "__main__":
    init_db()
    create_app_title_mapping()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)