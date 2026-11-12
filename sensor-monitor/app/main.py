from fastapi import FastAPI

app = FastAPI(title="Sensor Monitor")


@app.get("/health")
def health():
     return {"status": "ok"}