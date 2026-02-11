import pytest
from datetime import timedelta
from adapters.repository import FakeUserRepository
from domain.types import UserId
from domain.exceptions import (
    AuthentificationError,
    ExpiredSignatureError,
    InvalidTokenError,
)
from dtos import UserDTO, UserType
from service_layer.unit_of_work import FakeUnitOfWork

# Предполагаем, что ваши функции лежат в service_layer/auth.py
from adapters.auth import (
    AuthDTO,
    AuthentificateDTO,
    check_password_by_hash,
    generate_password_hash,
    authentificate,
    generate_token,
    extract_auth_payload_from_token,
    ExtractPayloadFromTokenDTO,
    is_user_type_in,
)


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
    return FakeUnitOfWork(users=FakeUserRepository({UserId(1): user}))


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

    token = generate_token(
        user=user,
        secret_key=auth_config["secret"],
        expiration_time=auth_config["exp"],
        encryption_algorithm=auth_config["algo"],
    )

    extract_dto = ExtractPayloadFromTokenDTO(
        token=token,
        secret_key=auth_config["secret"],
        encryption_algorithm=auth_config["algo"],
    )

    user_id = extract_auth_payload_from_token(extract_dto)
    assert user_id == 99


def test_extract_token_invalid_signature(auth_config):
    user = UserDTO(
        user_id=UserId(1),
        email="a@a.com",
        user_type=UserType.USER,
        password_hash="h",
        full_name="n",
    )

    token = generate_token(
        user, auth_config["secret"], auth_config["exp"], auth_config["algo"]
    )

    # Пытаемся декодировать с другим ключом
    extract_dto = ExtractPayloadFromTokenDTO(
        token=token, secret_key="WRONG_SECRET", encryption_algorithm=auth_config["algo"]
    )

    with pytest.raises(InvalidTokenError):
        extract_auth_payload_from_token(extract_dto)


def test_extract_token_expired(auth_config):
    user = UserDTO(
        user_id=UserId(1),
        email="a@a.com",
        user_type=UserType.USER,
        password_hash="h",
        full_name="n",
    )

    # Создаем токен с отрицательным временем жизни
    token = generate_token(
        user,
        auth_config["secret"],
        expiration_time=timedelta(seconds=-1),
        encryption_algorithm=auth_config["algo"],
    )

    extract_dto = ExtractPayloadFromTokenDTO(
        token=token,
        secret_key=auth_config["secret"],
        encryption_algorithm=auth_config["algo"],
    )

    with pytest.raises(ExpiredSignatureError):
        extract_auth_payload_from_token(extract_dto)


def test_password_hashing():
    password = "my_secret_password"
    hashed = generate_password_hash(password)

    assert hashed != password
    assert check_password_by_hash(password, hashed) is True
    assert check_password_by_hash("wrong", hashed) is False


def test_is_user_type_in_check(uow_with_user):
    repo = uow_with_user.users

    # Юзер с ID 1 имеет тип USER (из фикстуры)
    assert is_user_type_in(UserId(1), [UserType.USER], repo) is True
    assert is_user_type_in(UserId(1), [UserType.ADMIN], repo) is False
