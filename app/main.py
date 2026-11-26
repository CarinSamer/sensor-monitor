import os
import secrets
import time
from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException
from prometheus_client import Counter, Gauge
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.database import Base, ReadingRow, SessionLocal, engine

Base.metadata.create_all(engine)

app = FastAPI(title="Sensor Monitor")
Instrumentator().instrument(app).expose(app, include_in_schema=False)

READINGS_TOTAL = Counter(
    "sensor_readings_total", "Readings accepted by the API", ["sensor_id"]
)
LAST_TEMPERATURE = Gauge(
    "sensor_temperature_celsius", "Latest temperature per sensor", ["sensor_id"]
)
LAST_READING_TIME = Gauge(
    "sensor_last_reading_timestamp_seconds",
    "Unix time of the latest reading per sensor",
    ["sensor_id"],
)


def check_key(x_api_key: str = Header(default="")):
    expected = os.environ.get("API_KEY", "dev-key")
    if not secrets.compare_digest(x_api_key.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Invalid API key")


class ReadingIn(BaseModel):
    sensor_id: str = Field(min_length=1)
    temperature: float = Field(ge=-50, le=200)


class Reading(ReadingIn):
    model_config = ConfigDict(from_attributes=True)
    timestamp: datetime


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"commit": os.environ.get("GIT_SHA", "dev")}


@app.post(
    "/readings",
    response_model=Reading,
    status_code=201,
    dependencies=[Depends(check_key)],
)
def add_reading(reading: ReadingIn):
    with SessionLocal() as session:
        row = ReadingRow(**reading.model_dump())
        session.add(row)
        session.commit()
        session.refresh(row)
        READINGS_TOTAL.labels(sensor_id=reading.sensor_id).inc()
        LAST_TEMPERATURE.labels(sensor_id=reading.sensor_id).set(reading.temperature)
        LAST_READING_TIME.labels(sensor_id=reading.sensor_id).set(time.time())
        return Reading.model_validate(row)


@app.get("/readings", response_model=list[Reading])
def list_readings(limit: int = 50):
    with SessionLocal() as session:
        query = select(ReadingRow).order_by(ReadingRow.id.desc()).limit(limit)
        rows = session.scalars(query).all()
        return [Reading.model_validate(r) for r in reversed(rows)]