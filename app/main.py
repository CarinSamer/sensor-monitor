from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.database import Base, ReadingRow, SessionLocal, engine

Base.metadata.create_all(engine)

app = FastAPI(title="Sensor Monitor")


class ReadingIn(BaseModel):
    sensor_id: str = Field(min_length=1)
    temperature: float = Field(ge=-50, le=200)


class Reading(ReadingIn):
    model_config = ConfigDict(from_attributes=True)
    timestamp: datetime


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/readings", response_model=Reading, status_code=201)
def add_reading(reading: ReadingIn):
    with SessionLocal() as session:
        row = ReadingRow(**reading.model_dump())
        session.add(row)
        session.commit()
        session.refresh(row)
        return Reading.model_validate(row)


@app.get("/readings", response_model=list[Reading])
def list_readings(limit: int = 50):
    with SessionLocal() as session:
        query = select(ReadingRow).order_by(ReadingRow.id.desc()).limit(limit)
        rows = session.scalars(query).all()
        return [Reading.model_validate(r) for r in reversed(rows)]