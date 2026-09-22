from fastapi import APIRouter, HTTPException
from app.models.auth import SignInRequest, SignUpRequest
from app.services.database import get_profile_by_email, create_profile

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup")
def signup(req: SignUpRequest):
    existing = get_profile_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    # In a real app we would hash the password. Here we follow demo auth requirements.
    profile = create_profile(req.model_dump())
    
    return {"message": "Account created successfully", "role": profile["role"], "id": profile["id"]}

@router.post("/signin")
def signin(req: SignInRequest):
    profile = get_profile_by_email(req.email)
    if not profile or profile["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    return {"message": "Signed in successfully", "role": profile["role"], "id": profile["id"]}

