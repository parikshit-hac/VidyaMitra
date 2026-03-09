from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user_schema import AuthResponse, TokenResponse, UserLogin, UserRead, UserRegister


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def register_user(db: Session, payload: UserRegister) -> AuthResponse:
    try:
        existing = get_user_by_email(db, payload.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = User(
            email=payload.email,
            name=payload.full_name,
            profile_data={"hashed_password": hash_password(payload.password), "is_active": True},
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    token = create_access_token(subject=str(user.id), extra={"email": user.email})
    return AuthResponse(
        user=UserRead(id=user.id, email=user.email or "", full_name=user.name or "", is_active=True),
        token=TokenResponse(access_token=token),
    )


def login_user(db: Session, payload: UserLogin) -> AuthResponse:
    user = get_user_by_email(db, payload.email)
    hashed_password = ((user.profile_data or {}).get("hashed_password") if user else None)
    if not user or not hashed_password or not verify_password(payload.password, hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(subject=str(user.id), extra={"email": user.email})
    is_active = bool((user.profile_data or {}).get("is_active", True))
    return AuthResponse(
        user=UserRead(id=user.id, email=user.email or "", full_name=user.name or "", is_active=is_active),
        token=TokenResponse(access_token=token),
    )
