import asyncio
import datetime
import logging
import random
import uuid
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.auth import Principal, get_current_principal
from app.db.session import get_db
from app.db.models import User, OTPRecord, OTP
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    OTPGenerate,
    OTPVerify,
    PasswordResetRequest,
    PasswordResetConfirm,
    GoogleLoginRequest,
    UserResponse,
    AuthResponse,
)
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.services.email_service import send_styled_otp_email

logger = logging.getLogger(__name__)
router = APIRouter()

def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()

def _format_user_response(user: User) -> dict:
    full_name = user.name or f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip() or user.email.split("@")[0].title()
    first_name = user.first_name or full_name.split(" ")[0]
    last_name = user.last_name or " ".join(full_name.split(" ")[1:])
    return {
        "id": str(user.id),
        "email": user.email,
        "name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "is_verified": bool(user.is_verified),
        "is_active": bool(user.is_active),
        "role": user.role or "Analyst",
        "organization": user.organization or "NTRO — Imagery Analysis",
        "default_jurisdiction": user.default_jurisdiction or "INDIA",
    }

# ---------------------------------------------------------------------------
# Supabase HTTPS API Bridge Functions (with SMTP Fallback)
# ---------------------------------------------------------------------------

async def send_supabase_otp(email: str) -> bool:
    """Dispatches a 6-digit OTP code through Supabase Auth HTTPS endpoint over port 443."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY or "PROJECT_REF" in settings.SUPABASE_URL:
        return False
    try:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/otp"
        headers = {
            "apikey": settings.SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers, json={"email": email, "create_user": True})
            if resp.status_code in (200, 201):
                logger.info("supabase_otp_dispatched_successfully", extra={"email": email})
                return True
            logger.warning("supabase_otp_failed_response", extra={"status": resp.status_code, "text": resp.text})
            return False
    except Exception as exc:
        logger.error(f"supabase_otp_exception: {exc}", extra={"email": email})
        return False


async def send_supabase_password_reset(email: str) -> bool:
    """Dispatches a password recovery OTP code through Supabase Auth HTTPS endpoint over port 443."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY or "PROJECT_REF" in settings.SUPABASE_URL:
        return False
    try:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/recover"
        headers = {
            "apikey": settings.SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers, json={"email": email})
            if resp.status_code in (200, 201):
                logger.info("supabase_recover_dispatched_successfully", extra={"email": email})
                return True
            logger.warning("supabase_recover_failed_response", extra={"status": resp.status_code, "text": resp.text})
            return False
    except Exception as exc:
        logger.error(f"supabase_recover_exception: {exc}", extra={"email": email})
        return False


