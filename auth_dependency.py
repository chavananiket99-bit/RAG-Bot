//auth_dependency.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from services.security import decode_access_token

security = HTTPBearer(
    auto_error=False
)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
):
    """
    Validate the JWT bearer token and return
    the authenticated user information.
    """
    # ============================================================
    # CREDENTIAL CHECK
    # ============================================================
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    token = (
        credentials.credentials
        if credentials.credentials
        else ""
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    # ============================================================
    # JWT VALIDATION
    # ============================================================
    try:
        payload = decode_access_token(
            token
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        )

    if not payload or not isinstance(
        payload,
        dict
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        )

    # ============================================================
    # REQUIRED CLAIMS
    # ============================================================
    user_id = payload.get(
        "sub"
    )

    username = payload.get(
        "username"
    )

    if not user_id or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )

    # ============================================================
    # USER OBJECT
    #
    # Keep the existing response structure so the frontend
    # does not need to change.
    # ============================================================
    return {
        "id": str(user_id),
        "username": str(
            username
        ),
        "name": str(
            payload.get(
                "name",
                username
            )
        ),
        "loginType": payload.get(
            "loginType",
            "form"
        ),
    }
