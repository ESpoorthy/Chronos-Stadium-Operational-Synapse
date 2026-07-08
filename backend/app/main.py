from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai

app = FastAPI(
    title="Chronos Stadium AI",
    description="The world's first Generative Future Engine for Mega Events.",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Chronos Stadium AI Backend is running."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(ai.router)

