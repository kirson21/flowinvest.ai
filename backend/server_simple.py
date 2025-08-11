from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Flow Invest API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Flow Invest API - Minimal Mode",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/api/")
async def api_root():
    return {"message": "Flow Invest API", "status": "healthy"}

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "mode": "minimal"
    }

@app.get("/api/status") 
async def status():
    return {"status": "ok", "environment": os.getenv("ENVIRONMENT", "production")}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("server_simple:app", host="0.0.0.0", port=port)