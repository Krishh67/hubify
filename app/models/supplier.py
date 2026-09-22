"""
Pydantic models for Supplier data.
id is BIGINT (int) — Supabase identity column, not UUID.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field


class SupplierCreate(BaseModel):
    """Fields accepted when a supplier submits a new offering."""

    profile_id: int = Field(..., description="ID of the user profile creating this record")

    # Supplier / contact
    supplier_name: str = Field(..., min_length=1, max_length=255, description="Supplier company name")
    email: EmailStr = Field(..., description="Contact email address")

    # Product offered
    product_offered: str = Field(..., min_length=1, description="Description of the product offered")
    category: str = Field(..., min_length=1, description="Product category")
    specs: dict[str, Any] = Field(default_factory=dict, description="JSONB technical specifications")

    # Pricing & inventory
    pricing_details: str = Field(..., min_length=1, description="Human-readable pricing description")
    unit_price: float = Field(..., ge=0, description="Price per unit")
    min_order_qty: float = Field(..., ge=0, description="Minimum order quantity")
    available_quantity: float = Field(..., ge=0, description="Currently available quantity")
    unit: str = Field(..., min_length=1, description="Unit of measure (kg, pcs, MT, …)")

    # Location
    location: str = Field(..., min_length=1, description="Full location description")
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    country: str = Field(..., min_length=1)

    # Delivery
    delivery_capability: str = Field(..., min_length=1, description="Delivery capability description")
    delivery_days: int = Field(..., gt=0, description="Standard delivery lead time in days")

    # Optional
    additional_notes: Optional[str] = Field(None)
    certifications: list[str] = Field(default_factory=list, description="Product certifications or quality standards")


class SupplierResponse(BaseModel):
    """Full supplier record returned by the API."""

    id: int
    profile_id: Optional[int] = None
    supplier_name: str
    email: str
    product_offered: str
    category: str
    specs: dict[str, Any] = Field(default_factory=dict)
    pricing_details: str
    unit_price: float
    min_order_qty: float
    available_quantity: float
    unit: str
    location: str
    city: str
    state: str
    country: str
    delivery_capability: str
    delivery_days: int
    additional_notes: Optional[str] = None
    certifications: list[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    has_embedding: bool = False

    model_config = {"from_attributes": True}

