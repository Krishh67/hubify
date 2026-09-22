import logging
from app.services.database import supabase

logger = logging.getLogger(__name__)

def create_notification(client_id: int = None, supplier_id: int = None, message: str = "", match_id: int = None):
    """Create a notification in the database."""
    try:
        data = {
            "message": message,
            "is_read": False
        }
        if client_id:
            data["client_id"] = client_id
        if supplier_id:
            data["supplier_id"] = supplier_id
        if match_id:
            data["match_id"] = match_id
            
        supabase.table("notifications").insert(data).execute()
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
