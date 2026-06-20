from fastapi.security import OAuth2PasswordBearer
from app.core.session import SessionLocal
from typing import Annotated
from fastapi import Depends, status, HTTPException
from app.core.security.tokens import verify_and_decode_jwt_token, TokenType
from app.user.services import get_user, User
from sqlalchemy.orm import Session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[Session, Depends(get_db)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_and_decode_jwt_token(token, token_type=TokenType.ACCESS)
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user: User = get_user(db, int(user_id))

    return user
