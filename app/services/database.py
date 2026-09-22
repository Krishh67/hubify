"""
Database service — all Supabase interactions live here.

Tables used:
  public.clients        — client requirements
  public.suppliers      — supplier offerings
  public.matches        — AI-generated matches (read-only in Phase 1)
  public.notifications  — notifications (read-only in Phase 1)

The Supabase client is initialized once at module load.
All functions are synchronous (supabase-py v2 sync client).
Errors are caught and re-raised as FastAPI HTTPExceptions so raw
database errors never reach the client.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import HTTPException
from supabase import Client, create_client

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Client initialization
# ---------------------------------------------------------------------------

def _init_supabase() -> Client:
    try:
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except Exception as exc:
        logger.critical("Failed to initialize Supabase client: %s", exc)
        raise RuntimeError(f"Supabase initialization error: {exc}") from exc


supabase: Client = _init_supabase()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _handle_db_error(operation: str, exc: Exception) -> None:
    """Log and convert any database exception into an HTTP 500."""
    logger.error("Database error during '%s': %s", operation, exc)
    raise HTTPException(
        status_code=500,
        detail=f"A database error occurred. Please try again later.",
    )

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

def create_client_record(data: dict) -> dict:
    """Insert a new row into public.clients and return the created record."""
    try:
        if "certifications" in data:
            val = data["certifications"]
            if val is None:
                data["certifications"] = []
            elif isinstance(val, str):
                data["certifications"] = [c.strip() for c in val.split(",") if c.strip()]
        response = supabase.table("clients").insert(data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=500, detail="Insert succeeded but returned no data.")
    except HTTPException:
        raise
    except Exception as exc:
        _handle_db_error("create_client_record", exc)


def get_clients(profile_id: Optional[int] = None) -> list[dict]:
    """Return client rows, optionally filtered by profile_id, newest first."""
    try:
        query = supabase.table("clients").select("*").order("created_at", desc=True)
        if profile_id:
            query = query.eq("profile_id", profile_id)
        response = query.execute()
        data = response.data or []
        for d in data:
            d["has_embedding"] = d.get("embedding") is not None
        return data
    except Exception as exc:
        _handle_db_error("get_clients", exc)


def get_client_by_id(client_id: int) -> Optional[dict]:
    """Return a single client row by BIGINT id, or None if not found."""
    try:
        response = (
            supabase.table("clients")
            .select("*")
            .eq("id", client_id)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as exc:
        _handle_db_error("get_client_by_id", exc)

# ---------------------------------------------------------------------------
# Suppliers
# ---------------------------------------------------------------------------

def create_supplier_record(data: dict) -> dict:
    """Insert a new row into public.suppliers and return the created record."""
    try:
        if "certifications" in data:
            val = data["certifications"]
            if val is None:
                data["certifications"] = []
            elif isinstance(val, str):
                data["certifications"] = [c.strip() for c in val.split(",") if c.strip()]
        response = supabase.table("suppliers").insert(data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=500, detail="Insert succeeded but returned no data.")
    except HTTPException:
        raise
    except Exception as exc:
        _handle_db_error("create_supplier_record", exc)


def get_suppliers(profile_id: Optional[int] = None) -> list[dict]:
    """Return supplier rows, optionally filtered by profile_id, newest first."""
    try:
        query = supabase.table("suppliers").select("*").order("created_at", desc=True)
        if profile_id:
            query = query.eq("profile_id", profile_id)
        response = query.execute()
        data = response.data or []
        for d in data:
            d["has_embedding"] = d.get("embedding") is not None
        return data
    except Exception as exc:
        _handle_db_error("get_suppliers", exc)


def get_supplier_by_id(supplier_id: int) -> Optional[dict]:
    """Return a single supplier row by BIGINT id, or None if not found."""
    try:
        response = (
            supabase.table("suppliers")
            .select("*")
            .eq("id", supplier_id)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as exc:
        _handle_db_error("get_supplier_by_id", exc)

# ---------------------------------------------------------------------------
# Matches  (read-only in Phase 1)
# ---------------------------------------------------------------------------

def get_matches(client_id: Optional[int] = None, supplier_id: Optional[int] = None) -> list[dict]:
    """Return all match rows with optional filters and join supplier/client details."""
    try:
        query = supabase.table("matches").select("*, suppliers(*, profiles(*)), clients(*, profiles(*))").order("rank")
        if client_id:
            query = query.eq("client_id", client_id)
        if supplier_id:
            query = query.eq("supplier_id", supplier_id)
            
        response = query.execute()
        return response.data or []
    except Exception as exc:
        _handle_db_error("get_matches", exc)

# ---------------------------------------------------------------------------
# Notifications  (read-only in Phase 1)
# ---------------------------------------------------------------------------

def get_notifications(user_id: Optional[int] = None) -> list[dict]:
    """Return notifications for a user (profile_id) by finding their clients.id and suppliers.id."""
    try:
        query = supabase.table("notifications").select("*").order("created_at", desc=True)
        if user_id:
            # Resolve profile_id to clients.id and suppliers.id
            c_res = supabase.table("clients").select("id").eq("profile_id", user_id).execute()
            s_res = supabase.table("suppliers").select("id").eq("profile_id", user_id).execute()
            
            c_ids = [str(r["id"]) for r in (c_res.data or [])]
            s_ids = [str(r["id"]) for r in (s_res.data or [])]
            
            # If the user has no clients or suppliers, they have no notifications
            if not c_ids and not s_ids:
                return []
                
            # Filter notifications where client_id IN (...) OR supplier_id IN (...)
            filters = []
            if c_ids:
                filters.append(f"client_id.in.({','.join(c_ids)})")
            if s_ids:
                filters.append(f"supplier_id.in.({','.join(s_ids)})")
                
            or_filter = ",".join(filters)
            query = query.or_(or_filter)
            
        response = query.execute()
        return response.data or []
    except Exception as exc:
        _handle_db_error("get_notifications", exc)


# ---------------------------------------------------------------------------
# Profiles (Demo Auth)
# ---------------------------------------------------------------------------

def get_profile_by_email(email: str) -> Optional[dict]:
    try:
        response = supabase.table("profiles").select("*").eq("email", email).execute()
        return response.data[0] if response.data else None
    except Exception as exc:
        _handle_db_error("get_profile_by_email", exc)

def create_profile(data: dict) -> dict:
    try:
        response = supabase.table("profiles").insert(data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=500, detail="Profile creation failed.")
    except Exception as exc:
        _handle_db_error("create_profile", exc)

