from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.utils.security import decode_access_token


@dataclass(frozen=True)
class Principal:
    subject: str
    org_id: str | None
    roles: frozenset[str]


_current_principal: ContextVar[Principal] = ContextVar(
    "current_principal",
    default=Principal(subject="anonymous", org_id=None, roles=frozenset()),
)
_bearer = HTTPBearer(auto_error=False)


def current_principal() -> Principal:
    return _current_principal.get()


def set_principal(principal: Principal):
    return _current_principal.set(principal)


def reset_principal(token):
    _current_principal.reset(token)


async def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> Principal:
    if credentials is not None and credentials.credentials:
        raw_token = credentials.credentials.strip()
        # 1. Try decoding our unified HS256 JWT access token
        payload = decode_access_token(raw_token)
        if payload and "sub" in payload:
            sub = str(payload["sub"])
            org_id = str(payload.get("org_id") or payload.get("organization") or "NTRO")
            raw_roles = payload.get("roles") or [payload.get("role") or "Analyst"]
            roles = frozenset(raw_roles if isinstance(raw_roles, list) else [raw_roles])
            principal = Principal(subject=sub, org_id=org_id, roles=roles)
            _current_principal.set(principal)
            return principal

        # 2. If Keycloak / OIDC RS256 is enabled, try decoding with JWKS
        if settings.AUTH_ENABLED:
            try:
                import httpx
                from jose import jwt

                jwks_url = settings.OIDC_JWKS_URL or f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/certs"
                async with httpx.AsyncClient(timeout=5.0) as client:
                    jwks = (await client.get(jwks_url)).raise_for_status().json()
                header = jwt.get_unverified_header(raw_token)
                key = next(key for key in jwks["keys"] if key["kid"] == header["kid"])
                claims = jwt.decode(
                    raw_token,
                    key,
                    algorithms=["RS256"],
                    audience=settings.OIDC_AUDIENCE,
                    issuer=settings.OIDC_ISSUER_URL,
                )
                org_id = claims.get("org_id") or claims.get("tenant_id") or claims.get("organization")
                if not org_id:
                    raise HTTPException(status_code=403, detail="Token has no organization claim")
                roles = set(claims.get("roles", []))
                roles.update(claims.get("realm_access", {}).get("roles", []))
                principal = Principal(subject=claims["sub"], org_id=str(org_id), roles=frozenset(roles))
                _current_principal.set(principal)
                return principal
            except HTTPException:
                raise
            except Exception as exc:
                raise HTTPException(status_code=401, detail="Invalid bearer token") from exc

    # 3. If AUTH_ENABLED is False, permit anonymous access
    if not settings.AUTH_ENABLED:
        principal = Principal(subject="anonymous", org_id=None, roles=frozenset())
        _current_principal.set(principal)
        return principal

    raise HTTPException(status_code=401, detail="Bearer authentication required")


def require_role(role: str):
    async def dependency(principal: Principal = Depends(get_current_principal)) -> Principal:
        if role not in principal.roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return principal

    return dependency