async def verify_supabase_otp(email: str, token: str, otp_type: str = "email") -> bool:
    """Verifies a 6-digit OTP code against Supabase Auth HTTPS endpoint."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY or "PROJECT_REF" in settings.SUPABASE_URL:
        return False
    types_to_try = [otp_type, "email" if otp_type == "recovery" else "recovery", "magiclink", "signup"]
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }
    for t in types_to_try:
        try:
            url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/verify"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, headers=headers, json={"type": t, "email": email, "token": token})
                if resp.status_code == 200:
                    logger.info("supabase_otp_verified_successfully", extra={"email": email, "type": t})
                    return True
        except Exception:
            pass
    return False


async def _save_and_send_local_otp(email: str, db: AsyncSession, purpose: str = "login") -> str:
    """Fallback OTP generator using local database and Gmail SMTP."""
    code = f"{random.randint(100000, 999999):06d}"
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)

    # Clean previous OTPs for this email
    await db.execute(delete(OTPRecord).where(OTPRecord.email == email))
    await db.execute(delete(OTP).where(OTP.email == email))

    rec = OTPRecord(email=email, otp_code=code, expires_at=expires_at)
    rec_compat = OTP(email=email, code=code, expires_at=expires_at)
    db.add(rec)
    db.add(rec_compat)
    await db.commit()

    try:
        await asyncio.to_thread(send_styled_otp_email, email, code, purpose)
    except Exception as exc:
        logger.warning(f"smtp_delivery_failed_simulating_for_dev: {exc}")

    return code


async def _verify_local_otp(email: str, code: str, db: AsyncSession) -> bool:
    """Verifies OTP code against local database records."""
    clean_code = code.strip()
    now = datetime.datetime.now(datetime.timezone.utc)

    # Check OTPRecord
    stmt = select(OTPRecord).where(OTPRecord.email == email, OTPRecord.otp_code == clean_code)
    res = await db.execute(stmt)
    record = res.scalars().first()
    if record and record.expires_at >= now:
        await db.execute(delete(OTPRecord).where(OTPRecord.email == email))
        await db.execute(delete(OTP).where(OTP.email == email))
        await db.commit()
        return True

    # Check OTP compatibility table
    stmt2 = select(OTP).where(OTP.email == email, OTP.code == clean_code)
    res2 = await db.execute(stmt2)
    record2 = res2.scalars().first()
    if record2 and record2.expires_at >= now:
        await db.execute(delete(OTPRecord).where(OTPRecord.email == email))
        await db.execute(delete(OTP).where(OTP.email == email))
        await db.commit()
        return True

    return False


# ---------------------------------------------------------------------------
# Core Authentication Endpoints
# ---------------------------------------------------------------------------

@router.post("/signup", response_model=dict)
@router.post("/register", response_model=dict)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """User registration with automatic 6-digit OTP dispatch."""
    email = _normalize_email(user_in.email)
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if user and user.is_verified:
        raise HTTPException(status_code=400, detail="Email is already registered. Please sign in.")

    hashed_pwd = get_password_hash(user_in.password)
    full_name = user_in.name or f"{(user_in.first_name or '').strip()} {(user_in.last_name or '').strip()}".strip() or email.split("@")[0].title()
    first_name = user_in.first_name or full_name.split(" ")[0]
    last_name = user_in.last_name or " ".join(full_name.split(" ")[1:])

    if user:
        user.hashed_password = hashed_pwd
        user.name = full_name
        user.first_name = first_name
        user.last_name = last_name
        user.organization = user_in.organization or user.organization
    else:
        user = User(
            email=email,
            hashed_password=hashed_pwd,
            name=full_name,
            first_name=first_name,
            last_name=last_name,
            organization=user_in.organization or "NTRO — Imagery Analysis",
            is_verified=False,
            is_active=True,
            role="Analyst",
            default_jurisdiction="INDIA"
        )
        db.add(user)
    await db.commit()

    # 1. Try Supabase Auth HTTPS OTP
    dispatched = await send_supabase_otp(email)
    # 2. If Supabase is not configured or failed, use local SMTP
    if not dispatched:
        await _save_and_send_local_otp(email, db, purpose="verification")

    return {
        "message": "Verification code sent to your email.",
        "requires_otp": True,
        "email": email
    }


@router.post("/login", response_model=AuthResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticates user via email and password."""
    email = _normalize_email(user_in.email)
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user or not user.hashed_password or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not user.is_verified:
        # User registered but has not verified email OTP yet
        dispatched = await send_supabase_otp(email)
        if not dispatched:
            await _save_and_send_local_otp(email, db, purpose="verification")
        raise HTTPException(
            status_code=403,
            detail="Email address not verified yet. A new verification code was sent to your email."
        )

    token = create_access_token({
        "sub": user.email,
        "role": user.role or "Analyst",
        "organization": user.organization or "NTRO"
    })
    user_data = _format_user_response(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "token": token,
        "message": "Logged in successfully",
        "user": user_data
    }


@router.post("/request-otp")
@router.post("/request-login-otp")
async def request_otp(otp_in: OTPGenerate, db: AsyncSession = Depends(get_db)):
    """Dispatches a single-use 6-digit login OTP code to user's email."""
    email = _normalize_email(otp_in.email)
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user:
        # Auto-provision user account for frictionless experience
        full_name = email.split("@")[0].replace(".", " ").title()
        user = User(
            email=email,
            hashed_password=get_password_hash(f"OTP_PROVISIONED_{uuid.uuid4().hex[:12]}"),
            name=full_name,
            first_name=full_name.split(" ")[0],
            last_name=" ".join(full_name.split(" ")[1:]),
            organization="NTRO — Imagery Analysis",
            is_verified=False,
            is_active=True,
            role="Analyst",
            default_jurisdiction="INDIA"
        )
        db.add(user)
        await db.commit()

    # 1. Try Supabase Auth HTTPS OTP
    dispatched = await send_supabase_otp(email)
    # 2. Fall back to local SMTP
    if not dispatched:
        await _save_and_send_local_otp(email, db, purpose="login")

    return {"message": "Verification code sent to your email.", "email": email}


