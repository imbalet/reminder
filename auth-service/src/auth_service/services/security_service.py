import base64
import datetime
import json
import os
from pathlib import Path
import secrets
import tempfile

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from auth_service.schemas import KeyPair
from auth_service.config import config


KEY_PAIR_EXPIRES_DAYS = config.KEY_PAIR_EXPIRES_DAYS
ROTATING_BEFORE_EXPIRING_DAYS = config.ROTATING_BEFORE_EXPIRING_DAYS


def int_to_base64url(value: int) -> str:
    byte_length = (value.bit_length() + 7) // 8
    big_endian_bytes = value.to_bytes(byte_length, byteorder="big")
    return base64.urlsafe_b64encode(big_endian_bytes).decode("utf-8").rstrip("=")


class DataStorage:
    def __init__(
        self, current_kid: str, keys: list[KeyPair], expired: list | None = None
    ):
        self.current_kid = current_kid
        self.keys = keys
        self.expired = expired or []

    @property
    def current_key_pair(self):
        keys = list(filter(lambda key: key.kid == self.current_kid, self.keys))
        if len(keys) == 0:
            raise ValueError("Current key pair is not available")
        return keys[0]

    @staticmethod
    def load_public_key_from_path(path: Path) -> rsa.RSAPublicKey:
        if not path.is_file():
            raise FileNotFoundError(f"Public key not found at {path.resolve()}")
        data = path.read_bytes()
        key = serialization.load_pem_public_key(data)
        if not isinstance(key, rsa.RSAPublicKey):

            raise ValueError(f"Public key at {path.resolve()} is not a RSAPrivateKey")
        return key

    @staticmethod
    def load_private_key_from_path(path: Path) -> rsa.RSAPrivateKey:
        if not path.is_file():
            raise FileNotFoundError(f"Private key not found at {path.resolve()}")
        data = path.read_bytes()
        key = serialization.load_pem_private_key(data, password=None)
        if not isinstance(key, rsa.RSAPrivateKey):
            raise ValueError(f"Private key at {path.resolve()} is not a RSAPrivateKey")
        return key

    @staticmethod
    def is_keys_expired(key_pair: KeyPair) -> bool:
        return key_pair.expires_at <= datetime.datetime.now(datetime.UTC)

    @classmethod
    def from_json(cls, path: Path):
        if not path.is_file():
            raise FileNotFoundError(f"Json data file not found at {path.resolve()}")
        try:
            with open(path) as f:
                raw_data = json.load(f)
            current_kid = raw_data["current_kid"]
            if not isinstance(current_kid, str):
                raise ValueError(f"Error on loading json data at {path.resolve()}")

            keys = []
            expired = []
            for key_pair in raw_data["keys"]:
                kid = key_pair["kid"]
                expires_at = datetime.datetime.fromtimestamp(
                    key_pair["expires_at"], tz=datetime.UTC
                )
                private_path = path.parent / key_pair["private_filename"]
                public_path = path.parent / key_pair["public_filename"]

                private_key = cls.load_private_key_from_path(private_path)
                public_key = cls.load_public_key_from_path(public_path)

                key_pair_to_append = KeyPair(
                    kid=kid,
                    expires_at=expires_at,
                    private_key=private_key,
                    public_key=public_key,
                    _private_filename=private_path.name,
                    _public_filename=public_path.name,
                )
                if cls.is_keys_expired(key_pair_to_append):
                    expired.append(key_pair_to_append)
                    continue

                keys.append(key_pair_to_append)
            return cls(current_kid, keys, expired)
        except Exception as e:
            raise ValueError(f"Error on loading json data at {path.resolve()}") from e

    def to_json(self, path: Path):
        data = {
            "current_kid": self.current_key_pair.kid,
            "keys": [
                {
                    "kid": key_pair.kid,
                    "expires_at": key_pair.expires_at.timestamp(),
                    "private_filename": key_pair._private_filename,
                    "public_filename": key_pair._public_filename,
                }
                for key_pair in self.keys
            ],
        }
        temp_file = None
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=path.parent,
                delete=False,
            ) as tmp_file:
                temp_name = tmp_file.name
                json.dump(data, tmp_file, indent=2)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            os.replace(temp_name, path)

        except Exception:
            if temp_file and temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)
            raise


class SecurityService:
    DATA_FILENAME = "data.json"

    def __init__(self, secret_path: Path) -> None:
        self.keys = []
        self.current_key_pair: KeyPair = None  # type: ignore
        self.secret_path = secret_path
        data_file = secret_path / self.DATA_FILENAME

        if not secret_path.is_dir():
            secret_path.mkdir()

        if not data_file.exists():
            self.rotate_keys()
        else:
            try:
                storage = DataStorage.from_json(data_file)
                self._delete_expired_key_files(storage.expired)
                self.keys = storage.keys

                if not self.keys:
                    # logger here
                    self.rotate_keys()
                else:
                    self.current_key_pair = storage.current_key_pair
                    if self._is_keys_expired(self.current_key_pair):
                        # logger here
                        self.rotate_keys()
            except Exception:
                # logger here
                self.rotate_keys()
        if not isinstance(self.current_key_pair, KeyPair):
            raise ValueError("Failed to initialize key pair")

    @staticmethod
    def _generate_keys():
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
            _private_filename=f"{kid}.pem",
            _public_filename=f"{kid}_pub.pem",
        )

    def _save_keys(self, key_pair: KeyPair):
        private_pem = key_pair.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_pem = key_pair.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        with open(self.secret_path / key_pair._private_filename, "wb") as f:
            f.write(private_pem)

        with open(self.secret_path / key_pair._public_filename, "wb") as f:
            f.write(public_pem)

    @staticmethod
    def _is_keys_expired(key_pair: KeyPair) -> bool:
        return key_pair.expires_at <= datetime.datetime.now(datetime.UTC)

    def _delete_expired_key_files(self, expired_keys: list[KeyPair]):
        for key_pair in expired_keys:
            try:
                private_path = self.secret_path / key_pair._private_filename
                public_path = self.secret_path / key_pair._public_filename

                if private_path.exists():
                    private_path.unlink()
                if public_path.exists():
                    public_path.unlink()

            except OSError:
                # logger here
                pass

    def _clean_expired_keys(self):
        now = datetime.datetime.now(datetime.UTC)
        expired_keys = [k for k in self.keys if k.expires_at <= now]
        valid_keys = [k for k in self.keys if k.expires_at > now]
        if not expired_keys:
            return

        self.keys = valid_keys
        self._delete_expired_key_files(expired_keys)

    def _save_data(self):
        storage = DataStorage(self.current_key_pair.kid, self.keys)
        storage.to_json(self.secret_path / self.DATA_FILENAME)

    def rotate_keys(self):
        new_keys = self._generate_keys()
        self._save_keys(new_keys)
        self.keys.append(new_keys)
        self.current_key_pair = new_keys
        self._clean_expired_keys()
        self._save_data()

    def rotate_keys_if_need(self):
        if (
            self.current_key_pair.expires_at - datetime.datetime.now(datetime.UTC)
        ).days <= ROTATING_BEFORE_EXPIRING_DAYS:
            self.rotate_keys()

    def get_last_key_pair(self):
        self.rotate_keys_if_need()
        return self.current_key_pair

    def get_jwks(self) -> dict:
        self.rotate_keys_if_need()
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
