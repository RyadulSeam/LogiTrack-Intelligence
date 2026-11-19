"""
LogiTrack Intelligence — FastAPI Application Entrypoint
Phase 10: API & Application Layer
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from logitrack.api.routes import health, kpis, hubs, fleet, ml_inference, forecasting

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("logitrack.api")

app = FastAPI(
    title="LogiTrack Intelligence API",
    version="1.0.0",
    description="""
    ## Enterprise Supply Chain & Fleet Telematics REST API
    LogiTrack Intelligence API provides real-time access to:
    - **Executive Control Tower KPIs**: SLA On-Time Delivery rates, delay rates, fulfilled orders, fleet utilization.
    - **Regional Hub Operations**: Capacity utilization, throughput rankings, and bottleneck alerts across 6 Texas hubs.
    - **Fleet Telematics**: GPS tracking, engine diagnostics, fuel telemetry, and asset status across 45 vehicles.
    - **Machine Learning Inference**: Real-time delay risk scoring (XGBoost) and transit ETA prediction.
    - **Time-Series Forecasting**: 7-day and 30-day order demand, hub workload, and fleet vehicle requirements with 95% Confidence Intervals.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration for local dashboard and web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(health.router)
app.include_router(kpis.router)
app.include_router(hubs.router)
app.include_router(fleet.router)
app.include_router(ml_inference.router)
app.include_router(forecasting.router)


@app.get("/", include_in_schema=False)
def root_redirect():
    """Redirect root path to interactive Swagger documentation."""
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("logitrack.api.main:app", host="0.0.0.0", port=8000, reload=True)
