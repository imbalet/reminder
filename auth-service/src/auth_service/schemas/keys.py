from dataclasses import dataclass
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa


@dataclass
class KeyPair:
    kid: str
    private_key: rsa.RSAPrivateKey
    public_key: rsa.RSAPublicKey
    expires_at: datetime.datetime
    _private_filename: str
    _public_filename: str
