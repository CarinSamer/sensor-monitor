import os
import random
import time

import httpx

URL = os.environ.get("API_URL", "http://127.0.0.1:8000/readings")
HEADERS = {"X-API-Key": os.environ.get("API_KEY", "dev-key")}
SENSORS = {"motor1": 70.0, "motor2": 65.0, "pump1": 55.0}  # base temperatures in °C

while True:
    for sensor_id, base in SENSORS.items():
        payload = {
            "sensor_id": sensor_id,
            "temperature": round(base + random.uniform(-3, 3), 2),
        }
        try:
            r = httpx.post(URL, json=payload, headers=HEADERS, timeout=5)
            print(f"{sensor_id}: {payload['temperature']} °C -> {r.status_code}")
        except httpx.HTTPError as e:
            print(f"Could not reach API: {e}")
    time.sleep(1)