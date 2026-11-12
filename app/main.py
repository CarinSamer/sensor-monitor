from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Sensor Monitor")


class ReadingIn(BaseModel):
    sensor_id: str = Field(min_length=1)
    temperature: float = Field(ge=-50, le=200)


class Reading(ReadingIn):
    timestamp: datetime


readings: list[Reading] = []  # in-memory storage; replaced by PostgreSQL in Week 3


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/readings", response_model=Reading, status_code=201)
def add_reading(reading: ReadingIn):
    stored = Reading(**reading.model_dump(), timestamp=datetime.now(timezone.utc))
    readings.append(stored)
    return stored


@app.get("/readings")
def list_readings(limit: int = 50):
    return readings[-limit:]
