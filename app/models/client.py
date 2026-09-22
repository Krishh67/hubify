"""
Pydantic models for Client data.
id is BIGINT (int) — Supabase identity column, not UUID.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field


class ClientCreate(BaseModel):
    """Fields accepted when a client submits a new requirement."""

    profile_id: int = Field(..., description="ID of the user profile creating this record")

    # Company / contact
    client_name: str = Field(..., min_length=1, max_length=255, description="Company or client name")
    email: EmailStr = Field(..., description="Contact email address")

    # Product details
    product_requirement: str = Field(..., min_length=1, description="Description of the product required")
    category: str = Field(..., min_length=1, description="Product category")
    specs: dict[str, Any] = Field(default_factory=dict, description="JSONB technical specifications")

    # Quantities & budget
    quantity_required: float = Field(..., gt=0, description="Quantity required")
    unit: str = Field(..., min_length=1, description="Unit of measure (kg, pcs, etc.)")
    budget: float = Field(..., ge=0, description="Estimated budget")

    # Location
    location: str = Field(..., min_length=1, description="Delivery location")
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    country: str = Field(..., min_length=1)

    # Timeline
    delivery_timeline: str = Field(..., min_length=1, description="Human-readable delivery timeline")
    delivery_days: int = Field(..., gt=0, description="Max acceptable lead time in days")

    # Optional
    additional_notes: Optional[str] = Field(None)
    certifications: list[str] = Field(default_factory=list, description="Required product certifications")


class ClientResponse(BaseModel):
    """Full client record returned by the API."""

    id: int
    profile_id: Optional[int] = None
    client_name: str
    email: str
    product_requirement: str
    category: str
    specs: dict[str, Any] = Field(default_factory=dict)
    quantity_required: float
    unit: str
    budget: float
    location: str
    city: str
    state: str
    country: str
    delivery_timeline: str
    delivery_days: int
    additional_notes: Optional[str] = None
    certifications: list[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    has_embedding: bool = False

    model_config = {"from_attributes": True}
