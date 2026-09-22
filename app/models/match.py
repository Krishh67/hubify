"""
Pydantic models for Match and Notification data.
These are read-only in Phase 1 — populated by Phase 2 AI matching.
Using extra="allow" to handle whatever columns the tables contain.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class MatchResponse(BaseModel):
    """AI-generated match record."""

    id: Any
    client_id: Optional[int] = None
    supplier_id: Optional[int] = None
    final_score: Optional[float] = None
    semantic_score: Optional[float] = None
    category_score: Optional[float] = None
    quantity_score: Optional[float] = None
    budget_score: Optional[float] = None
    location_score: Optional[float] = None
    delivery_score: Optional[float] = None
    rank: Optional[int] = None
    status: Optional[str] = None
    explanation: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "extra": "allow"}


class NotificationResponse(BaseModel):
    """Notification record."""

    id: Any
    title: Optional[str] = None
    message: Optional[str] = None
    is_read: Optional[bool] = None
    notification_type: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "extra": "allow"}

