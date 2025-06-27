import base64
import datetime
from pathlib import Path
import secrets
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from src.schemas import KeyPair


JWT_ALGORITHM = "RS256"
KEY_PAIR_EXPIRES_DAYS = 15


def int_to_base64url(value: int) -> str:
    byte_length = (value.bit_length() + 7) // 8
    big_endian_bytes = value.to_bytes(byte_length, byteorder="big")
    return base64.urlsafe_b64encode(big_endian_bytes).decode("utf-8").rstrip("=")


class SecurityService:
    def __init__(self, keys: list[KeyPair], secret_path: Path) -> None:
        self.keys = keys
        self.secret_path = secret_path

    @classmethod
    def load_keys(cls, path=".secrets"):
        key_path = Path(path)
        if not key_path.is_dir():
            raise ValueError(f"Secrets directory not found at {key_path.resolve()}")

        keys = []
        for file in key_path.iterdir():
            if file.is_file():
                try:
                    data = file.read_bytes()
                    private_key = serialization.load_pem_private_key(
                        data,
                        password=None,
                    )
                    if not isinstance(private_key, rsa.RSAPrivateKey):
                        continue
                    public_key = private_key.public_key()
                    expires_at = datetime.datetime.fromtimestamp(
                        int(file.name.split("_")[-1]),
                        tz=datetime.timezone.utc,
                    ) + datetime.timedelta(days=KEY_PAIR_EXPIRES_DAYS)
                    keys.append(
                        KeyPair(
                            kid=file.name,
                            expires_at=expires_at,
                            private_key=private_key,
                            public_key=public_key,
                        )
                    )
                except Exception as e:
                    raise ValueError(f"Error reading {file}: {e}") from e
        return cls(keys, key_path)

    def _generate_keys(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        public_key = private_key.public_key()
        iss_time = datetime.datetime.now(datetime.UTC)
        kid = f"{secrets.token_urlsafe(8)}_{int(iss_time.timestamp())}"
        return KeyPair(
            kid=kid,
            expires_at=iss_time + datetime.timedelta(days=KEY_PAIR_EXPIRES_DAYS),
            private_key=private_key,
            public_key=public_key,
        )

    def _save_keys(self, key_pair: KeyPair):
        private_pem = key_pair.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        with open(self.secret_path / key_pair.kid, "wb") as f:
            f.write(private_pem)

    def rotate_keys(self):
        new_keys = self._generate_keys()
        self._save_keys(new_keys)
        self.keys.append(new_keys)

    # TODO: ADD delete_expired

    def get_last_key_pair(self):
        return max(self.keys, key=lambda x: x.expires_at)

    def get_key_pairs(self):
        return self.keys

    def get_jwks(self) -> dict:
        jwks = {"keys": []}
        for key_pair in self.keys:
            public_numbers = key_pair.public_key.public_numbers()
            jwk = {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": key_pair.kid,
                "n": int_to_base64url(public_numbers.n),
                "e": int_to_base64url(public_numbers.e),
            }
            jwks["keys"].append(jwk)
        return jwks
