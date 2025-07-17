from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import route modules
from routes import mc_verification, load_management, call_finalization

# Create FastAPI instance
app = FastAPI(
    title="HappyRobot FDE API",
    description="API for freight dispatch and carrier management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(mc_verification.router, prefix="/api/v1", tags=["MC Verification"])
app.include_router(load_management.router, prefix="/api/v1", tags=["Load Management"])
app.include_router(call_finalization.router, prefix="/api/v1", tags=["Call Management"])

@app.get("/")
async def root():
    return {"message": "HappyRobot FDE API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "HappyRobot FDE API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)