@router.post("/verify-otp", response_model=AuthResponse)
@router.post("/verify-login-otp", response_model=AuthResponse)
async def verify_otp(otp_in: OTPVerify, db: AsyncSession = Depends(get_db)):
    """Verifies a single-use 6-digit code and issues an authenticated session."""
    email = _normalize_email(otp_in.email)
    code = otp_in.get_code()

    if len(code) != 6:
        raise HTTPException(status_code=400, detail="Verification code must be 6 digits")

    # 1. Try Supabase HTTPS verify
    is_valid = await verify_supabase_otp(email, code, otp_type="email")
    # 2. If not verified via Supabase, check local DB
    if not is_valid:
        is_valid = await _verify_local_otp(email, code, db)

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user:
        full_name = email.split("@")[0].replace(".", " ").title()
        user = User(
            email=email,
            hashed_password=get_password_hash("OTP_AUTHENTICATED"),
            name=full_name,
            first_name=full_name.split(" ")[0],
            last_name=" ".join(full_name.split(" ")[1:]),
            organization="NTRO — Imagery Analysis",
            is_verified=True,
            is_active=True,
            role="Analyst",
            default_jurisdiction="INDIA"
        )
        db.add(user)
    else:
        user.is_verified = True
        user.is_active = True

    await db.commit()
    await db.refresh(user)

    token = create_access_token({
        "sub": user.email,
        "role": user.role or "Analyst",
        "organization": user.organization or "NTRO"
    })
    user_data = _format_user_response(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "token": token,
        "message": "OTP verified successfully",
        "user": user_data
    }


@router.post("/forgot-password")
async def forgot_password(payload: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """Initiates password reset by dispatching a 6-digit recovery code."""
    email = _normalize_email(payload.email)
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="No account found associated with this email address")

    # 1. Try Supabase password recovery
    sent = await send_supabase_password_reset(email)
    if not sent:
        # Fall back to local OTP generation & SMTP
        await _save_and_send_local_otp(email, db, purpose="verification")

    return {"message": "Password reset code sent to your email."}


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(payload: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    """Verifies recovery code and updates the user's password."""
    email = _normalize_email(payload.email)
    code = payload.get_code()
    new_pwd = payload.new_password.strip()

    if len(new_pwd) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    # 1. Try Supabase verify with recovery type
    is_valid = await verify_supabase_otp(email, code, otp_type="recovery")
    # 2. Check local DB fallback
    if not is_valid:
        is_valid = await _verify_local_otp(email, code, db)

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User account not found")

    user.hashed_password = get_password_hash(new_pwd)
    user.is_verified = True
    user.is_active = True
    await db.commit()
    await db.refresh(user)

    token = create_access_token({
        "sub": user.email,
        "role": user.role or "Analyst",
        "organization": user.organization or "NTRO"
    })
    user_data = _format_user_response(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "token": token,
        "message": "Password reset successfully. You are now signed in.",
        "user": user_data
    }


@router.post("/google", response_model=AuthResponse)
async def google_auth(payload: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticates or automatically provisions user from Google Firebase OAuth sign-in."""
    email = _normalize_email(payload.email)
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email from Google account")

    name = payload.name or payload.displayName or ""
    first_name = payload.first_name or (name.split(" ")[0] if name else email.split("@")[0].title())
    last_name = payload.last_name or (" ".join(name.split(" ")[1:]) if name else "")
    full_name = f"{first_name} {last_name}".strip()

    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user:
        user = User(
            email=email,
            hashed_password=get_password_hash(f"GOOGLE_FIREBASE_OAUTH_{uuid.uuid4().hex}"),
            name=full_name,
            first_name=first_name,
            last_name=last_name,
            organization="NTRO — Imagery Analysis",
            is_verified=True,
            is_active=True,
            role="Analyst",
            default_jurisdiction="INDIA"
        )
        db.add(user)
    else:
        user.is_verified = True
        user.is_active = True
        if first_name and not user.first_name:
            user.first_name = first_name
        if last_name and not user.last_name:
            user.last_name = last_name
        if full_name and not user.name:
            user.name = full_name

    await db.commit()
    await db.refresh(user)

    token = create_access_token({
        "sub": user.email,
        "role": user.role or "Analyst",
        "organization": user.organization or "NTRO"
    })
    user_data = _format_user_response(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "token": token,
        "message": "Signed in with Google successfully",
        "user": user_data
    }


@router.get("/me", response_model=dict)
async def get_current_user_profile(
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db)
):
    """Returns the authenticated operator profile."""
    if principal.subject == "anonymous":
        return {
            "email": "anonymous@ntro.gov.in",
            "name": "Operator",
            "role": "Analyst",
            "organization": "NTRO — Imagery Analysis",
            "is_authenticated": False
        }

    stmt = select(User).where(User.email == principal.subject)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if user:
        profile = _format_user_response(user)
        profile["is_authenticated"] = True
        return profile

    return {
        "email": principal.subject,
        "name": principal.subject.split("@")[0].title(),
        "role": list(principal.roles)[0] if principal.roles else "Analyst",
        "organization": principal.org_id or "NTRO",
        "is_authenticated": True
    }
