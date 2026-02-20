"""
aitema|RIS - Security Module
JWT validation, RBAC, and Keycloak integration.
"""
from __future__ import annotations

import time
from enum import StrEnum
from typing import Any

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()
security_scheme = HTTPBearer(auto_error=False)


class Role(StrEnum):
    """System roles following German municipal hierarchy."""
    SUPERADMIN = "superadmin"          # aitema platform admin
    ADMIN = "admin"                     # Kommune-Administrator
    SITZUNGSDIENST = "sitzungsdienst"  # Sitzungsdienst-Mitarbeiter
    FRAKTIONSMITARBEITER = "fraktionsmitarbeiter"
    RATSMITGLIED = "ratsmitglied"      # Elected council member
    SACHKUNDIGER = "sachkundiger"       # Expert citizen
    BUERGER = "buerger"                # Public citizen (read-only)
    ANONYMOUS = "anonymous"             # Unauthenticated


class Permission(StrEnum):
    """Fine-grained permissions."""
    # OParl read
    OPARL_READ = "oparl:read"
    
    # Meeting management
    MEETING_CREATE = "meeting:create"
    MEETING_EDIT = "meeting:edit"
    MEETING_DELETE = "meeting:delete"
    MEETING_INVITE = "meeting:invite"
    
    # Paper / Vorlage management
    PAPER_CREATE = "paper:create"
    PAPER_EDIT = "paper:edit"
    PAPER_DELETE = "paper:delete"
    PAPER_SUBMIT = "paper:submit"
    
    # Voting
    VOTE_CAST = "vote:cast"
    VOTE_VIEW = "vote:view"
    
    # File management
    FILE_UPLOAD = "file:upload"
    FILE_DELETE = "file:delete"
    FILE_VIEW_NONPUBLIC = "file:view_nonpublic"
    
    # Administration
    ADMIN_USERS = "admin:users"
    ADMIN_TENANTS = "admin:tenants"
    ADMIN_SETTINGS = "admin:settings"
    
    # Workflow
    WORKFLOW_MANAGE = "workflow:manage"
    WORKFLOW_APPROVE = "workflow:approve"


# Role -> Permissions mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.SUPERADMIN: set(Permission),  # All permissions
    Role.ADMIN: {
        Permission.OPARL_READ,
        Permission.MEETING_CREATE, Permission.MEETING_EDIT,
        Permission.MEETING_DELETE, Permission.MEETING_INVITE,
        Permission.PAPER_CREATE, Permission.PAPER_EDIT,
        Permission.PAPER_DELETE, Permission.PAPER_SUBMIT,
        Permission.VOTE_VIEW,
        Permission.FILE_UPLOAD, Permission.FILE_DELETE, Permission.FILE_VIEW_NONPUBLIC,
        Permission.ADMIN_USERS, Permission.ADMIN_SETTINGS,
        Permission.WORKFLOW_MANAGE, Permission.WORKFLOW_APPROVE,
    },
    Role.SITZUNGSDIENST: {
        Permission.OPARL_READ,
        Permission.MEETING_CREATE, Permission.MEETING_EDIT, Permission.MEETING_INVITE,
        Permission.PAPER_CREATE, Permission.PAPER_EDIT, Permission.PAPER_SUBMIT,
        Permission.VOTE_VIEW,
        Permission.FILE_UPLOAD, Permission.FILE_VIEW_NONPUBLIC,
        Permission.WORKFLOW_MANAGE, Permission.WORKFLOW_APPROVE,
    },
    Role.FRAKTIONSMITARBEITER: {
        Permission.OPARL_READ,
        Permission.PAPER_CREATE, Permission.PAPER_EDIT,
        Permission.VOTE_VIEW,
        Permission.FILE_UPLOAD, Permission.FILE_VIEW_NONPUBLIC,
    },
    Role.RATSMITGLIED: {
        Permission.OPARL_READ,
        Permission.PAPER_CREATE,
        Permission.VOTE_CAST, Permission.VOTE_VIEW,
        Permission.FILE_UPLOAD, Permission.FILE_VIEW_NONPUBLIC,
    },
    Role.SACHKUNDIGER: {
        Permission.OPARL_READ,
        Permission.VOTE_VIEW,
        Permission.FILE_VIEW_NONPUBLIC,
    },
    Role.BUERGER: {
        Permission.OPARL_READ,
    },
    Role.ANONYMOUS: {
        Permission.OPARL_READ,
    },
}


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str
    email: str = ""
    name: str = ""
    preferred_username: str = ""
    realm_access: dict[str, Any] = {}
    tenant_id: str = ""
    exp: int = 0

    @property
    def roles(self) -> list[str]:
        return self.realm_access.get("roles", [])

    @property
    def highest_role(self) -> Role:
        """Return the highest-privilege role the user has."""
        role_priority = list(Role)
        for role in role_priority:
            if role.value in self.roles:
                return role
        return Role.ANONYMOUS

    @property
    def permissions(self) -> set[Permission]:
        """Aggregate permissions from all roles."""
        perms: set[Permission] = set()
        for role_name in self.roles:
            try:
                role = Role(role_name)
                perms |= ROLE_PERMISSIONS.get(role, set())
            except ValueError:
                continue
        return perms


class KeycloakJWKS:
    """Keycloak JWKS key cache for JWT validation."""

    def __init__(self) -> None:
        self._keys: dict[str, Any] = {}
        self._last_refresh: float = 0
        self._refresh_interval: float = 3600  # 1 hour

    async def get_signing_key(self, kid: str) -> dict[str, Any]:
        if not self._keys or (time.time() - self._last_refresh) > self._refresh_interval:
            await self._refresh_keys()
        if kid not in self._keys:
            await self._refresh_keys()
        if kid not in self._keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unknown signing key",
            )
        return self._keys[kid]

    async def _refresh_keys(self) -> None:
        url = (
            f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"
            "/protocol/openid-connect/certs"
        )
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, timeout=10.0)
                resp.raise_for_status()
                data = resp.json()
                self._keys = {key["kid"]: key for key in data.get("keys", [])}
                self._last_refresh = time.time()
            except Exception:
                # In development, fall back to local secret validation
                if not settings.is_production:
                    return
                raise


jwks = KeycloakJWKS()


async def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token."""
    try:
        # First try Keycloak JWKS validation
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        if kid and settings.environment != "development":
            key = await jwks.get_signing_key(kid)
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=settings.keycloak_client_id,
                issuer=f"{settings.keycloak_url}/realms/{settings.keycloak_realm}",
            )
        else:
            # Development: accept HS256 tokens signed with secret_key
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=["HS256"],
            )
        
        return TokenPayload(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> TokenPayload:
    """FastAPI dependency: extract and validate current user from JWT."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return await decode_token(credentials.credentials)


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> TokenPayload | None:
    """FastAPI dependency: optionally extract current user (None if anonymous)."""
    if credentials is None:
        return None
    try:
        return await decode_token(credentials.credentials)
    except HTTPException:
        return None


def require_permission(permission: Permission):
    """FastAPI dependency factory: require a specific permission."""
    async def check_permission(
        user: TokenPayload = Depends(get_current_user),
    ) -> TokenPayload:
        if permission not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} required",
            )
        return user
    return check_permission


def require_role(role: Role):
    """FastAPI dependency factory: require a minimum role."""
    async def check_role(
        user: TokenPayload = Depends(get_current_user),
    ) -> TokenPayload:
        role_priority = list(Role)
        user_idx = role_priority.index(user.highest_role)
        required_idx = role_priority.index(role)
        if user_idx > required_idx:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {role} or higher required",
            )
        return user
    return check_role
