//routers / auth.py
from fastapi import APIRouter, HTTPException

from models.auth import LoginRequest
from services.auth_service import auth_service
from services.security import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login")
def login(request: LoginRequest):
    user = auth_service.authenticate(username=request.username, password=request.password)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(user)

    return {
        "success": True,
        "user": user,
        "access_token": access_token,
        "token_type": "bearer",
    }
