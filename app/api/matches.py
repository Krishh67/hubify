"""
API routes for AI-generated matches.

GET /api/matches — List all matches (empty in Phase 1)

POST /api/matching/run/{client_id} will be added in Phase 2.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.services.database import get_matches

router = APIRouter(prefix="/api/matches", tags=["Matches"])


from typing import Optional

@router.get("")
def list_matches(client_id: Optional[int] = None, supplier_id: Optional[int] = None):
    """
    Return all AI-generated match records.
    Filters by client_id or supplier_id.
    """
    return get_matches(client_id, supplier_id)

