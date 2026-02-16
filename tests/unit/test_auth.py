import pytest
from datetime import timedelta

from accounts.config import AuthConfig
from accounts.core.types import UserId
from accounts.adapters.repository import FakeUserRepository
from accounts.adapters.auth import (
    AuthDTO,
    AuthentificationError,
    ExpiredSignatureError,
    ExtractPayloadFromTokenDTO,
    InvalidTokenError,
    check_password_by_hash,
    generate_password_hash,
    authentificate,
    generate_token,
    extract_auth_payload_from_token,
    is_user_type_in,
)
from accounts.dtos import UserDTO, UserType
from accounts.service_layer.unit_of_work import FakeUnitOfWork


@pytest.fixture
def auth_config():
    return {"secret": "test-secret", "algo": "HS256", "exp": timedelta(minutes=30)}


@pytest.fixture
def uow_with_user():
    user = UserDTO(
        user_id=UserId(1),
        email="test@example.com",
        full_name="Test User",
        user_type=UserType.USER,
        password_hash=generate_password_hash("correct_password"),
    )
    # Инициализируем FakeUnitOfWork с предзаполненным репозиторием
    return FakeUnitOfWork(users=FakeUserRepository({UserId(1): user}, user_serial=1))


def test_authentificate_success(uow_with_user):
    dto = AuthDTO(email="test@example.com", password="correct_password")
    user = authentificate(dto, uow_with_user)

    assert user.email == "test@example.com"
    assert user.user_id == 1


def test_authentificate_fail_wrong_password(uow_with_user):
    dto = AuthDTO(email="test@example.com", password="wrong_password")

    with pytest.raises(AuthentificationError):
        authentificate(dto, uow_with_user)


def test_authentificate_fail_user_not_found(uow_with_user):
    dto = AuthDTO(email="unknown@example.com", password="any_password")

    with pytest.raises(AuthentificationError):
        authentificate(dto, uow_with_user)


def test_generate_and_extract_token_success(auth_config):

    user = UserDTO(
        user_id=UserId(99),
        email="q@q.com",
        user_type=UserType.USER,
        password_hash="hash",
        full_name="Name",
    )

    auth_config = AuthConfig(
        secret_key=auth_config["secret"],
        expiration_time=auth_config["exp"],
        encryption_algorithm=auth_config["algo"],
    )

    token = generate_token(
        user=user,
        config=auth_config,
    )

    extract_dto = ExtractPayloadFromTokenDTO(
        token=token,
    )

    user_id = extract_auth_payload_from_token(
        extract_dto,
        config=auth_config,
    )
    assert user_id == 99


def test_extract_token_invalid_signature(auth_config):
    user = UserDTO(
        user_id=UserId(1),
        email="a@a.com",
        user_type=UserType.USER,
        password_hash="h",
        full_name="n",
    )

    config = AuthConfig(
        auth_config["secret"],
        auth_config["exp"],
        auth_config["algo"],
    )

    token = generate_token(user, config)

    # Пытаемся декодировать с другим ключом
    extract_dto = ExtractPayloadFromTokenDTO(
        token=token,
    )

    config = AuthConfig(
        "other-key",
        auth_config["exp"],
        auth_config["algo"],
    )

    with pytest.raises(InvalidTokenError):
        extract_auth_payload_from_token(extract_dto, config)


def test_extract_token_expired(auth_config):
    user = UserDTO(
        user_id=UserId(1),
        email="a@a.com",
        user_type=UserType.USER,
        password_hash="h",
        full_name="n",
    )

    # Создаем токен с отрицательным временем жизни
    config = AuthConfig(
        secret_key=auth_config["secret"],
        expiration_time=timedelta(seconds=-1),
        encryption_algorithm=auth_config["algo"],
    )
    token = generate_token(
        user,
        config,
    )

    extract_dto = ExtractPayloadFromTokenDTO(
        token=token,
    )

    with pytest.raises(ExpiredSignatureError):
        extract_auth_payload_from_token(extract_dto, config)


def test_password_hashing():
    password = "my_secret_password"
    hashed = generate_password_hash(password)

    assert hashed != password
    assert check_password_by_hash(password, hashed) is True
    assert check_password_by_hash("wrong", hashed) is False


def test_is_user_type_in_check(uow_with_user):
    repo = uow_with_user.users

    assert is_user_type_in(UserId(1), [UserType.USER], repo) is True
    assert is_user_type_in(UserId(1), [UserType.ADMIN], repo) is False
