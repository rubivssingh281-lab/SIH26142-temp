import asyncio
import logging
import uuid
import random
import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.email_service import send_styled_otp_email as send_otp_email

router = APIRouter()
logger = logging.getLogger(__name__)

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    organization: str = None
    password: str

class RequestOTPRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    code: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# In-memory store for demo without Docker
mock_users = {}
mock_otps = {}

@router.post("/register")
async def register(req: RegisterRequest):
    mock_users[req.email] = {"name": req.name, "org": req.organization, "active": False}
    
    # Generate OTP
    code = str(random.randint(100000, 999999))
    mock_otps[req.email] = {
        "code": code,
        "expires": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10),
        "purpose": "registration"
    }
    
    try:
        await asyncio.to_thread(send_otp_email, req.email, code, "verification")
    except Exception:
        logger.exception("otp_email_delivery_failed", extra={"email": req.email})
        mock_users.pop(req.email, None)
        mock_otps.pop(req.email, None)
        raise HTTPException(status_code=503, detail="Unable to send verification email")
    
    return {"message": "Account created. OTP sent to email."}

@router.post("/request-login-otp")
async def request_login_otp(req: RequestOTPRequest):
    # Auto-provision user profile for demo if not already registered
    if req.email not in mock_users:
        mock_users[req.email] = {
            "name": req.email.split("@")[0].replace(".", " ").title(),
            "org": "NTRO — Imagery Analysis",
            "active": True
        }
    
    # Generate OTP
    code = str(random.randint(100000, 999999))
    mock_otps[req.email] = {
        "code": code,
        "expires": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10),
        "purpose": "login"
    }
    
    try:
        await asyncio.to_thread(send_otp_email, req.email, code, "login")
    except Exception:
        logger.exception("login_otp_email_delivery_failed", extra={"email": req.email})
        mock_otps.pop(req.email, None)
        raise HTTPException(status_code=503, detail="Unable to send login verification email")
    
    return {"message": "Login code sent to email."}

@router.post("/verify-otp")
@router.post("/verify-login-otp")
async def verify_otp(req: VerifyOTPRequest):
    otp = mock_otps.get(req.email)
    
    if not otp or otp["code"] != req.code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    if otp["expires"] < datetime.datetime.now(datetime.timezone.utc):
        mock_otps.pop(req.email, None)
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new code.")
        
    if req.email in mock_users:
        mock_users[req.email]["active"] = True
    else:
        mock_users[req.email] = {
            "name": req.email.split("@")[0].replace(".", " ").title(),
            "org": "NTRO — Imagery Analysis",
            "active": True
        }
        
    # Consume OTP so it cannot be reused
    mock_otps.pop(req.email, None)
    
    user_info = mock_users[req.email]
    return {
        "message": "OTP verified successfully",
        "token": f"jwt_{uuid.uuid4().hex[:16]}",
        "user": {
            "email": req.email,
            "name": user_info.get("name", "Analyst"),
            "organization": user_info.get("org", "NTRO")
        }
    }

@router.post("/login")
async def login(req: LoginRequest):
    if req.email not in mock_users:
        # Auto-provision demo account for seamless demo testing
        mock_users[req.email] = {
            "name": req.email.split("@")[0].replace(".", " ").title(),
            "org": "NTRO — Imagery Analysis",
            "active": True
        }
    
    user_info = mock_users[req.email]
    return {
        "message": "Logged in successfully",
        "token": f"jwt_{uuid.uuid4().hex[:16]}",
        "user": {
            "email": req.email,
            "name": user_info.get("name", "Analyst"),
            "organization": user_info.get("org", "NTRO")
        }
    }
