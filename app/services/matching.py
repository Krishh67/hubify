import os
import json
import logging
import numpy as np
from typing import List, Dict, Any
from google import genai
from pydantic import BaseModel
from app.services.database import supabase, get_client_by_id
from app.services.embeddings import get_embedding
from app.services.notifications import create_notification

logger = logging.getLogger(__name__)

# Base units for normalization
# quantity * factor = base_quantity
UNIT_CONVERSIONS = {
    "kg": ("mass", 1.0),
    "mt": ("mass", 1000.0),
    "l": ("volume", 1.0),
    "cbm": ("volume", 1000.0),
    "m": ("length", 1.0),
    "sqm": ("area", 1.0),
    "pcs": ("count", 1.0),
    "boxes": ("count", 100.0), # assumed fallback
    "pallets": ("count", 1000.0), # assumed fallback
}

class LLMMatchOutput(BaseModel):
    supplier_id: int
    product_fit_score: float
    spec_score: float
    certification_compatibility: str
    risks: List[str]
    deal_breakers: List[str]
    explanation: str

class LLMRankingList(BaseModel):
    matches: List[LLMMatchOutput]

def cosine_similarity(a, b) -> float:
    if isinstance(a, str):
        a = json.loads(a)
    if isinstance(b, str):
        b = json.loads(b)
        
    a_np = np.array(a, dtype=float)
    b_np = np.array(b, dtype=float)
    if np.linalg.norm(a_np) == 0 or np.linalg.norm(b_np) == 0:
        return 0.0
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))

def get_normalized_quantity_and_price(qty: float, price: float, unit: str):
    unit_lower = unit.lower().strip()
    if unit_lower in UNIT_CONVERSIONS:
        family, factor = UNIT_CONVERSIONS[unit_lower]
        base_qty = qty * factor
        base_price = price / factor if price else 0
        return family, base_qty, base_price
    return "other", qty, price

def get_client_text(req: dict) -> str:
    return f"Product: {req.get('product_requirement', '')}\nCategory: {req.get('category', '')}\nSpecs: {json.dumps(req.get('specs', {}))}\nCertifications: {req.get('certifications', [])}\nNotes: {req.get('additional_notes', '')}"

def get_supplier_text(supp: dict) -> str:
    return f"Product: {supp.get('product_offered', '')}\nCategory: {supp.get('category', '')}\nSpecs: {json.dumps(supp.get('specs', {}))}\nCertifications: {supp.get('certifications', [])}\nNotes: {supp.get('additional_notes', '')}\nDelivery: {supp.get('delivery_capability', '')}"

