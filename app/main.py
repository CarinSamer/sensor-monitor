import os
import secrets
from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.database import Base, ReadingRow, SessionLocal, engine

Base.metadata.create_all(engine)

app = FastAPI(title="Sensor Monitor")


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
        return Reading.model_validate(row)


@app.get("/readings", response_model=list[Reading])
def list_readings(limit: int = 50):
    with SessionLocal() as session:
        query = select(ReadingRow).order_by(ReadingRow.id.desc()).limit(limit)
        rows = session.scalars(query).all()
        return [Reading.model_validate(r) for r in reversed(rows)]