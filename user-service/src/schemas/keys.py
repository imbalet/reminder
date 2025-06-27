import datetime
from cryptography.hazmat.primitives.asymmetric import rsa


class KeyPair:
    def __init__(
        self,
        kid: str,
        private_key: rsa.RSAPrivateKey,
        public_key: rsa.RSAPublicKey,
        expires_at: datetime.datetime,
    ) -> None:
        self.kid = kid
        self.expires_at = expires_at
        self.private_key = private_key
        self.public_key = public_key
