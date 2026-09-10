"""
NidhiTrace - FastAPI entrypoint
Wires up routes for works, anomalies, and dashboard endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import works, anomalies

app = FastAPI(title="NidhiTrace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mplad-insight.vercel.app", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(works.router, prefix="/api/works", tags=["works"])
app.include_router(anomalies.router, prefix="/api/anomalies", tags=["anomalies"])

@app.get("/health")
def health():
    return {"status": "ok"}
