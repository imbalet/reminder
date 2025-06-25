from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext

from src.config import config

from src.schemas.token import (
    GeneratedToken,
    AccesTokenData,
    RefreshTokenData,
)

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if a plain password matches a hashed password

    Args:
        plain_password (str): the plain-text password to verify
        hashed_password (str): the stored password hash for compare

    Returns:
        bool: True if password matches hash, otherwise False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_token(data: dict, expires_delta: timedelta) -> GeneratedToken:
    """Generate a JWT for provided user data

    Args:
        data (dict): user data to encode in the token
        expires_delta (timedelta): time duration for token expiration

    Returns:
        str: generated JWT
        datetime: expiration time
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return GeneratedToken(token=encoded_jwt, expiration_time=expire)


def create_access_token(data: AccesTokenData) -> GeneratedToken:
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return generate_token({"sub": str(data.user_id)}, expires_delta)


def create_refresh_token(data: RefreshTokenData) -> GeneratedToken:
    expires_delta: timedelta = timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    return generate_token(
        {"sub": str(data.user_id), "jti": str(data.jti)}, expires_delta
    )


def decode_jwt(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
