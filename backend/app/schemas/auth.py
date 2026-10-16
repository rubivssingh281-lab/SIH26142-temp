from typing import Optional, Union, Any
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = "NTRO — Imagery Analysis"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class OTPGenerate(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: Optional[str] = None
    code: Optional[str] = None

    def get_code(self) -> str:
        return (self.otp_code or self.code or "").strip()

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    otp_code: Optional[str] = None
    code: Optional[str] = None
    new_password: str = Field(..., min_length=6)

    def get_code(self) -> str:
        return (self.otp_code or self.code or "").strip()

class GoogleLoginRequest(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    displayName: Optional[str] = None
    id_token: Optional[str] = None

class UserResponse(BaseModel):
    id: Union[int, str]
    email: str
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_verified: bool = True
    is_active: bool = True
    role: Optional[str] = "Analyst"
    organization: Optional[str] = "NTRO — Imagery Analysis"
    default_jurisdiction: Optional[str] = "INDIA"

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    token: str # Compatibility alias for Bhu-Dristi UI
    message: Optional[str] = "Authentication successful"
    user: UserResponse
