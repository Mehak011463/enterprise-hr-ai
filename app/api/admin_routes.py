from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.admin_auth import (
    ADMIN_USERNAME,
    ADMIN_PASSWORD_HASH,
    verify_password,
    create_access_token,
    get_current_admin,
)

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@router.post("/login")
def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate an HR administrator and return a JWT access token.
    """

    if not ADMIN_PASSWORD_HASH:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin password hash is not configured",
        )

    if form_data.username != ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not verify_password(
        form_data.password,
        ADMIN_PASSWORD_HASH,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(
        username=ADMIN_USERNAME,
        role="admin",
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "admin",
    }


@router.get("/me")
def admin_me(
    current_admin: dict = Depends(get_current_admin),
):
    """
    Return the currently authenticated administrator.
    """

    return {
        "authenticated": True,
        "username": current_admin["username"],
        "role": current_admin["role"],
    }


@router.get("/system-status")
def system_status(
    current_admin: dict = Depends(get_current_admin),
):
    """
    Basic protected system status endpoint.
    """

    return {
        "status": "healthy",
        "service": "enterprise-hr-ai",
        "admin": current_admin["username"],
        "role": current_admin["role"],
    }