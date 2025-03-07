from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Import API endpoints
from api.endpoints import router as api_router

# Initialize FastAPI app
app = FastAPI(
    title="Web QA Analyzer API",
    description="Analyzes web pages for quality issues using CrewAI and LLMs",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Web QA Analyzer API is running",
        "docs": "/docs",
        "version": app.version
    }

if __name__ == "__main__":
    # Make sure OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set")
        print("Set it with: export OPENAI_API_KEY='your-api-key'")
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000)