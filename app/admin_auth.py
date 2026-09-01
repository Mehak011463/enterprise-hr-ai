import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext


# =========================================================
# CONFIGURATION
# =========================================================

SECRET_KEY = os.getenv(
    "HR_JWT_SECRET",
    "CHANGE_THIS_SECRET_IN_PRODUCTION"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "HR_TOKEN_EXPIRE_MINUTES",
        "60"
    )
)


# =========================================================
# PASSWORD HASHING
# =========================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =========================================================
# ADMIN CREDENTIALS
# =========================================================

ADMIN_USERNAME = os.getenv(
    "HR_ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD_HASH = os.getenv(
    "HR_ADMIN_PASSWORD_HASH",
    ""
)


# =========================================================
# OAUTH2
# =========================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/admin/login"
)


# =========================================================
# PASSWORD FUNCTIONS
# =========================================================

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def hash_password(password: str) -> str:

    return pwd_context.hash(password)


# =========================================================
# TOKEN CREATION
# =========================================================

def create_access_token(
    username: str,
    role: str = "admin"
):

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# =========================================================
# TOKEN VALIDATION
# =========================================================

def get_current_admin(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        role = payload.get("role")

        if not username or role != "admin":
            raise credentials_exception

        return {
            "username": username,
            "role": role
        }

    except JWTError:

        raise credentials_exception