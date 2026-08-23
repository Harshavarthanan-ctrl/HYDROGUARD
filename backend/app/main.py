from fastapi import FastAPI

app = FastAPI(
    title="HydroGuard AI",
    description="Real-Time Urban Flood Intelligence & Response Platform",
    version="0.1.0",
)


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