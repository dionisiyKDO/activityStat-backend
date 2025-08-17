# ActivityStat Backend

FastAPI server for processing and serving [ActivityWatch](https://activitywatch.net/) exported data for the [ActivityStat Frontend](https://github.com/dionisiyKDO/activityStat-frontend).

Built with:

- **FastAPI**: For serving a lightweight and well-documented REST API.
- **SQLite**: For compact, local storage and fast queries.
- **Pandas / NumPy**: For parsing and preprocessing of ActivityWatcher exports.

## Features

- Import and parse ActivityWatcher JSON exports in SQLite database
- REST API endpoints for activity statistics
- Data aggregation and processing

## Setup

1. Clone this repository:

```bash
git clone https://github.com/dionisiyKDO/activitystat-backend
cd activitystat-backend
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy exported ActivityWatch data to the `data/export` directory.

- To get your data, while AW is running, go to `http://localhost:5600/#/buckets` and press "Export all buckets as JSON."
- The exported file will be named `aw-buckets-export.json`.
- You can use multiple export files, but they must all start with `aw-buckets-export` to be detected.

```bash
mkdir data/export
cp /path/to/activitywatch/export/*.json data/export
```

5. Run the server:

```bash
cd ./app
uvicorn main:app --reload
```

## API Endpoints

### `GET /app_list`

List of application titles with associated executables/classes.  
**Example:**

```json
{
  "Google Chrome": ["chrome.exe", "chrome"],
  "Slack": ["slack.exe", "Slack"]
}
```

### `GET /spent_time`

Total time spent per application.  
**Example:**

```json
[
  {"title": "Google Chrome", "duration": 1200.5, "app": "chrome.exe"},
  {"title": "Slack", "duration": 845.2, "app": "slack.exe"}
]
```

### `GET /daily_app_usage/{app_name}`

Daily usage timeline for a given application.  
**Example:**

```json
[
  {"date": "2024-08-23", "duration": 2.4},
  {"date": "2024-08-24", "duration": 5.1}
]
```

### `GET /dataset_metadata`

Metadata about the imported dataset.  
**Example:**

```json
{
  "start_date": "2023-01-01T00:00:00Z",
  "end_date": "2023-12-31T23:59:59Z",
  "total_records": 100000
}
```

## Requirements

- Python 3.8+
- ActivityWatch data export

## Related

- [ActivityStat Frontend](https://github.com/dionisiyKDO/activityStat-frontend) — interactive dashboard built with Svelte 5 + D3.js
