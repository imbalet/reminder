from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext


ALGORITHM = "RS256"

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


def decode_jwt(token: str, public_key: rsa.RSAPublicKey):
    return jwt.decode(token, public_key, algorithms=[ALGORITHM])
