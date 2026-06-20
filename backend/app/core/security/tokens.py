import jwt
import datetime
from fastapi import HTTPException
from pydantic import BaseModel
from app.core.config import settings
from enum import Enum


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def create_jwt_token(user_id: int, token_type: TokenType) -> tuple[str, datetime]:
    if token_type == TokenType.ACCESS:
        expiration = (datetime.datetime.now(datetime.UTC) +
                      datetime.timedelta(minutes=settings.jwt_access_token_expire_minutes))
        secret_key = settings.jwt_secret_key
    else:
        expiration = (datetime.datetime.now(datetime.UTC) +
                      datetime.timedelta(days=settings.jwt_refresh_token_expire_days))
        secret_key = settings.jwt_refresh_secret_key
    payload = {"sub": str(user_id), "exp": expiration, "type": token_type}
    return jwt.encode(payload, secret_key, algorithm=settings.jwt_algorithm), expiration


def verify_and_decode_jwt_token(token: str, token_type: TokenType) -> dict:
    if token_type == TokenType.ACCESS:
        secret_key = settings.jwt_secret_key
    else:
        secret_key = settings.jwt_refresh_secret_key
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=[settings.jwt_algorithm])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired!")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token!")

