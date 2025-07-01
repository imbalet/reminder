import datetime
from cryptography.hazmat.primitives.asymmetric import rsa


class KeyPair:
    def __init__(
        self,
        kid: str,
        private_key: rsa.RSAPrivateKey,
        public_key: rsa.RSAPublicKey,
        expires_at: datetime.datetime,
        _private_filename: str,
        _public_filename: str,
    ) -> None:
        self.kid = kid
        self.expires_at = expires_at
        self.private_key = private_key
        self.public_key = public_key
        self._private_filename = _private_filename
        self._public_filename = _public_filename
