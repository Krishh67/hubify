import logging
from fastapi import APIRouter, HTTPException
from app.services.matching import match_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/matching", tags=["Matching"])

@router.post("/client/{client_id}")
def run_client_matching(client_id: int):
    """
    Run the AI matching pipeline for a specific client requirement.
    Process: embedding -> pgvector retrieval -> hard constraints -> deterministic scores -> top 10 -> LLM -> final score -> rank -> save matches -> notifications.
    """
    try:
        result = match_client(client_id)
        return result
    except ValueError as ve:
        logger.warning(f"Matching validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Matching pipeline failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during matching.")

