import datetime
import json
from pathlib import Path
import secrets

import pytest
from pytest_mock import MockerFixture
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from unittest.mock import MagicMock, patch

from auth_service.services.security_service import (
    SecurityService,
    DataStorage,
    ROTATING_BEFORE_EXPIRING_DAYS,
)
from auth_service.services.security_service import int_to_base64url
from auth_service.schemas import KeyPair


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, ""),
        (1, "AQ"),
        (255, "_w"),
        (256, "AQA"),
        (257, "AQE"),
        (63488, "-AA"),
        (64512, "_AA"),
        (123456789, "B1vNFQ"),
        (65535, "__8"),
    ],
)
def test_int_to_base64url(value, expected):
    assert int_to_base64url(value) == expected


def datetime_offset(days: float = 0, hours: float = 0, minutes: float = 0):
    return datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        days=days, hours=hours, minutes=minutes
    )


def create_key_pair(expiring_time: datetime.datetime | None = None):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    kid = secrets.token_urlsafe(8)
    key_pair = KeyPair(
        kid=kid,
        private_key=private_key,
        public_key=private_key.public_key(),
        expires_at=expiring_time or datetime_offset(days=5),
        _private_filename=f"{kid}.pem",
        _public_filename=f"{kid}_pub.pem",
    )
    return key_pair


def write_key_pair(path: Path, expiring_time: datetime.datetime | None = None):
    key_pair = create_key_pair(expiring_time)

    private_pem = key_pair.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = key_pair.public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    kid = secrets.token_urlsafe(8)
    key_pair = KeyPair(
        kid=kid,
        private_key=key_pair.private_key,
        public_key=key_pair.private_key.public_key(),
        expires_at=expiring_time or datetime_offset(days=5),
        _private_filename=f"{kid}.pem",
        _public_filename=f"{kid}_pub.pem",
    )
    (path / key_pair._private_filename).write_bytes(private_pem)
    (path / key_pair._public_filename).write_bytes(public_pem)
    return key_pair


def save_keys(keys: list[KeyPair], path: Path):
    with open(path / SecurityService.DATA_FILENAME, "w") as f:
        json.dump(
            {
                "current_kid": max(keys, key=lambda x: x.expires_at).kid,
                "keys": [
                    {
                        "kid": key_pair.kid,
                        "expires_at": key_pair.expires_at.timestamp(),
                        "private_filename": key_pair._private_filename,
                        "public_filename": key_pair._public_filename,
                    }
                    for key_pair in keys
                ],
            },
            f,
        )


def check_key_pair_equal(key_pair1: KeyPair, key_pair2: KeyPair):
    assert key_pair1.expires_at == key_pair2.expires_at
    assert key_pair1.kid == key_pair2.kid
    assert key_pair1._private_filename == key_pair2._private_filename
    assert key_pair1._public_filename == key_pair2._public_filename

    kp1_private = key_pair1.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    kp2_private = key_pair2.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    kp1_public = key_pair1.public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    kp2_public = key_pair2.public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    assert kp1_private == kp2_private
    assert kp1_public == kp2_public


@pytest.fixture
def keys(tmp_path: Path):
    keys: list[KeyPair] = []
    for _ in range(2):
        key_pair = write_key_pair(tmp_path)
        keys.append(key_pair)
    save_keys(keys, tmp_path)
    return keys


# ------------------------------------#
#           DATA STORAGE              #
# ------------------------------------#


def test_valid_loading_json_ds(keys: list[KeyPair], tmp_path: Path):
    storage = DataStorage.from_json(tmp_path / "data.json")
    assert len(storage.keys) == 2
    check_key_pair_equal(keys[-1], storage.current_key_pair)


def test_loading_with_expired_json_ds(tmp_path: Path):
    keys = [write_key_pair(tmp_path) for _ in range(2)]
    expired_keys = write_key_pair(
        path=tmp_path,
        expiring_time=datetime_offset(days=-1),
    )
    keys.append(expired_keys)
    save_keys(keys, tmp_path)

    storage = DataStorage.from_json(tmp_path / "data.json")
    assert len(storage.keys) == 2
    assert len(storage.expired) == 1
    check_key_pair_equal(storage.expired[0], expired_keys)
    check_key_pair_equal(keys[-2], storage.current_key_pair)


def test_valid_dump_loading_json_ds(keys: list[KeyPair], tmp_path: Path):
    storage = DataStorage.from_json(tmp_path / "data.json")
    (tmp_path / "data.json").unlink()
    storage.to_json(tmp_path / "data.json")
    storage = DataStorage.from_json(tmp_path / "data.json")
    assert len(storage.keys) == 2
    check_key_pair_equal(keys[-1], storage.current_key_pair)


@pytest.mark.parametrize(
    "expires_at, expected",
    [
        (datetime_offset(hours=1), False),
        (datetime_offset(hours=-1), True),
        (datetime_offset(minutes=1), False),
        (datetime_offset(minutes=-1), True),
        (datetime_offset(days=1), False),
        (datetime_offset(days=-1), True),
    ],
)
def test_is_key_expired_ds(expires_at: datetime.datetime, expected: bool):
    key_pair = KeyPair(
        kid="kid",
        public_key="",  # type: ignore
        private_key="",  # type: ignore
        expires_at=expires_at,
        _private_filename="",
        _public_filename="",
    )
    assert DataStorage.is_keys_expired(key_pair) == expected


