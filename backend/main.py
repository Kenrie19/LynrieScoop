from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import asyncio
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.api.routes import admin, auth, bookings, cinemas, movies, reserve, showings, users
from app.core.config import settings
from app.core.mqtt_client import setup_mqtt_for_app
from app.db.init_db import init_db

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

# Set up MQTT client
setup_mqtt_for_app(app)


# Add startup event to initialize database
@app.on_event("startup")
async def startup_db_client():
    await init_db()


# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(movies.router, prefix="/movies", tags=["movies"])
app.include_router(showings.router, prefix="/showings", tags=["showings"])
app.include_router(reserve.router, prefix="", tags=["reserve"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(cinemas.router, prefix="/cinemas", tags=["cinemas"])
# app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Project Cinema API"}


# Add a custom handler for the OpenAPI schema to include JWT auth
@app.get("/api-schema", include_in_schema=False)
def get_open_api_schema():
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=[{"url": "/"}],
    )
