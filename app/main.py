"""
FastAPI application entry point.

Architecture:
  frontend (HTML/CSS/JS)
      ↓  fetch("/api/...")
  FastAPI (this file)
      ↓
  app/services/database.py
      ↓
  Supabase PostgreSQL (clients, suppliers, matches, notifications)

Routing order is important:
  1. CORS middleware
  2. API routers  ← registered BEFORE static file mount
  3. Named HTML page routes
  4. Static file mount (catches everything else)
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api import clients, suppliers, matches, notifications, auth, matching

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)-8s]  %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Validate configuration on startup (fail fast)
# ---------------------------------------------------------------------------
settings.validate()

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Client–Supplier Matchmaking Platform",
    description=(
        "Connects clients with suitable suppliers using AI-powered semantic matching. "
        "Built for the Wisdom Group AI Intern evaluation."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ---------------------------------------------------------------------------
# CORS (permissive for development)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# API Routers  — must be registered BEFORE static file mount
# ---------------------------------------------------------------------------
app.include_router(clients.router)
app.include_router(suppliers.router)
app.include_router(matches.router)
app.include_router(notifications.router)
app.include_router(auth.router)
app.include_router(matching.router)

# ---------------------------------------------------------------------------
# HTML page routes (clean URLs without .html extension)
# ---------------------------------------------------------------------------
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/auth", include_in_schema=False)
def read_auth():
    return FileResponse(FRONTEND_DIR / "auth.html")


@app.get("/client", include_in_schema=False)
def client_page():
    return FileResponse(FRONTEND_DIR / "client.html")


@app.get("/supplier", include_in_schema=False)
def supplier_page():
    return FileResponse(FRONTEND_DIR / "supplier.html")


@app.get("/admin/dashboard", include_in_schema=False)
def admin_dashboard_page():
    return FileResponse(FRONTEND_DIR / "admin_dashboard.html")

@app.get("/client/dashboard", include_in_schema=False)
def client_dashboard_page():
    return FileResponse(FRONTEND_DIR / "client_dashboard.html")

@app.get("/client/matches", include_in_schema=False)
def client_matches_page():
    return FileResponse(FRONTEND_DIR / "client_matches.html")

@app.get("/supplier/dashboard", include_in_schema=False)
def supplier_dashboard_page():
    return FileResponse(FRONTEND_DIR / "supplier_dashboard.html")

@app.get("/supplier/matches", include_in_schema=False)
def supplier_matches_page():
    return FileResponse(FRONTEND_DIR / "supplier_matches.html")


# ---------------------------------------------------------------------------
# Static file mount — serves CSS, JS, images
# Must come LAST so it does not shadow API or HTML routes
# ---------------------------------------------------------------------------
app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend",
)