def call_llm_reranker(client_req: dict, top_candidates: list[dict]) -> dict:
    """Uses Gemini structured output to evaluate candidates."""
    api_keys = [
        os.environ.get("GEMINI_API_KEY"),
        os.environ.get("GEMINI_API_KEY0"),
        os.environ.get("GEMINI_API_KEY1"),
        os.environ.get("GEMINI_API_KEY2")
    ]
    api_keys = [k for k in api_keys if k]
    if not api_keys:
        logger.error("No GEMINI_API_KEY found")
        return None
    
    prompt = f"Evaluate the suitability of the following {len(top_candidates)} suppliers for this client requirement.\n\n"
    prompt += f"CLIENT REQUIREMENT:\n"
    prompt += f"Product: {client_req.get('product_requirement')}\n"
    prompt += f"Category: {client_req.get('category')}\n"
    prompt += f"Specs: {json.dumps(client_req.get('specs'))}\n"
    prompt += f"Certs: {client_req.get('certifications')}\n"
    prompt += f"Notes: {client_req.get('additional_notes')}\n\n"
    
    prompt += "CANDIDATE SUPPLIERS:\n"
    for s in top_candidates:
        prompt += f"--- Supplier ID: {s['id']} ---\n"
        prompt += f"Product: {s.get('product_offered')}\n"
        prompt += f"Category: {s.get('category')}\n"
        prompt += f"Specs: {json.dumps(s.get('specs'))}\n"
        prompt += f"Certs: {s.get('certifications')}\n"
        prompt += f"Notes: {s.get('additional_notes')}\n\n"
        
    prompt += (
        "This is a high-level matchmaking platform. DO NOT heavily penalize missing technical details or specifications. "
        "If the products are in the same general domain/category and serve the core purpose, give a high product_fit_score and spec_score (80-100). "
        "The buyer and supplier will finalize exact technical specifics upon contact. "
        "Return a structured JSON evaluation for each supplier. Provide product_fit_score (0-100) and spec_score (0-100)."
    )
    
    models_to_try = [
        'gemini-3.6-flash',
        'gemini-3.5-flash',
        'gemini-3.5-flash-lite'
    ]
    
    for key in api_keys:
        client = genai.Client(api_key=key)
        key_exhausted = False
        
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=LLMRankingList,
                        temperature=0.1
                    )
                )
                print(f"Gemini LLM Output for Client {client_req.get('id')} using {model_name}: {response.text}")
                return json.loads(response.text)
            except Exception as e:
                err_str = str(e).lower()
                logger.warning(f"LLM Reranking failed for model {model_name} on key {key[:4]}...: {e}")
                if "429" in err_str or "quota" in err_str or "exhausted" in err_str or "rate limit" in err_str:
                    key_exhausted = True
                    break
                else:
                    continue
        if not key_exhausted:
            break
            
    logger.error("All fallback models/keys failed for LLM Reranking.")
    return None

