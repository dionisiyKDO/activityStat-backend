# ActivityStat Backend

FastAPI server for processing and serving [ActivityWatch](https://activitywatch.net/) data for the [ActivityStat Frontend](https://github.com/dionisiyKDO/activityStat-frontend).

## Features

- ActivityWatch data parsing
- REST API endpoints for activity statistics
- Data aggregation and processing

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
cd ./app
uvicorn main:app --reload
```

## Requirements

- Python 3.8+
- ActivityWatch data export
