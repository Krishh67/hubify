from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.auth import SignInRequest, SignUpRequest
from app.services.database import get_profile_by_email, create_profile
from app.services.matching import process_missing_embeddings_and_match

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup")
def signup(req: SignUpRequest, background_tasks: BackgroundTasks):
    existing = get_profile_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    # In a real app we would hash the password. Here we follow demo auth requirements.
    profile = create_profile(req.model_dump())
    
    background_tasks.add_task(process_missing_embeddings_and_match)
    return {"message": "Account created successfully", "role": profile["role"], "id": profile["id"]}

@router.post("/signin")
def signin(req: SignInRequest, background_tasks: BackgroundTasks):
    profile = get_profile_by_email(req.email)
    if not profile or profile["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    background_tasks.add_task(process_missing_embeddings_and_match)
    return {"message": "Signed in successfully", "role": profile["role"], "id": profile["id"]}

