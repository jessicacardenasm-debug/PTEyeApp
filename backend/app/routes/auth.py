from fastapi import APIRouter, HTTPException, status
from app.models.user import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_user
from app.core.security import create_access_token

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    token = create_access_token(
        {"sub": user.email, "name": user.name, "role": user.role}
    )
    return TokenResponse(access_token=token)
