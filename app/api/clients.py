"""
API routes for client requirements.

POST /api/clients      — Submit a new client requirement
GET  /api/clients      — List all client requirements
GET  /api/clients/{id} — Get a single client requirement by BIGINT id
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.models.client import ClientCreate, ClientResponse
from app.services.database import (
    create_client_record,
    get_clients,
    get_client_by_id,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/clients", tags=["Clients"])


@router.post("", response_model=ClientResponse, status_code=201)
def submit_client(client: ClientCreate, background_tasks: BackgroundTasks):
    """
    Submit a new client requirement.

    Validates all fields via Pydantic, then inserts into public.clients.
    Returns the created record including its auto-generated BIGINT id.
    """
    data = client.model_dump()
    logger.info("Creating client requirement for: %s", data.get("client_name"))
    record = create_client_record(data)
    logger.info("Client requirement created with id=%s", record.get("id"))
    
    # Trigger matching pipeline asynchronously
    from app.services.matching import match_client
    background_tasks.add_task(match_client, record["id"])
    
    return record


@router.get("", response_model=list[ClientResponse])
def read_clients(profile_id: Optional[int] = None):
    """Fetch all clients (optionally filtered by profile_id)."""
    return get_clients(profile_id)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int):
    """Return a single client requirement by its BIGINT id."""
    record = get_client_by_id(client_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Client requirement {client_id} not found.")
    return record


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client: ClientCreate, background_tasks: BackgroundTasks):
    from app.services.database import supabase
    data = client.model_dump()
    data["embedding"] = None
    
    res = supabase.table("clients").update(data).eq("id", client_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Client requirement not found.")
        
    supabase.table("matches").delete().eq("client_id", client_id).execute()
    
    from app.services.matching import match_client
    background_tasks.add_task(match_client, client_id)
    
    return res.data[0]
