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
    fullName: Optional[str] = Field(default=None, description="Full name (camelCase)")
    full_name: Optional[str] = Field(default=None, description="Full name (snake_case)")
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)


class UpdateProfileRequest(BaseModel):
    fullName: Optional[str] = Field(default=None, description="Display name for the user")
    avatar: Optional[str] = Field(default=None, description="Themed avatar identifier or data")


class UpdateAvatarRequest(BaseModel):
    avatar: str = Field(..., min_length=1, description="Themed avatar identifier or data")


class AuthResponse(BaseModel):
    success: bool = True
    token: str
    user: dict


@router.post("/register")
def register(req: RegisterRequest):
    try:
        resolved_name = (req.fullName or req.full_name or "").strip()
        if not resolved_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter your full name.")
        result = auth_svc.register_user(
            email=req.email,
            password=req.password,
            full_name=resolved_name,
            household_type=None,
        )
        return {
            "success": True,
            "token": result["token"],
            "access_token": result["token"],
            "token_type": "bearer",
            "user": result["user"],
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Register failed: {e}")
        err_text = str(e).strip()
        if "UNIQUE constraint failed" in err_text or "already exists" in err_text.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists.",
            )
        detail_msg = err_text if err_text else "Registration could not be completed. Please check your information and try again."
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail_msg)


@router.post("/login")
def login(req: LoginRequest):
    try:
        result = auth_svc.login_user(email=req.email, password=req.password)
        return {
            "success": True,
            "token": result["token"],
            "access_token": result["token"],
            "token_type": "bearer",
            "user": result["user"],
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed.")


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "user": user,
        "id": user.get("id"),
        "email": user.get("email"),
        "full_name": user.get("fullName") or user.get("full_name"),
    }


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
):
    if credentials and credentials.credentials:
        auth_svc.logout_user(credentials.credentials)
    return {"success": True, "message": "Logged out."}


@router.put("/profile")
def update_profile(
    req: UpdateProfileRequest,
    user: dict = Depends(get_current_user),
):
    """Update authenticated user's profile information (display name, avatar)."""
    user_id = user["id"]
    try:
        updated = auth_svc.update_profile(
            user_id=user_id,
            full_name=req.fullName,
            avatar=req.avatar,
        )
        return {"success": True, "user": updated, "message": "Profile updated successfully."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Profile update failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update profile.",
        )


@router.put("/avatar")
def update_avatar(
    req: UpdateAvatarRequest,
    user: dict = Depends(get_current_user),
):
    """Update authenticated user's avatar selection."""
    user_id = user["id"]
    try:
        updated = auth_svc.update_profile(
            user_id=user_id,
            avatar=req.avatar,
        )
        return {
            "success": True,
            "user": updated,
            "message": "Avatar updated successfully.",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Avatar update failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update avatar.",
        )
