"""
FoodFresh AI — Authentication routes (register, login, logout, me).
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.deps.auth import get_current_user
from backend.app.services import auth_service as auth_svc
from backend.app.deps.auth import _bearer
from fastapi.security import HTTPAuthorizationCredentials

logger = logging.getLogger("foodfresh.routes.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    fullName: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    success: bool = True
    token: str
    user: dict


@router.post("/register")
def register(req: RegisterRequest):
    try:
        result = auth_svc.register_user(
            email=req.email,
            password=req.password,
            full_name=req.fullName,
            household_type=None,
        )
        return {"success": True, "token": result["token"], "user": result["user"]}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Register failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed.")


@router.post("/login")
def login(req: LoginRequest):
    try:
        result = auth_svc.login_user(email=req.email, password=req.password)
        return {"success": True, "token": result["token"], "user": result["user"]}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed.")


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return {"success": True, "user": user}


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
):
    if credentials and credentials.credentials:
        auth_svc.logout_user(credentials.credentials)
    return {"success": True, "message": "Logged out."}
