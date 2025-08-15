from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

# Super minimal FastAPI app - guaranteed to work
app = FastAPI(title="f01i.ai API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "f01i.ai API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/api/")
def api_root():
    return {
        "message": "f01i.ai API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "production")
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("server_minimal:app", host="0.0.0.0", port=port)