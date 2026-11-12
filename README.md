# Sensor Monitor

A small REST API that receives temperature readings from simulated industrial
sensors (motors and pumps). Built as a DevOps learning project.

## Run the API

```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Interactive docs: http://127.0.0.1:8000/docs

## Run the sensor simulator

In a second terminal (with the venv activated):

```bash
python simulator.py
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /health | Health check |
| POST | /readings | Add a reading: `{"sensor_id": "motor1", "temperature": 72.5}` |
| GET | /readings | List the latest readings (`?limit=50`) |
