"""
API routes for supplier offerings.

POST /api/suppliers      — Submit a new supplier offering
GET  /api/suppliers      — List all supplier offerings
GET  /api/suppliers/{id} — Get a single supplier offering by BIGINT id
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.models.supplier import SupplierCreate, SupplierResponse
from app.services.database import (
    create_supplier_record,
    get_suppliers,
    get_supplier_by_id,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])


@router.post("", response_model=SupplierResponse, status_code=201)
def submit_supplier(supplier: SupplierCreate):
    """
    Submit a new supplier offering.

    Validates all fields via Pydantic, then inserts into public.suppliers.
    Returns the created record including its auto-generated BIGINT id.
    """
    data = supplier.model_dump()
    logger.info("Creating supplier offering for: %s", data.get("supplier_name"))
    record = create_supplier_record(data)
    logger.info("Supplier offering created with id=%s", record.get("id"))
    return record


@router.get("", response_model=list[SupplierResponse])
def read_suppliers(profile_id: Optional[int] = None):
    """Fetch all suppliers (optionally filtered by profile_id)."""
    return get_suppliers(profile_id)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int):
    """Return a single supplier offering by its BIGINT id."""
    record = get_supplier_by_id(supplier_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Supplier offering {supplier_id} not found.")
    return record


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, supplier: SupplierCreate, background_tasks: BackgroundTasks):
    from app.services.database import supabase
    data = supplier.model_dump()
    data["embedding"] = None
    
    res = supabase.table("suppliers").update(data).eq("id", supplier_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Supplier offering not found.")
        
    supabase.table("matches").delete().eq("supplier_id", supplier_id).execute()
    
    def re_evaluate_clients():
        from app.services.embeddings import get_embedding
        from app.services.matching import get_supplier_text, match_client
        # 1. Gen emb for this supplier
        sup = supabase.table("suppliers").select("*").eq("id", supplier_id).execute()
        if sup.data:
            s_text = get_supplier_text(sup.data[0])
            emb = get_embedding(s_text)
            if emb:
                supabase.table("suppliers").update({"embedding": emb}).eq("id", supplier_id).execute()
        
        # 2. Re-run matches for active clients
        clients = supabase.table("clients").select("id").execute()
        if clients.data:
            for c in clients.data:
                match_client(c["id"])
                
    background_tasks.add_task(re_evaluate_clients)
    
    return res.data[0]