# ------------------------------------#
#             SERVICE                 #
# ------------------------------------#

"""
test saving
test empty_loading
test is_key_expired
test deleting files
test clean expired

test rotate_key
test rotate_key_if_need
"""


def test_key_loading(tmp_path: Path, keys: list[KeyPair], mocker: MockerFixture):
    mock_rotate = mocker.patch.object(SecurityService, "rotate_keys")
    service = SecurityService(tmp_path)

    assert len(service.keys) == 2
    check_key_pair_equal(keys[-1], service.get_last_key_pair())
    mock_rotate.assert_not_called()


def test_empty_filder_key_loading(tmp_path: Path, mocker: MockerFixture):
    spy = mocker.spy(SecurityService, "rotate_keys")
    service = SecurityService(tmp_path)
    spy.assert_called()
    assert len(service.keys) == 1
    check_key_pair_equal(service.current_key_pair, service.keys[0])


def test_save_keys(tmp_path: Path, mocker: MockerFixture):
    key_pair = create_key_pair()
    mocker.patch.object(SecurityService, "rotate_keys")
    with patch("auth_service.services.security_service.isinstance", return_value=True):
        service = SecurityService(tmp_path)

    storager = DataStorage(key_pair.kid, [key_pair])
    storager.to_json(tmp_path / "data.json")

    service._save_keys(key_pair)
    storager = DataStorage.from_json(tmp_path / "data.json")
    private_path = tmp_path / key_pair._private_filename
    public_path = tmp_path / key_pair._public_filename

    assert private_path.is_file()
    assert public_path.is_file()
    check_key_pair_equal(storager.current_key_pair, key_pair)


@pytest.mark.parametrize(
    "expires_at, expected",
    [
        (datetime_offset(hours=1), False),
        (datetime_offset(hours=-1), True),
        (datetime_offset(minutes=1), False),
        (datetime_offset(minutes=-1), True),
        (datetime_offset(days=1), False),
        (datetime_offset(days=-1), True),
    ],
)
def test_is_key_expired(expires_at: datetime.datetime, expected: bool):
    key_pair = create_key_pair(expiring_time=expires_at)
    assert SecurityService._is_keys_expired(key_pair) == expected


def test_delete_expired_files(tmp_path: Path):
    mock_self = MagicMock(SecurityService)
    mock_self.secret_path = tmp_path

    keys = [write_key_pair(tmp_path, datetime_offset(days=-1)) for _ in range(2)]

    assert any(tmp_path.iterdir())
    SecurityService._delete_expired_key_files(mock_self, keys)

    assert not any(tmp_path.iterdir())


def test_clean_expired_keys(tmp_path):
    mock_self = MagicMock(spec=SecurityService)
    mock_self.secret_path = tmp_path

    expired_keys = [
        write_key_pair(tmp_path, datetime_offset(days=-1)) for _ in range(2)
    ]
    valid_key = write_key_pair(tmp_path, datetime_offset(days=1))

    mock_self.keys = expired_keys + [valid_key]
    mock_self._delete_expired_key_files = MagicMock()

    SecurityService._clean_expired_keys(mock_self)

    mock_self._delete_expired_key_files.assert_called_once()
    args, _ = mock_self._delete_expired_key_files.call_args
    assert len(args[0]) == 2
    assert len(mock_self.keys) == 1
    check_key_pair_equal(mock_self.keys[0], valid_key)


def test_rotate_keys_mocks():
    key_pair = create_key_pair()

    mock_self = MagicMock(spec=SecurityService)
    mock_self.keys = []
    mock_self._generate_keys = MagicMock(return_value=key_pair)
    mock_self._save_keys = MagicMock()
    mock_self._clean_expired_keys = MagicMock()
    mock_self._save_data = MagicMock()

    SecurityService.rotate_keys(mock_self)

    mock_self._save_keys.assert_called_with(key_pair)
    assert len(mock_self.keys) == 1


@pytest.mark.parametrize(
    "expires_at, expected",
    [
        (datetime_offset(days=ROTATING_BEFORE_EXPIRING_DAYS + 2), False),
        (datetime_offset(days=ROTATING_BEFORE_EXPIRING_DAYS + 1, hours=1), False),
        (datetime_offset(days=ROTATING_BEFORE_EXPIRING_DAYS + 1, minutes=1), False),
        (datetime_offset(days=ROTATING_BEFORE_EXPIRING_DAYS + 1), True),
        (datetime_offset(days=ROTATING_BEFORE_EXPIRING_DAYS), True),
        (datetime_offset(days=-1), True),
        (datetime_offset(hours=-1), True),
        (datetime_offset(minutes=-1), True),
    ],
)
def test_rotate_keys_if_need(expires_at, expected: bool):
    key_pair = create_key_pair(expires_at)

    mock_self = MagicMock(spec=SecurityService)
    mock_self.current_key_pair = key_pair
    mock_self.rotate_keys = MagicMock()

    SecurityService.rotate_keys_if_need(mock_self)

    is_called = mock_self.rotate_keys.call_count > 0
    assert is_called == expected
