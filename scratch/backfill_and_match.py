import os
import sys
import logging

# Add the project root to the sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database import supabase
from app.services.embeddings import get_embedding
from app.services.matching import get_supplier_text, get_client_text, match_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backfill():
    # 1. Suppliers
    logger.info("Fetching suppliers without embeddings...")
    res = supabase.table("suppliers").select("*").is_("embedding", "null").execute()
    suppliers = res.data or []
    
    for supp in suppliers:
        logger.info(f"Generating embedding for supplier {supp['id']}...")
        text = get_supplier_text(supp)
        emb = get_embedding(text)
        supabase.table("suppliers").update({"embedding": emb}).eq("id", supp["id"]).execute()
        
    # 2. Clients
    logger.info("Fetching clients without embeddings...")
    res = supabase.table("clients").select("*").is_("embedding", "null").execute()
    clients = res.data or []
    
    for client in clients:
        logger.info(f"Generating embedding for client {client['id']}...")
        text = get_client_text(client)
        emb = get_embedding(text)
        supabase.table("clients").update({"embedding": emb}).eq("id", client["id"]).execute()
        
    logger.info("Backfill of embeddings complete.")
    
    # 3. Trigger matching for ALL clients to evaluate existing products
    logger.info("Fetching all clients to trigger matching pipeline...")
    all_clients = supabase.table("clients").select("id").execute().data or []
    
    for client in all_clients:
        logger.info(f"Running match pipeline for client {client['id']}...")
        try:
            match_client(client["id"])
            logger.info(f"Successfully ran match pipeline for client {client['id']}")
        except Exception as e:
            logger.error(f"Failed to match client {client['id']}: {e}")

if __name__ == "__main__":
    backfill()

