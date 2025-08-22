from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import summrizing

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(summrizing.router)
