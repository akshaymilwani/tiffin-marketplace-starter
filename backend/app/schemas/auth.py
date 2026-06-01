from pydantic import BaseModel, EmailStr

class SignUpRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "customer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