def match_client(client_id: int):
    client_req = get_client_by_id(client_id)
    if not client_req:
        raise ValueError(f"Client requirement {client_id} not found.")

    # 1. EMBEDDING
    client_text = get_client_text(client_req)
    try:
        client_emb = get_embedding(client_text)
    except Exception as e:
        logger.error(f"Failed to generate embedding for client: {e}")
        raise ValueError("Embedding failed gracefully.")

    # 2. SEMANTIC RETRIEVAL
    # Since RPC might fail or be missing in the schema, we use fallback python logic.
    all_suppliers = []
    try:
        res = supabase.rpc("match_suppliers", {"query_embedding": str(client_emb), "match_count": 20}).execute()
        all_suppliers = res.data
    except Exception:
        # Fallback: pull active suppliers and compute in python
        res = supabase.table("suppliers").select("*").execute()
        all_suppliers = res.data
        
        # Ensure embeddings exist
        for s in all_suppliers:
            if not s.get("embedding"):
                s_text = get_supplier_text(s)
                s["embedding"] = get_embedding(s_text)
                # optionally save back
                try:
                    supabase.table("suppliers").update({"embedding": s["embedding"]}).eq("id", s["id"]).execute()
                except Exception:
                    pass
        
        # Calculate semantic score
        for s in all_suppliers:
            if s.get("embedding"):
                s["semantic_sim"] = cosine_similarity(client_emb, s["embedding"])
            else:
                s["semantic_sim"] = 0.0
                
        # Sort and take top 20
        all_suppliers.sort(key=lambda x: x["semantic_sim"], reverse=True)
        all_suppliers = all_suppliers[:20]

    if not all_suppliers:
        return {"status": "success", "message": "No suppliers available to match."}

    # 3. CONSTRAINTS (Delivery is now a soft constraint)
    client_del_days = client_req.get("delivery_days", 999999)
    valid_suppliers = all_suppliers

    # Calculate Semantic Score for valid candidates if not already done by python fallback
    for s in valid_suppliers:
        if "semantic_sim" not in s:
            if s.get("embedding"):
                s["semantic_sim"] = cosine_similarity(client_emb, s["embedding"])
            else:
                s["semantic_sim"] = 0.0

    # 4 & 5. UOM & DETERMINISTIC SCORING
    c_family, c_base_qty, c_base_budget = get_normalized_quantity_and_price(
        client_req["quantity_required"], client_req["budget"], client_req["unit"]
    )
    
    scored_suppliers = []
    for s in valid_suppliers:
        s_family, s_base_qty, s_base_price = get_normalized_quantity_and_price(
            s["available_quantity"], s["unit_price"], s["unit"]
        )
        
        # Quantity Score
        qty_score = 0.0
        if c_family == s_family and c_family != "other":
            if s_base_qty >= c_base_qty:
                qty_score = 100.0
            else:
                qty_score = (s_base_qty / c_base_qty) * 100.0
        elif client_req["unit"].lower().strip() == s["unit"].lower().strip():
            if s["available_quantity"] >= client_req["quantity_required"]:
                qty_score = 100.0
            else:
                qty_score = (s["available_quantity"] / client_req["quantity_required"]) * 100.0
        
        qty_score = max(0.0, min(100.0, qty_score))
        
        # Budget Score
        budget_score = 0.0
        if c_family == s_family and c_family != "other":
            if s_base_price <= c_base_budget:
                budget_score = 100.0
            else:
                # Penalty for being over budget
                overage = s_base_price - c_base_budget
                penalty = (overage / c_base_budget) * 100.0 if c_base_budget > 0 else 100.0
                budget_score = max(0.0, 100.0 - penalty)
        elif client_req["unit"].lower().strip() == s["unit"].lower().strip():
            if s["unit_price"] <= client_req["budget"]:
                budget_score = 100.0
            else:
                c_u_p = client_req["budget"]
                overage = s["unit_price"] - c_u_p
                budget_score = max(0.0, 100.0 - (overage/c_u_p * 100.0))
                
        # Delivery Score (Allows 1-2 weeks margin of error)
        s_del_days = s.get("delivery_days", 0)
        if s_del_days <= client_del_days:
            del_score = 100.0
        else:
            # Over deadline: penalty applies. Margin of error ~ 14 days
            diff = s_del_days - client_del_days
            penalty = (diff / 14.0) * 100.0
            del_score = max(0.0, 100.0 - penalty)
            
        # Location Score
        loc_score = 25.0
        if client_req.get("city") == s.get("city"):
            loc_score = 100.0
        elif client_req.get("state") == s.get("state"):
            loc_score = 75.0
        elif client_req.get("country") == s.get("country"):
            loc_score = 50.0

        s["semantic_score"] = s["semantic_sim"] * 100.0
        s["quantity_score"] = qty_score
        s["budget_score"] = budget_score
        s["delivery_score"] = del_score
        s["location_score"] = loc_score
        
        # Pre-calculate a temporary score for top 10 ranking
        s["temp_score"] = (s["semantic_score"] + qty_score + budget_score + del_score + loc_score) / 5
        scored_suppliers.append(s)

    # Sort and take top 10
    scored_suppliers.sort(key=lambda x: x["temp_score"], reverse=True)
    top_10 = scored_suppliers[:10]

    if not top_10:
        return {"status": "success", "message": "No suppliers met hard constraints."}

    # 6. LLM RERANKING
    llm_output = call_llm_reranker(client_req, top_10)
    
    llm_map = {}
    if llm_output and "matches" in llm_output:
        for m in llm_output["matches"]:
            llm_map[m["supplier_id"]] = m

    # 7. FINAL SCORE
    final_results = []
    for s in top_10:
        llm_data = llm_map.get(s["id"], {})
        
        has_llm = bool(llm_data)
        p_fit = llm_data.get("product_fit_score", 50.0)
        s_score = llm_data.get("spec_score", 50.0)
        
        if has_llm:
            # 75% product fit, 25% for the rest
            final_score = (
                p_fit * 0.75 +
                s["semantic_score"] * 0.05 +
                s["quantity_score"] * 0.05 +
                s["budget_score"] * 0.05 +
                s["delivery_score"] * 0.05 +
                s["location_score"] * 0.05
            )
        else:
            # Fallback if LLM fails
            final_score = (
                s["semantic_score"] * 0.30 +
                s["quantity_score"] * 0.25 +
                s["budget_score"] * 0.25 +
                s["delivery_score"] * 0.10 +
                s["location_score"] * 0.10
            )
        
        final_results.append({
            "client_id": client_req["id"],
            "supplier_id": s["id"],
            "semantic_score": round(s["semantic_score"], 2),
            "product_fit_score": round(p_fit, 2),
            "quantity_score": round(s["quantity_score"], 2),
            "budget_score": round(s["budget_score"], 2),
            "delivery_score": round(s["delivery_score"], 2),
            "location_score": round(s["location_score"], 2),
            "spec_score": round(s_score, 2),
            "final_score": round(final_score, 2),
            "explanation": llm_data.get("explanation", "Matched based on system defaults."),
            "deal_breakers": llm_data.get("deal_breakers", []),
            "risks": llm_data.get("risks", [])
        })

    # Filter out scores < 30
    final_results = [r for r in final_results if r["final_score"] >= 30.0]

    # Sort by final score
    final_results.sort(key=lambda x: x["final_score"], reverse=True)
    
    # 8. STORE
    for idx, res in enumerate(final_results):
        res["rank"] = idx + 1
        try:
            # Using Supabase upsert (assuming unique constraint exists)
            existing = supabase.table("matches").select("id").eq("client_id", res["client_id"]).eq("supplier_id", res["supplier_id"]).execute()
            if existing.data:
                match_id = existing.data[0]["id"]
                supabase.table("matches").update(res).eq("id", match_id).execute()
            else:
                resp = supabase.table("matches").insert(res).execute()
                if resp.data:
                    match_id = resp.data[0]["id"]
                else:
                    continue
                    
            # Supplier notification
            create_notification(
                supplier_id=res["supplier_id"],
                message=f"Your offering matches a new buyer requirement with a score of {res['final_score']}.",
                match_id=match_id
            )
        except Exception as e:
            logger.error(f"Error saving match {res['client_id']}-{res['supplier_id']}: {e}")

    # Client notification (Once per requirement)
    if final_results:
        try:
            create_notification(
                client_id=client_req["id"],
                message=f"Matches found for your requirement '{client_req.get('product_requirement', '')}'. We found {len(final_results)} potential suppliers."
            )
        except Exception as e:
            logger.error(f"Error creating client notification: {e}")

    # Save embedding at the very end to signal UI that processing is fully complete
    try:
        supabase.table("clients").update({"embedding": client_emb}).eq("id", client_id).execute()
    except Exception as e:
        logger.warning(f"Could not save client embedding: {e}")

    return {"status": "success", "matches_created": len(final_results)}

def process_missing_embeddings_and_match():
    """Background task to generate embeddings for new records and trigger matching."""
    try:
        # Handle suppliers
        no_emb_suppliers = supabase.table("suppliers").select("id").is_("embedding", "null").execute()
        if no_emb_suppliers.data:
            suppliers_res = supabase.table("suppliers").select("*").in_("id", [s["id"] for s in no_emb_suppliers.data]).execute()
            for s in suppliers_res.data:
                s_text = get_supplier_text(s)
                emb = get_embedding(s_text)
                if emb:
                    supabase.table("suppliers").update({"embedding": emb}).eq("id", s["id"]).execute()
    except Exception as e:
        logger.error(f"Error updating supplier embeddings in background: {e}")

    try:
        # Handle clients
        no_emb_clients = supabase.table("clients").select("id").is_("embedding", "null").execute()
        if no_emb_clients.data:
            for c in no_emb_clients.data:
                match_client(c["id"])
    except Exception as e:
        logger.error(f"Error updating client embeddings in background: {e}")
