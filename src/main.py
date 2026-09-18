"""
OmniVision-DocIntel API — Main Application Entrypoint.
Production-grade FastAPI microservice featuring OpenAPI documentation,
Prometheus telemetry metrics, and CORS middleware.
"""

import time
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .api.v1.router import api_router
from .schemas.doc_schema import HealthResponse

# Optional Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, make_asgi_app
    PROMETHEUS_AVAILABLE = True
    REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
    REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["endpoint"])
except ImportError:
    PROMETHEUS_AVAILABLE = False


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time * 1000:.2f}ms"
    return response


# Include Core V1 Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount Prometheus metrics if available
if PROMETHEUS_AVAILABLE:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.get(
    f"{settings.API_V1_STR}/health",
    response_model=HealthResponse,
    tags=["System Health & Diagnostics"],
    summary="Healthcheck & Runtime Status",
)
async def health_check():
    return HealthResponse(
        status="HEALTHY",
        version=settings.VERSION,
        service=settings.PROJECT_NAME,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "OmniVision-DocIntel API is running",
        "docs_url": "/docs",
        "healthcheck": f"{settings.API_V1_STR}/health",
        "author": "Anuj (AI Automation & Python Specialist)",
    }
