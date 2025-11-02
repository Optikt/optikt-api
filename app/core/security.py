from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.schemas.access_token import AccessTokenData

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash una contraseña en texto plano"""
    return pwd_context.hash(password)


def create_access_token(
    data: AccessTokenData, expires_delta: Optional[timedelta] = None
) -> str:
    """Crea un token JWT"""
    to_encode = data.model_copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.exp = expire
    return jwt.encode(
        to_encode.model_dump(),
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> Optional[AccessTokenData]:
    """Decodifica y valida un token JWT"""
    try:
        decode_dict = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        return AccessTokenData(**decode_dict)
    except JWTError:
        return None
    except Exception as e:
        print(f"decode_access_token error: {e}")
        return None
