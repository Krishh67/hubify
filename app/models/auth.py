from pydantic import BaseModel, EmailStr

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class SignUpRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str
    company_name: str = ""

