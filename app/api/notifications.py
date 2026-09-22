"""
API routes for notifications.

GET /api/notifications — List all notifications (empty in Phase 1)
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

from app.services.database import get_notifications

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("")
def list_notifications(user_id: Optional[int] = None):
    """
    Return all notification records.

    Phase 1: Returns an empty list.
    Phase 2: Returns match-related notifications for clients and suppliers.
    """
    return get_notifications(user_id)
