from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Query
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from app.core.security.tokens import create_jwt_token, TokenResponse, TokenType, verify_and_decode_jwt_token
from app.core.config import settings
from app.dependencies import get_db, get_current_user
from app.user.schemas import UserRegister, UserResponse, UpdateUserInfo, GoogleLoginRequest, PaginatedHistoryResponse
from app.user import services
from app.user.models import User
from google.oauth2 import id_token
from google.auth.transport import requests
from decimal import Decimal
from datetime import date as date_type


router = APIRouter(tags=["Users"])


@router.post("/google-login", response_model=TokenResponse)
def google_login(
        response: Response,
        body: GoogleLoginRequest,
        db: Annotated[Session, Depends(get_db)]
):
    try:
        body_ = GoogleLoginRequest.model_dump(body)

        id_info = id_token.verify_oauth2_token(
            body_["token"],
            requests.Request(),
            settings.google_client_id
        )

        email = id_info.get("email")

        if not email:
            raise HTTPException(status_code=400, detail="Google token missing email")

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истекший токен Google"
        )

    user = services.get_user_by_email(db, email)

    if not user:
        user = services.create_oauth_user(db, email=email)

    access_token, _ = create_jwt_token(user.id, token_type=TokenType.ACCESS)
    refresh_token, expiration_at = create_jwt_token(user.id, token_type=TokenType.REFRESH)
    services.save_refresh_token_to_db(db, user.id, refresh_token, expiration_at)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )

    return TokenResponse(access_token=access_token)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister,
             db: Annotated[Session, Depends(get_db)]
) -> dict:
    if services.is_user_exist(db, user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Пользователь с таким email уже существует"
        )
    services.create_user(db, user_data)
    return {"message": "Добро пожаловать! Ваша регистрация прошла успешно"}


@router.post("/login", response_model=TokenResponse)
def login(response: Response,
          form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
          db: Annotated[Session, Depends(get_db)],
):
    try:
        user = services.authenticate_user(db, form_data.username, form_data.password)
    except services.InvalidCredentialsError as er:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(er),
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token, _ = create_jwt_token(user.id, token_type=TokenType.ACCESS)
    refresh_token, expiration_at = create_jwt_token(user.id, token_type=TokenType.REFRESH)
    services.save_refresh_token_to_db(db, user.id, refresh_token, expiration_at)

    response.set_cookie(key="refresh_token",
                        value=refresh_token,
                        httponly=True, samesite="lax",
                        max_age= 7 * 24 * 60 * 60,
                        path="/"
    )
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh_session(
        refresh_token: str = Cookie(None),
        db: Session = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
    payload = verify_and_decode_jwt_token(refresh_token, token_type=TokenType.REFRESH)

    if not services.has_refresh_token(db, refresh_token, int(payload.get("sub"))):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token was not found")

    new_access_token, _ = create_jwt_token(payload.get("sub"), token_type=TokenType.ACCESS)
    return TokenResponse(access_token=new_access_token)


@router.get("/profile", response_model=UserResponse)
def get_user_info(
        cur_user: Annotated[User, Depends(get_current_user)],
):
    return UserResponse(email=cur_user.email, currency=cur_user.currency)


@router.patch("/profile", response_model=UserResponse)
def update_user_info(
        db: Annotated[Session, Depends(get_db)],
        cur_user: Annotated[User, Depends(get_current_user)],
        user_info: UpdateUserInfo,
):
    data = user_info.model_dump(exclude_none=True)

    update_dict = {}
    if "email" in data:
        update_dict["email"] = data["email"]
    if "currency" in data:
        update_dict["currency"] = data["currency"]
    if "new_passwd" in data:
        update_dict["new_passwd"] = data["new_passwd"]
        update_dict["passwd"] = data["passwd"]
    elif "email" in data:
        update_dict["passwd"] = data["passwd"]

    try:
        updated_user = services.update_user(db, cur_user, update_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return UserResponse.model_validate(updated_user)


@router.get("/profile/history", response_model=PaginatedHistoryResponse)
def display_tx(
    db: Annotated[Session, Depends(get_db)],
    cur_user: Annotated[User, Depends(get_current_user)],
    # ── Фильтры ────────────────────────────────────────────────────
    goal: Optional[str] = Query(None, description="Partial match on goal title"),
    date_from: Optional[date_type] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date_type] = Query(None, description="End date (YYYY-MM-DD)"),
    operation_type: Optional[str] = Query(None, description="deposit | withdraw"),
    amount_from: Optional[Decimal] = Query(None, description="Min amount (converted)"),
    amount_to: Optional[Decimal] = Query(None, description="Max amount (converted)"),
    # ── Сортировка ─────────────────────────────────────────────────
    sort_by: str = Query("date", description="date | goal | total | type"),
    sort_dir: str = Query("desc", description="asc | desc"),
    # ── Пагинация ──────────────────────────────────────────────────
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    return services.get_user_history(
        db,
        cur_user,
        goal=goal,
        date_from=date_from,
        date_to=date_to,
        operation_type=operation_type,
        amount_from=amount_from,
        amount_to=amount_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )

