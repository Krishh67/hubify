"""
API routes for supplier offerings.

POST /api/suppliers      — Submit a new supplier offering
GET  /api/suppliers      — List all supplier offerings
GET  /api/suppliers/{id} — Get a single supplier offering by BIGINT id
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

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

