from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.routes import (
    admin_router,
    auth_router,
    bookings_router,
    movies_router,
    showings_router,
    users_router,
)
from app.core.config import settings
from app.db.init_db import init_db

from app.api.routes.websocket_route import router as websocket_router


app = FastAPI(
    title="Cinema API",
    description="API for a cinema booking system with real-time ticket updates",
    version="1.0.0",
    docs_url="/api-docs",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.ENVIRONMENT != "development":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )


# Add startup event to initialize database
@app.on_event("startup")
async def startup_db_client() -> None:
    await init_db()


# Include API routers
app.include_router(websocket_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(movies_router, prefix="/movies", tags=["movies"])
app.include_router(showings_router, prefix="/showings", tags=["showings"])
app.include_router(bookings_router, prefix="/bookings", tags=["bookings"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "Project Cinema API"}


# Add a custom handler for the OpenAPI schema to include JWT auth
@app.get("/api-schema", include_in_schema=False)
def get_open_api_schema() -> Dict:
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=[{"url": "/"}],
    )
