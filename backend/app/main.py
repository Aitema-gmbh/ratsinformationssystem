"""
aitema|Rats - FastAPI Application

OParl 1.1 kompatibles Ratsinformationssystem
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import os

from app.database import init_db
from app.routers import oparl


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    init_db()
    yield


app = FastAPI(
    title="aitema|Rats",
    description="OParl 1.1 kompatibles Ratsinformationssystem fuer deutsche Kommunen",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(oparl.router)


# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "aitema-rats", "version": "0.1.0"}


# API info
@app.get("/api")
def api_info():
    return {
        "name": "aitema|Rats API",
        "version": "0.1.0",
        "oparl": "/oparl/v1",
        "docs": "/api/docs",
        "health": "/health",
    }
