from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from .auth.router import router as auth_router
from .routers.chat import router as chat_router
from .routers.admin import router as admin_router
from .routers.community import router as community_router

# Load environment variables from root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(
    title="Baby Policy Chatbot API",
    description="Backend for the Baby Policy Chatbot",
    version="1.0.0",
)

# CORS Middleware
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(community_router, prefix="/api/community", tags=["Community"])


@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Welcome to the Baby Policy Chatbot API"}
