from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.weather import router as weather_router
from backend.app.api.risk import router as risk_router

app = FastAPI(
    title="HydroGuard AI",
    description="Real-Time Urban Flood Intelligence & Response Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk_router)
app.include_router(weather_router)

@app.get("/")
def root():
    return {
        "system": "HydroGuard AI",
        "status": "operational",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "hydroguard-api",
    }